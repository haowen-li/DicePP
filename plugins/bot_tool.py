import numpy as np

from .dice_tool import RollDiceCommond, SplitDiceCommand, SplitNumberCommand
from .utils import ReadJson, UpdateJson, Command, CommandType, ChineseToEnglishSymbol, TypeValueError
from .utils import commandKeywordList, GetCurrentDateRaw, GetCurrentDate
from .type_assert import TypeAssert
from .custom_config import LOCAL_NICKNAME_PATH, LOCAL_INITINFO_PATH, LOCAL_PCSTATE_PATH, LOCAL_GROUPINFO_PATH, GIFT_LIST

class Bot:
    def __init__(self):
        self.nickNameDict = ReadJson(LOCAL_NICKNAME_PATH)
        self.initInfoDict = ReadJson(LOCAL_INITINFO_PATH)
        self.pcStateDict = ReadJson(LOCAL_PCSTATE_PATH)
        self.groupInfoDict = ReadJson(LOCAL_GROUPINFO_PATH)
    
    # 接受输入字符串，返回输出字符串
    def ProcessInput(self, inputStr, personId, personName, groupId = None, only_to_me = False):
        command = ParseInput(inputStr)
        if command is None:
            return None

        cType = command.cType
        if groupId: # 当时群聊状态时, 检查是否是激活状态
            try:
                assert self.groupInfoDict[groupId]['Active'] == 'True' # 已有记录且是激活状态并继续执行命令
            except:
                try:
                    if (self.groupInfoDict[groupId]['Active'] != 'True') and (cType != CommandType.BOT): # 已有记录且是非激活状态则只执行开关命令
                        return None
                except:
                    self.groupInfoDict[groupId] = {}
                    self.groupInfoDict[groupId]['Active'] = 'True' # 没有记录则新建记录并继续执行命令
                    UpdateJson(self.groupInfoDict, LOCAL_GROUPINFO_PATH)
        
        command.personId = personId
        command.groupId = groupId

        try:
            nickName = self.nickNameDict[personId]
        except:
            nickName = personName
        if cType == CommandType.Roll:
            reason = command.cArg[1]
            if len(reason) != 0:
                reason = f'由于{reason},'
            error, resultStr, resultValList = RollDiceCommond(command.cArg[0])
            if error:
                return resultStr
            finalResult = f'{reason}{nickName}掷出了{resultStr}'
            return finalResult
        elif cType == CommandType.NickName:
            nickName = command.cArg[0]
            result = self.__UpdateNickName(personId, nickName)
            if result == 1:
                return f'要用本来的名字称呼你吗? 了解!'
            elif result == 0:
                return f'要称呼{personName}为{nickName}吗? 没问题!'
        elif cType == CommandType.JRRP:
            date = GetCurrentDateRaw()
            value = self.__GetJRRP(personId, date)
            answer = f'{nickName}今天走运的概率是{value}%'
            if value >= 80:
                answer += ', 今天运气不错哦~'
            elif value <= 20:
                gift = GIFT_LIST[np.random.randint(0,len(GIFT_LIST))]
                answer += f', 今天跑团的时候小心点... 给你{gift}作为防身道具吧~'
            return answer
        elif cType == CommandType.INIT:
            subType = command.cArg[0]
            if not groupId: return '只有在群聊中才能使用该功能哦'
            if not subType:
                initInfo = self.__GetInitList(command.groupId)
                return initInfo
            elif subType == 'clr':
                result = self.__ClearInitList(command.groupId)
                return result
            elif subType[:3] == 'del':
                result =  self.__RemoveInitList(command.groupId, subType[3:].strip())
                return result
        elif cType == CommandType.RI:
            if not groupId: return '只有在群聊中才能使用该功能哦'
            initAdj = command.cArg[0]
            name = command.cArg[1]
            if not name:
                isPC = True
                name = nickName
            else:
                isPC = False
            result = self.__JoinInitList(command.groupId, command.personId, name, initAdj, isPC)
            return result
        elif cType == CommandType.SETHP:
            result = None
            if not command.cArg[0]: # hp为空说明要清除生命值记录
                hp, maxhp = '', ''
            else: # 检查hp 和 maxhp 的有效性
                try:
                    hp = int(command.cArg[0])
                except:
                    return f'{command.cArg[0]}不是有效的生命值'
                try:
                    maxhp = int(command.cArg[1])
                except:
                    return f'{command.cArg[1]}不是有效的生命值'
            result = self.__UpdateHP(personId, hp, maxhp)
            if result == 0:
                return f'{nickName}的生命值是{hp}, 最大生命值是{maxhp}吗? 了解!'
            elif result == 1:
                return f'已经忘记了{nickName}的生命值...'
            elif result == 2:
                return f'{nickName}好像还没有设置过生命值呢...'
            else:
                return f'遇到了未知错误呢...请联系主人吧...#鞠躬'
        elif cType == CommandType.BOT:
            if not groupId: return '只有在群聊中才能使用该功能哦'
            if not only_to_me: return None #'不指定我的话, 这个指令是无效的哦'
            isTurnOn = command.cArg[0]
            result = self.__BotSwitch(groupId, isTurnOn)
            return result
        elif cType == CommandType.DND:
            try:
                times = int(command.cArg[0])
                assert times > 0 and times < 10
            except:
                times = 1
            reason = command.cArg[1]
            result = self.__DNDBuild(groupId, times)
            result = f'{nickName}的初始属性: {reason}\n{result}'
            return result

        return None






    
    def __UpdateNickName(self, personId, nickName) -> int:
        assert personId is not None, '用户名不能为空!'
        if nickName: # 如果指定了昵称, 则更新昵称
            self.nickNameDict[personId] = nickName
            UpdateJson(self.nickNameDict, LOCAL_NICKNAME_PATH)
            return 0
        else: # 否则移除原有的昵称
            try:
                self.nickNameDict.pop(personId)
            except:
                return 1
            UpdateJson(self.nickNameDict, LOCAL_NICKNAME_PATH)
            return 1
        
    def __UpdateHP(self, personId, hp, maxhp) -> int:
        assert personId is not None, '用户名不能为空!'
        result = -1
        if hp:
            try:
                pcState = self.pcStateDict[personId]
                pcState['hp'] = hp
                pcState['maxhp'] = maxhp
            except:
                pcState = {'personId':personId, 'hp':hp, 'maxhp':maxhp}
            self.pcStateDict[personId] = pcState
            result = 0 #修改成功
        else: # 清除生命值记录
            try:
                del self.pcStateDict[personId]
                result = 1 #清除成功
            except:
                result = 2 #清除失败
        
        UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        return result
        
    def __GetJRRP(self, personId, date) -> int:
        seed = 0
        seed += date.year + date.month + date.day
        for c in personId:
            seed += ord(c)
        seed = int(seed)
        np.random.seed(seed)
        value = np.random.randint(0,101)
        return value
    
    def __GetInitList(self, groupId) -> str:
        try: #查找已存在的先攻信息
            initInfo = self.initInfoDict[groupId]
        except: #如未找到, 返回错误信息
            return '还没有做好先攻列表哦'
        
        sortedInfo = sorted(initInfo['initList'].items(), key = lambda i: i[1]['init'], reverse=True)
        result = '先攻列表:'
        for info in sortedInfo:
            # 更新PC生命值
            if info[1]['isPC']:
                try:
                    pcState = self.pcStateDict[personId]
                    info[1]["hp"] = pcState['hp']
                    info[1]["maxhp"] = pcState['maxhp']
                except:
                    pass

            result += f'\n{info[0]} {info[1]["init"]} '
            if info[1]['maxhp'] != 0: result += f'HP:{info[1]["hp"]}/{info[1]["maxhp"]}'
            else: result += f'已损失HP:{info[1]["hp"]}'
        return result
    
    def __ClearInitList(self, groupId) -> str:
        try: #查找已存在的先攻信息
            initInfo = self.initInfoDict[groupId]
            del self.initInfoDict[groupId]
            UpdateJson(self.initInfoDict, LOCAL_INITINFO_PATH)
            return '先攻列表已经删除啦'
        except: #如未找到, 返回错误信息
            return '无法删除不存在的先攻列表哦'

    def __RemoveInitList(self, groupId, name) -> str:
        try: #查找已存在的先攻信息
            initInfo = self.initInfoDict[groupId]
        except: #如未找到, 返回错误信息
            return '还没有做好先攻列表哦'

        if not name in initInfo['initList'].keys():
            possName = []
            for k in initInfo['initList'].keys():
                if k.find(name) != -1:
                    possName.append(k)
            if len(possName) == 0:
                return f'在先攻列表中找不到与"{name}"相关的名字哦'
            elif len(possName) > 1:
                return f'在先攻列表找到多个可能的名字: {[ n for n in possName]}'
            else:
                name = possName[0]

        del initInfo['initList'][name]
        self.initInfoDict[groupId] = initInfo
        UpdateJson(self.initInfoDict, LOCAL_INITINFO_PATH)
        return f'已经将{name}从先攻列表中删除'

    
    def __JoinInitList(self, groupId, personId, name, initAdj, isPC) -> str:
        try: #查找已存在的先攻信息
            initInfo = self.initInfoDict[groupId]
        except: #如未找到, 创建一个新的先攻信息
            initInfo = {'date': GetCurrentDate(), 'initList':{}}
            
        #initAdj 有两种情况, 一是调整值, 二是固定值
        if not initAdj or initAdj[0] in ['+','-'] or initAdj[:2] in ['优势','劣势']: #通过符号判断
            error, resultStr, resultValList = RollDiceCommond('d20'+initAdj)
            if error: return resultStr
            initResult = sum(resultValList)
        else:
            error, resultStr, resultValList = RollDiceCommond(initAdj)
            if error: return resultStr
            initResult = sum(resultValList)
            
        try: #尝试获取生命值信息
            if isPC:
                pcState = self.pcStateDict[personId]
                hp, maxhp = (pcState['hp'], pcState['maxhp'])
            else:
                hp, maxhp = (0, 0)
        except:
            hp, maxhp = (0, 0)
        
        initInfo['initList'][name] = {'id':personId, 'init':initResult, 'hp':hp, 'maxhp':maxhp, 'isPC':isPC}
        self.initInfoDict[groupId] = initInfo
        UpdateJson(self.initInfoDict, LOCAL_INITINFO_PATH)
        
        return f'{name}先攻:{resultStr}'

    def __BotSwitch(self, groupId, activeState) -> str:
        self.groupInfoDict[groupId]['Active'] = activeState
        UpdateJson(self.groupInfoDict, LOCAL_GROUPINFO_PATH)
        if activeState == 'False':
            return '那我就不说话咯'
        else:
            return '来啦~ 让我看看哪个小可爱能得到今日份的礼物'

    @TypeAssert(times = int)
    def __DNDBuild(self, groupId, times) -> str:
        assert times > 0 and times < 10
        
        result = ''
        for i in range(times):
            error, resultStr, resultValList = RollDiceCommond(f'6#4d6k3')
            result += f'力量:{resultValList[0][0]}  体质:{resultValList[1][0]}  敏捷:{resultValList[2][0]}'
            result += f'智力:{resultValList[3][0]}  感知:{resultValList[4][0]}  魅力:{resultValList[5][0]}'
            result += f'  共计:{sum([valList[0] for valList in resultValList])}'
            if i != (times-1) and times != 1:
                result += '\n'
        return result

