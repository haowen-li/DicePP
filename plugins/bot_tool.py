import numpy as np
import os

from .dice_tool import RollDiceCommond, SplitDiceCommand, SplitNumberCommand
from .utils import ReadJson, UpdateJson, Command, CommandType, ChineseToEnglishSymbol, TypeValueError
from .utils import commandKeywordList, GetCurrentDateRaw, GetCurrentDate
from .type_assert import TypeAssert
from .custom_config import *
from .help_info import *

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
        subType = None
        targetStr = None
        hpCommand = None
        commandStr = commandStr.strip()
        if len(commandStr) == 0:
            return Command(CommandType.SETHP, [None])
        #是否显式指定了指令类型
        for i in range(len(commandStr)): 
            if commandStr[i] in ['+', '-', '=']:
                subType = commandStr[i]
                targetStr = commandStr[:i].strip()
                hpCommand = commandStr[i+1:].strip()
                break
        #不指定指令类型则默认为'='
        if not subType:
            for i in range(len(commandStr)):
                if commandStr[i] in (['d']+[str(n) for n in range(0,10)]):
                    subType = '='
                    targetStr = commandStr[:i].strip()
                    hpCommand = commandStr[i:].strip()
                    break
        if not subType:
            return None
        splitIndex = hpCommand.rfind('/')
        if splitIndex != -1:
            hpStr = hpCommand[:splitIndex]
            maxhpStr = hpCommand[splitIndex+1:]
        else:
            hpStr = hpCommand
            maxhpStr = ''
        return Command(CommandType.SETHP, [targetStr, subType , hpStr, maxhpStr])
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
    elif commandType == 'help':
        # subType 可能为 '', '指令', '源码', '协议' 
        subType = commandStr.replace(' ', '')
        return Command(CommandType.HELP,[subType])
    elif commandType == '查询':
        target = commandStr.replace(' ', '')
        return Command(CommandType.QUERY,[target])
    return None