@TypeAssert(str)
def ParseInput(inputStr):
    # 接受用户的输入, 输出一个数组, 包含指令类型与对应参数
    # 如不是命令则返回None
    inputStr = inputStr.strip()
    # 空字符串直接返回
    if not inputStr:
        return None
    # 先将符号转为英文(半角)
    try:
        inputStr = ChineseToEnglishSymbol(inputStr)
    except TypeValueError:
        print(e)
        raise e
    first_char = inputStr[0]
    # 首字符不是 '.' 说明不是命令
    if first_char != '.':
        return None
    
    # 跳过'.' 并转为小写
    commandStr = inputStr[1:].strip().lower()
    # 判断指令类型, 指令后面跟着参数
    splitIndex = -1
    # 从commandKeywordList中依次匹配命令
    for i in range(len(commandKeywordList)):
        commandKeyword = commandKeywordList[i]
        splitIndex = commandStr.find(commandKeyword)
        if splitIndex == 0:
            commandType = commandStr[:len(commandKeyword)] # 类型
            commandStr = commandStr[len(commandKeyword):].strip() # 参数
            break
    # 无法找到匹配的关键字则直接返回
    if splitIndex != 0:
        return None
    
    # 判断命令类型, 解析参数, 生成Command类的实例并返回
    # 掷骰命令
    if commandType == 'r':
#         # 参数包含两部分, 骰子表达式与原因, 原因为可选项
        diceCommand, reason = SplitDiceCommand(commandStr)
        return Command(CommandType.Roll,[diceCommand, reason])
    # 更改昵称命令
    elif commandType == 'nn':
        nickName = commandStr
        return Command(CommandType.NickName,[nickName])
    # 今日人品命令
    elif commandType == 'jrrp':
        return Command(CommandType.JRRP, [])
    # 先攻列表命令
    elif commandType == 'init':
        # commandStr 可能为 '', 'clr' 
        return Command(CommandType.INIT,[commandStr])
    elif commandType == 'ri':
#         # 参数包含两部分, 骰子表达式(加值)与名称, 名称为可选项
        diceCommand, name = SplitDiceCommand(commandStr)
        return Command(CommandType.RI,[diceCommand, name])
    elif commandType == 'sethp':
        splitIndex = commandStr.strip().find('/')

        if splitIndex != -1:
            hpStr = commandStr[:splitIndex]
            maxhpStr = commandStr[splitIndex+1:]
        else:
            hpStr = commandStr
            maxhpStr = commandStr
        return Command(CommandType.SETHP, [hpStr, maxhpStr])
    elif commandType == 'bot':
        if commandStr.find('on') != -1:
            return Command(CommandType.BOT, ['True'])
        elif commandStr.find('off') != -1:
            return Command(CommandType.BOT, ['False'])
        else:
            return None
    elif commandType == 'dnd':
        number, reason = SplitNumberCommand(commandStr)
        return Command(CommandType.DND,[number, reason])
    return None