class Bot:
    def __init__(self):
        self.nickNameDict = ReadJson(LOCAL_NICKNAME_PATH)
        self.initInfoDict = ReadJson(LOCAL_INITINFO_PATH)
        self.pcStateDict = ReadJson(LOCAL_PCSTATE_PATH)
        self.groupInfoDict = ReadJson(LOCAL_GROUPINFO_PATH)
        print(f'个人资料库加载成功!')
        try:
            filesPath = os.listdir(LOCAL_QUERYINFO_DIR_PATH) #读取所有文件名
            print(f'找到以下查询资料: {filesPath}')
            self.queryInfoDict = {}
            for fp in filesPath:
                try:
                    assert fp[-5:] == '.json'
                    absPath = os.path.join(LOCAL_QUERYINFO_DIR_PATH, fp)
                    print(f'尝试加载{fp}')
                    currentQueryInfoDict = ReadJson(absPath)
                    self.queryInfoDict.update(currentQueryInfoDict)
                    print(f'成功加载{fp}, 共{len(currentQueryInfoDict)}个条目')
                except Exception as e:
                    print(e)
            assert len(self.queryInfoDict) > 0
            self.queryInfoDict['最长条目长度'] = max([len(k) for k in self.queryInfoDict.keys()])
            print(f'查询资料库加载成功! 共{len(self.queryInfoDict)}个条目')
        except: 
            print(f'查询资料库加载失败!')
            self.queryInfoDict = None
    
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
            nickName = self.nickNameDict[groupId][personId]
        except:
            try:
                nickName = self.nickNameDict['Default'][personId]
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
            if not groupId: groupId = 'Default'
            nickName = command.cArg[0]
            result = self.__UpdateNickName(groupId, personId, nickName)
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
            if not groupId: return '只有在群聊中才能使用该功能哦'
            result = None
            # Args: [targetStr, subType , hpStr, maxhpStr]
            if command.cArg[0] is None: # 第一个参数为None说明要清除生命值记录
                result = self.__ClearHP(groupId, personId)
                return f'已经忘记了{nickName}的生命值...'
            else:
                result = self.__UpdateHP(groupId, personId, *command.cArg, nickName)
                return result
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
        elif cType == CommandType.HELP:
            subType = str(command.cArg[0])
            helpInfo = self.__GetHelpInfo(subType)
            return helpInfo
        elif cType == CommandType.QUERY:
            targetStr = str(command.cArg[0])
            queryResult = self.__QueryInfo(targetStr)
            return queryResult

        return None







    
    def __UpdateNickName(self, groupId, personId, nickName) -> int:
        try:
            assert type(self.nickNameDict[groupId]) == dict
        except:
            self.nickNameDict[groupId] = {}

        if nickName: # 如果指定了昵称, 则更新昵称
            self.nickNameDict[groupId][personId] = nickName
            UpdateJson(self.nickNameDict, LOCAL_NICKNAME_PATH)
            return 0
        else: # 否则移除原有的昵称
            try:
                self.nickNameDict[groupId].pop(personId)
            except:
                return 1
            UpdateJson(self.nickNameDict, LOCAL_NICKNAME_PATH)
            return 1
        
    def __UpdateHP(self, groupId, personId, targetStr, subType, hpStr, maxhpStr, nickName) -> str:
        hp = None
        maxhp = None
        if subType != '=' and maxhpStr:
            return '增加或减少生命值的时候不能修改最大生命值哦'
        # 先尝试解读hpStr和maxhpStr
        error, resultStrHp, resultValListHp = RollDiceCommond(hpStr)
        if error: return error
        try:
            hp = sum(resultValListHp)
        except:
            return f'无法解释生命值参数{hpStr}呢...'
        if hp < 0:
            return f'hp数值{resultStrHp}为负数, 没有修改hp数值'

        if maxhpStr:
            try:
                maxhp = int(maxhpStr)
                assert maxhp > 0
            except:
                return f'无法解释最大生命值参数{maxhpStr}呢...'

        if not targetStr: # 不指定目标说明要修改自己的生命值信息
            try:
                pcState = self.pcStateDict[groupId][personId]
            except:
                self.__CreateHP(groupId, personId, 0)
                pcState = self.pcStateDict[groupId][personId]

            if subType == '=':
                pcState['hp'] = hp
                pcState['alive'] = True
                result = f'成功将{nickName}的生命值设置为{resultStrHp}'
                if maxhpStr:
                    pcState['maxhp'] = maxhp
                    result += f', 最大生命值是{maxhp}'
            elif subType == '+':
                pcState['hp'] += hp
                pcState['alive'] = True
                result = f'{nickName}的生命值增加了{resultStrHp}'
            elif subType == '-':
                if pcState['alive']:
                    if pcState['hp'] > 0 and hp > pcState['hp']:
                        pcState['hp'] = 0
                        pcState['alive'] = False
                        result = f'{nickName}的生命值减少了{resultStrHp}\n因为生命值降至0, {nickName}昏迷/死亡了!'
                    else:
                        pcState['hp'] -= hp
                        result = f'{nickName}的生命值减少了{resultStrHp}'
                else:
                    result = f'{nickName}的生命值减少了{resultStrHp}\n{nickName}当前生命值已经是0, 无法再减少了'
            else:
                result = '不太对劲呢...'

            self.pcStateDict[groupId][personId] = pcState
            UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
            return result
        else:
            # 尝试对先攻列中的目标修改生命值信息
            try: #查找已存在的先攻信息
                initInfo = self.initInfoDict[groupId]
            except: #如未找到, 返回错误信息
                return '只能指定在先攻列表中的其他角色, 请先建立先攻列表吧~'

            # 尝试搜索targetStr有关的信息
            if not targetStr in initInfo['initList'].keys(): 
                possName = []
                for k in initInfo['initList'].keys():
                    if k.find(targetStr) != -1:
                        possName.append(k)
                if len(possName) == 0:
                    return f'在先攻列表中找不到与"{targetStr}"相关的名字哦'
                elif len(possName) > 1:
                    return f'在先攻列表找到多个可能的名字: {[ n for n in possName]}'
                else:
                    targetStr = possName[0]

            targetInfo = initInfo['initList'][targetStr]
            # 如果指定的目标是pc, 则直接修改pcStateDict然后返回
            if targetInfo['isPC']:
                targetId = targetInfo['id']
                try:
                    pcState = self.pcStateDict[groupId][targetId]
                except:
                    self.__CreateHP(groupId, targetId, 0)
                    pcState = self.pcStateDict[groupId][targetId]

                if subType == '=':
                    pcState['hp'] = hp
                    pcState['alive'] = True
                    result = f'成功将{targetStr}的生命值设置为{resultStrHp}'
                    if maxhpStr:
                        pcState['maxhp'] = maxhp
                        result += f', 最大生命值是{maxhp}'
                elif subType == '+':
                    pcState['hp'] += hp
                    pcState['alive'] = True
                    result = f'{targetStr}的生命值增加了{resultStrHp}'
                elif subType == '-':
                    if pcState['alive']:
                        if pcState['hp'] > 0 and hp > pcState['hp']:
                            pcState['hp'] = 0
                            pcState['alive'] = False
                            result = f'{targetStr}的生命值减少了{resultStrHp}\n因为生命值降至0, {targetStr}昏迷/死亡了!'
                        else:
                            pcState['hp'] -= hp
                            result = f'{targetStr}的生命值减少了{resultStrHp}'
                    else:
                        result = f'{targetStr}的生命值减少了{resultStrHp}\n{targetStr}当前生命值已经是0, 无法再减少了'
                else:
                    result = '有些不对劲呢...'
                self.pcStateDict[groupId][targetId] = pcState
                UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
                return result
            # 否则修改先攻列表中的信息并保存
            else:
                if subType == '=':
                    targetInfo['hp'] = hp
                    targetInfo['alive'] = True
                    if maxhpStr:
                        targetInfo['maxhp'] = maxhp
                    elif targetInfo['maxhp'] == -1:
                        targetInfo['maxhp'] = 0
                    result = f'成功将{targetStr}的生命值设置为{resultStrHp}'
                    if maxhpStr:
                        result += f', 最大生命值是{maxhp}'
                    return result
                elif subType == '+':
                    targetInfo['hp'] += hp
                    targetInfo['alive'] = True
                    result = f'{targetStr}的生命值增加了{resultStrHp}'
                elif subType == '-':
                    if targetInfo['alive']:
                        if targetInfo['hp'] > 0 and hp > targetInfo['hp']:
                            targetInfo['hp'] = 0
                            targetInfo['alive'] = False
                            result = f'{targetStr}的生命值减少了{resultStrHp}\n因为生命值降至0, {targetStr}昏迷/死亡了!'
                        else:
                            targetInfo['hp'] -= hp
                            result = f'{targetStr}的生命值减少了{resultStrHp}'
                    else:
                        result = f'{targetStr}的生命值减少了{resultStrHp}\n{targetStr}当前生命值已经是0, 无法再减少了'

                else:
                    result = '有些不对劲呢...'
                self.initInfoDict[groupId]['initList'][targetStr] = targetInfo
                UpdateJson(self.initInfoDict, LOCAL_INITINFO_PATH)
                return result

        return '未知的错误发生了'

    def __CreateHP(self, groupId, personId, hp, maxhp=0):
        try:
            assert type(self.pcStateDict[groupId]) == dict
        except:
            self.pcStateDict[groupId] = {}
        pcState = {'personId':personId, 'hp':hp, 'maxhp':maxhp, 'alive':True}
        self.pcStateDict[groupId][personId] = pcState
        UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)

    def __ClearHP(self, groupId, personId) -> str:
        try:
            del self.pcStateDict[groupId][personId]
        except:
            return '好像还没有设置过生命值呢'
        
        UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        return '成功清除生命值信息!'
        
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
        index = 1
        for info in sortedInfo:
            result += f'\n{index}.{info[0]} 先攻{info[1]["init"]} '

            # 获取生命值信息
            if info[1]['isPC']:
                try:
                    personId = info[1]['id']
                    pcState = self.pcStateDict[groupId][personId]
                    hp = pcState['hp']
                    maxhp = pcState['maxhp']
                    alive = pcState['alive']
                except:
                    hp = 0
                    maxhp = 0
                    alive = True
            else:
                hp = info[1]['hp']
                maxhp = info[1]['maxhp']
                alive = info[1]['alive']
            if not alive:
                result += f'昏迷/死亡'
            elif hp > 0 and maxhp > 0:
                result += f'HP:{hp}/{maxhp}'
            elif hp > 0 and maxhp == 0:
                result += f'HP:{hp}'
            elif hp < 0 and maxhp == 0:
                result += f'已损失HP:{-1*hp}'
            index += 1
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
            
        if isPC: # maxhp = 0 或 -1 影响先攻列表的显示与否
            hp, maxhp = (0, 0)
        else:
            hp, maxhp = (0, 0)
        
        initInfo['initList'][name] = {'id':personId, 'init':initResult, 'hp':hp, 'maxhp':maxhp, 'alive':True, 'isPC':isPC}
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

    @TypeAssert(subType = str)
    def __GetHelpInfo(self, subType) -> str:
        if subType == '':
            return HELP_STR
        elif subType == '指令':
            return HELP_COMMAND_STR
        elif subType == '链接':
            return HELP_LINK_STR
        elif subType == '协议':
            return HELP_AGREEMENT_STR
        elif subType == '更新':
            return HELP_COMMAND_UPDATE_STR
        elif subType == 'r':
            return HELP_COMMAND_R_STR
        elif subType == 'nn':
            return HELP_COMMAND_NN_STR
        elif subType == 'ri':
            return HELP_COMMAND_RI_STR
        elif subType == 'init':
            return HELP_COMMAND_INIT_STR
        elif subType == '查询':
            return HELP_COMMAND_QUERY_STR
        elif subType == 'sethp':
            return HELP_COMMAND_SETHP_STR
        elif subType == 'jrrp':
            return HELP_COMMAND_JRRP_STR
        else:
            return None

    @TypeAssert(targetStr = str)
    def __QueryInfo(self, targetStr) -> str:
        if not self.queryInfoDict:
            return '呃啊, 记忆好像不见了... 怎么办...'
        
        if len(targetStr) > self.queryInfoDict['最长条目长度']:
            return '记忆中好像没有这么长的条目呢...'
        elif not targetStr:
            return f'现在的记忆中共有{len(self.queryInfoDict)}个条目呢, 可查询内容请输入 .help查询 查看'

        try:
            result = str(self.queryInfoDict[targetStr])
            return result
        except:
            possResult = []
            for k in self.queryInfoDict.keys():
                if k.find(targetStr) != -1:
                    possResult.append(k)
            if len(possResult) > 1:
                if len(possResult) <= 20:
                    result = f'找到多个匹配的条目: {possResult}'
                else:
                    result = f'找到多个匹配的条目: {possResult[:20]}等, 共{len(possResult)}个条目'
                return result
            elif len(possResult) == 1:
                result = str(self.queryInfoDict[possResult[0]])
                result = f'要找的难道是{possResult[0]}吗? \n{result}'
                return result
            else:
                return '唔...找不到呢...'