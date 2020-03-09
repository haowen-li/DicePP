import numpy as np
import os
import re
import math

from .dice_tool import RollDiceCommond, SplitDiceCommand, SplitNumberCommand, isDiceCommand
from .type_assert import TypeAssert
from .utils import *
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
    findCommand = False
    # 从commandKeywordList中依次匹配命令
    for i in range(len(commandKeywordList)):
        commandKeyword = commandKeywordList[i]
        splitIndex = commandStr.find(commandKeyword)
        if splitIndex == 0:
            commandType = commandStr[:len(commandKeyword)] # 类型
            commandStr = commandStr[len(commandKeyword):].strip() # 参数
            findCommand = True
            break
    # 无法直接找到匹配的关键字则尝试使用正则表达式判定
    if not findCommand:
        for i in range(len(commandKeywordReList)):
            result = re.match(commandKeywordReList[i], commandStr)
            if result:
                index = result.span(0)[1]
                commandType = commandStr[:index].strip() # 类型
                commandStr = commandStr[index:].strip() # 参数
                findCommand = True
                break
    if not findCommand:
        return None
        
    
    # 判断命令类型, 解析参数, 生成Command类的实例并返回
    # 掷骰命令
    if commandType == 'r':
#         # 参数包含两部分, 骰子表达式与原因, 原因为可选项
        isHide = False
        if commandStr and commandStr[0] == 'h':
            commandStr = commandStr[1:]
            isHide = True
        diceCommand, reason = SplitDiceCommand(commandStr)
        return Command(CommandType.Roll,[diceCommand, reason, isHide])
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
    elif commandType == 'hp':
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
        return Command(CommandType.SETHP, [targetStr, subType, hpStr, maxhpStr])
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
    elif commandType == 'dismiss':
        return Command(CommandType.DISMISS, [])
    elif commandType == 'draw':
        target = commandStr.replace(' ', '')
        return Command(CommandType.DRAW, [target])
    elif commandType == '烹饪':
        diceCommand, keywrods = SplitDiceCommand(commandStr)
        if keywrods == '':
            keywrodList = None
        else:
            keywrodList = [k.strip() for k in keywrods.split('/') if k.strip()]
        return Command(CommandType.COOK, [diceCommand, keywrodList])
    elif commandType == '点菜':
        diceCommand, keywrods = SplitDiceCommand(commandStr)
        if keywrods == '':
            keywrodList = None
        else:
            keywrodList = [k.strip() for k in keywrods.split('/') if k.strip()]
        return Command(CommandType.ORDER, [diceCommand, keywrodList])
    elif commandType == '今日菜单':
        return Command(CommandType.TodayMenu, [])
    elif commandType == '角色卡':
        subType = '查看'
        if commandStr[:2] == '录入':
            subType = '录入'
            commandStr = commandStr[2:]
        elif commandStr[:2] == '删除':
            subType = '删除'
        elif commandStr[:2] == '模板':
            subType = '模板'
        elif commandStr[:4] == '完整查看':
            subType = '完整查看'
        return Command(CommandType.PC, [subType, commandStr])
    elif '检定' in commandType:
        diceCommand, reason = SplitDiceCommand(commandStr)
        return Command(CommandType.CHECK, [commandType[:-2], diceCommand, reason])
    elif '豁免' in commandType:
        diceCommand, reason = SplitDiceCommand(commandStr)
        return Command(CommandType.CHECK, [commandType, diceCommand, reason])

    return None




class Bot:
    def __init__(self):
        self.nickNameDict = ReadJson(LOCAL_NICKNAME_PATH)
        self.initInfoDict = ReadJson(LOCAL_INITINFO_PATH)
        self.pcStateDict = ReadJson(LOCAL_PCSTATE_PATH)
        self.groupInfoDict = ReadJson(LOCAL_GROUPINFO_PATH)
        print(f'个人资料库加载成功!')
        # 尝试加载查询资料库
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
            # self.queryInfoDict['最长条目长度'] = max([len(k) for k in self.queryInfoDict.keys()])
            print(f'查询资料库加载成功! 共{len(self.queryInfoDict)}个条目')
        except: 
            print(f'查询资料库加载失败!')
            self.queryInfoDict = None
        # 尝试加载牌库
        try:
            filesPath = os.listdir(LOCAL_DECKINFO_DIR_PATH) #读取所有文件名
            print(f'找到以下牌堆: {filesPath}')
            self.deckDict = {}
            for fp in filesPath:
                try:
                    assert fp[-5:] == '.json'
                    absPath = os.path.join(LOCAL_DECKINFO_DIR_PATH, fp)
                    print(f'尝试加载{fp}')
                    currentDeckDict = ReadJson(absPath)
                    assert len(currentDeckDict['list']) > 0, f'{fp}是一个空牌堆!'
                    self.deckDict[currentDeckDict['title']] = currentDeckDict['list']
                    print(f'成功加载{fp}, 牌堆名为{currentDeckDict["title"]}, 共{len(currentDeckDict["list"])}个条目')
                except Exception as e:
                    print(e)
            assert len(self.deckDict) > 0
            print(f'牌库加载成功! 共{len(self.deckDict)}个牌堆')
        except Exception as e:
            print(f'牌库加载失败! {e}')
            self.deckDict = None

        # 尝试加载菜谱资料库
        try:
            filesPath = os.listdir(LOCAL_MENUINFO_DIR_PATH) #读取所有文件名
            print(f'找到以下菜谱: {filesPath}')
            self.menuDict = {}
            for fp in filesPath:
                try:
                    assert fp[-5:] == '.json'
                    absPath = os.path.join(LOCAL_MENUINFO_DIR_PATH, fp)
                    print(f'尝试加载{fp}')
                    currentMenuDict = ReadJson(absPath)
                    self.menuDict.update(currentMenuDict)
                    print(f'成功加载{fp}, 共{len(currentMenuDict)}个菜谱')
                except Exception as e:
                    print(e)
            assert len(self.menuDict) > 0
            invalidDish = []
            for dishName in self.menuDict.keys():
                try:
                    dishInfo = self.menuDict[dishName]
                    dishInfo['美味'] = int(dishInfo['美味'])
                    dishInfo['难度'] = int(dishInfo['难度'])
                    assert len(dishName)<50, '名称过长'
                    assert len(dishInfo['描述'])<400, '描述过长'
                    assert dishInfo['美味'] >= -20 and dishInfo['美味'] <= 40, '美味数值不正确'
                    assert dishInfo['难度'] >= -20 and dishInfo['难度'] <= 40, '难度数值不正确'
                    assert len(dishInfo['价格'])<50
                    for key in dishInfo['菜系']:
                        assert key in MENU_CUISINE_LIST, f'{key}不是有效的关键词'
                    for key in dishInfo['种类']:
                        assert key in MENU_TYPE_LIST, f'{key}不是有效的关键词'
                    for key in dishInfo['风格']:
                        assert key in MENU_STYLE_LIST, f'{key}不是有效的关键词'
                    for key in dishInfo['关键词']:
                        assert key in MENU_KEYWORD_LIST, f'{key}不是有效的关键词'
                    self.menuDict[dishName] = dishInfo
                except Exception as e:
                    print (f'菜谱{dishName}无效 {e}')
                    invalidDish.append(dishName)
            for dishName in invalidDish:
                del self.menuDict[dishName]
            print(f'菜谱资料库加载成功! 共{len(self.menuDict)}个菜谱')
        except Exception as e:
            print(f'菜谱资料库加载失败! {e}')
            self.menuDict = None


    # 接受输入字符串，返回输出字符串
    def ProcessInput(self, inputStr, personId, personName, groupId = None, only_to_me = False) -> list:
        command = ParseInput(inputStr)
        if command is None:
            return None

        cType = command.cType
        if groupId: # 当时群聊状态时, 检查是否是激活状态
            try:
                assert self.groupInfoDict[groupId]['Active'] == 'True' # 已有记录且是激活状态并继续执行命令
            except:
                try:
                    if (self.groupInfoDict[groupId]['Active'] != 'True') and (cType != CommandType.BOT) and only_to_me == False: # 已有记录且是非激活状态, 且不是单独指令, 则只执行开关命令
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
            diceCommand = command.cArg[0]
            reason = command.cArg[1]
            isHide = command.cArg[2]
            if len(reason) != 0:
                reason = f'由于{reason},'
            error, resultStr, resultValList = RollDiceCommond(diceCommand)
            finalResult = f'{reason}{nickName}掷出了{resultStr}'
            if error:
                return [CommandResult(CoolqCommandType.MESSAGE, resultStr)]
            if isHide:
                if not groupId: return [CommandResult(CoolqCommandType.MESSAGE, '群聊时才能暗骰哦~')]
                finalResult = f'暗骰结果:{finalResult}'
                return [CommandResult(CoolqCommandType.MESSAGE, finalResult, personIdList = [personId]),
                        CommandResult(CoolqCommandType.MESSAGE, f'{nickName}进行了一次暗骰')]
            else:
                return [CommandResult(CoolqCommandType.MESSAGE, finalResult)]

        elif cType == CommandType.NickName:
            if not groupId: groupId = 'Default'
            nickName = command.cArg[0]
            result = self.__UpdateNickName(groupId, personId, nickName)
            if result == 1:
                return [CommandResult(CoolqCommandType.MESSAGE, f'要用本来的名字称呼你吗? 了解!')]
            elif result == 0:
                return [CommandResult(CoolqCommandType.MESSAGE, f'要称呼{personName}为{nickName}吗? 没问题!')]

        elif cType == CommandType.JRRP:
            date = GetCurrentDateRaw()
            value = self.__GetJRRP(personId, date)
            answer = f'{nickName}今天走运的概率是{value}%'
            if value >= 80:
                answer += ', 今天运气不错哦~'
            elif value <= 20:
                gift = GIFT_LIST[np.random.randint(0,len(GIFT_LIST))]
                answer += f', 今天跑团的时候小心点... 给你{gift}作为防身道具吧~'
            return [CommandResult(CoolqCommandType.MESSAGE, answer)]

        elif cType == CommandType.INIT:
            subType = command.cArg[0]
            if not groupId: return [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            if not subType:
                result = self.__GetInitList(command.groupId)
            elif subType == 'clr':
                result = self.__ClearInitList(command.groupId)
            elif subType[:3] == 'del':
                result =  self.__RemoveInitList(command.groupId, subType[3:].strip())
            else:
                return None
            return [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.RI:
            if not groupId: return [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            initAdj = command.cArg[0]
            name = command.cArg[1]
            if not name:
                isPC = True
                name = nickName
            else:
                isPC = False
            result = self.__JoinInitList(command.groupId, command.personId, name, initAdj, isPC)
            return [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.SETHP:
            if not groupId: return [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            result = None
            # Args: [targetStr, subType , hpStr, maxhpStr]
            if command.cArg[0] is None: # 第一个参数为None说明要清除生命值记录
                self.__ClearHP(groupId, personId)
                return [CommandResult(CoolqCommandType.MESSAGE, f'已经忘记了{nickName}的生命值...')]
            else:
                result = self.__UpdateHP(groupId, personId, *command.cArg, nickName)
                return [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.PC:
            if not groupId: return [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            subType = command.cArg[0]
            infoStr = command.cArg[1]
            if subType == '录入':# 参数为None说明要清除记录
                result = self.__SetPlayerInfo(groupId, personId, infoStr)
            elif subType == '查看':
                result = self.__GetPlayerInfo(groupId, personId, nickName)
            elif subType == '完整查看':
                result = self.__GetPlayerInfoFull(groupId, personId, nickName)
            elif subType == '删除':
                self.__ClearPlayerInfo(groupId, personId)
                result = f'成功删除了{nickName}的角色卡~'
            elif subType == '模板':
                result = pcSheetTemplate
            
            return [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.CHECK:
            if not groupId: return [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            item = command.cArg[0]
            diceCommand = command.cArg[1]
            reason = command.cArg[2]
            error, result = self.__PlayerCheck(groupId, personId, item, diceCommand)
            if error == 0:
                if reason:
                    result = f'由于{reason}, {nickName}{result}'
                else:
                    result = f'{nickName}{result}'
            return [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.BOT:
            if not groupId: return [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            if not only_to_me: return None #'不指定我的话, 这个指令是无效的哦'
            isTurnOn = command.cArg[0]
            result = self.__BotSwitch(groupId, isTurnOn)
            return [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.DND:
            try:
                times = int(command.cArg[0])
                assert times > 0 and times <= 10
            except:
                times = 1
            reason = command.cArg[1]
            result = self.__DNDBuild(groupId, times)
            result = f'{nickName}的初始属性: {reason}\n{result}'
            return [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.HELP:
            subType = str(command.cArg[0])
            helpInfo = self.__GetHelpInfo(subType)
            return [CommandResult(CoolqCommandType.MESSAGE, helpInfo)]

        elif cType == CommandType.QUERY:
            targetStr = str(command.cArg[0])
            queryResult = self.__QueryInfo(targetStr)
            return [CommandResult(CoolqCommandType.MESSAGE, queryResult)]

        elif cType == CommandType.DISMISS:
            if not only_to_me: return None #'不指定我的话, 这个指令是无效的哦'
            return [CommandResult(CoolqCommandType.DISMISS, '再见咯, 期待我们下次的相遇~' ,groupIdList = [groupId])]

        elif cType == CommandType.DRAW:
            targetStr = str(command.cArg[0])
            drawResult = self.__DrawInfo(targetStr)
            return [CommandResult(CoolqCommandType.MESSAGE, drawResult)]

        elif cType == CommandType.COOK:
            if not groupId: return [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            cookAdj = command.cArg[0]
            keywordList = command.cArg[1]
            error, cookResult = self.__CookCheck(cookAdj, keywordList)
            if error == -1:
                return [CommandResult(CoolqCommandType.MESSAGE, cookResult)]
            cookResult = f'{nickName}的烹饪结果是:\n{cookResult}'
            return [CommandResult(CoolqCommandType.MESSAGE, cookResult)]

        elif cType == CommandType.ORDER:
            if not groupId: return [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            number = command.cArg[0]
            keywordList = command.cArg[1]
            error, orderResult = self.__OrderDish(number, keywordList)
            if error == -1:
                return [CommandResult(CoolqCommandType.MESSAGE, orderResult)]
            orderResult = f'{nickName}的菜单:\n{orderResult}'
            return [CommandResult(CoolqCommandType.MESSAGE, orderResult)]

        elif cType == CommandType.TodayMenu:
            date = GetCurrentDateRaw()
            result = self.__GetTodayMenu(personId, date)
            result = f'{nickName}的{result}'
            return [CommandResult(CoolqCommandType.MESSAGE, result)]

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
        if hpStr.find('抗性') != -1 or hpStr.find('易伤') != -1:
            return '抗性与易伤关键字不能出现在此处!'
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
                self.__CreateHP(groupId, personId)
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
                    self.__CreateHP(groupId, targetId)
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
                        if pcState['hp'] > 0 and hp >= pcState['hp']:
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

    def __CreateHP(self, groupId, personId, hp=0, maxhp=0):
        try:
            assert type(self.pcStateDict[groupId]) == dict
        except:
            self.pcStateDict[groupId] = {}
        pcState = {'personId':personId, 'hp':hp, 'maxhp':maxhp, 'alive':True}
        self.pcStateDict[groupId][personId] = pcState
        UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)

    def __ClearHP(self, groupId, personId):
        try:
            self.pcStateDict[groupId][personId]['hp'] = 0
            self.pcStateDict[groupId][personId]['maxhp'] = 0
            UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        except:
            pass

    def __SetPlayerInfo(self, groupId, personId, infoStr) -> str:
        try:
            pcState = self.pcStateDict[groupId][personId]
        except:
            self.__CreateHP(groupId, personId, 0)
            pcState = self.pcStateDict[groupId][personId]

        infoStr = infoStr.strip()
        infoLength = len(infoStr)
        numberStrList = [str(n) for n in range(10)] + [' ']
        pcAbilityList = list(pcAbilityDict.keys())
        for ability in pcAbilityList + ['熟练加值']:
            index = infoStr.find(ability)
            if index == -1:
                return f'无法找到关键词"{ability}", 请查看.角色卡模板'
            # 找到属性值字符串
            index += len(ability) + 1
            lastIndex = index
            for i in range(index, infoLength):
                if infoStr[i] in numberStrList:
                    lastIndex = i+1
                else:
                    break
            abilityVal = infoStr[index:lastIndex].strip()
            try:
                abilityVal = int(abilityVal)
                assert abilityVal >=0 and abilityVal <= 99
                pcState[ability] = abilityVal
                pcState['额外'+ability] = ''
            except:
                return f'关键词"{ability}"对应的属性值"{abilityVal}"无效, 请查看.角色卡模板'

        for ability in pcAbilityList:
            pcState[ability+'调整值'] = math.floor((pcState[ability]-10)/2)

        checkKeywordList = list(pcCheckDictShort.keys())
        for key in checkKeywordList:
            pcState[key] = pcState[pcCheckDictShort[key]]
            pcState['额外'+key] = ''

        index = infoStr.find('熟练项:')
        lastIndex = infoStr[index:].find('\n')
        if index == -1:
            return f'无法找到关键词"熟练项", 请查看.角色卡模板'
        if lastIndex == -1:
            lastIndex = infoLength
        else:
            lastIndex += index
        index += 4

        pcState['熟练项'] = []
        profList = [p.strip() for p in infoStr[index:lastIndex].split('/') if p.strip()]
        
        for profItem in profList:
            if profItem in checkKeywordList:
                pcState[profItem] += pcState['熟练加值']
                pcState['熟练项'].append(profItem)
            else:
                return f'{profItem}不是有效的熟练关键词, 请查看.角色卡模板'

        pcState['额外加值'] = []
        if '额外加值:' in infoStr:
            index = infoStr.find('额外加值:') + 5
            lastIndex = infoStr[index:].find('\n')
            if lastIndex == -1:
                lastIndex = infoLength
            else:
                lastIndex += index
            additionList = [p.strip() for p in infoStr[index:lastIndex].split('/') if p.strip()]
            for additionItem in additionList:
                if '+' in additionItem:
                    index = additionItem.find('+')
                elif '-' in additionItem:
                    index = additionItem.find('-')
                else:
                    return f'额外加值{additionItem}必须包含"+"或"-", 请查看.角色卡模板'
                checkItem = additionItem[:index]
                addStr = additionItem[index:]
                if not isDiceCommand(addStr):
                    return f'额外加值中的{addStr}不是有效的加值, 请查看.角色卡模板'
                if checkItem in checkKeywordList:
                    pcState['额外'+checkItem] += addStr
                elif checkItem == '豁免':  # 如: 豁免+2
                    for saving in pcSavingDict.keys():
                        pcState['额外'+saving] += addStr
                elif checkItem in pcAbilityDict.keys(): # 如: 力量+2
                    pcState['额外'+checkItem] += addStr
                    pcState['额外'+checkItem+'豁免'] += addStr
                    for skill in pcSkillDict.keys():
                        if checkItem in pcSkillDict[skill]:
                            pcState['额外'+skill] += addStr
                else:
                    return f'额外加值中的{checkItem}不是有效的熟练关键词, 请查看.角色卡模板'
                pcState['额外加值'].append(additionItem)

        if 'hp:' in infoStr:
            index = infoStr.find('hp:') + 3
            lastIndex = infoStr[index:].find('\n')
            if lastIndex == -1:
                lastIndex = infoLength
            else:
                lastIndex += index
            hpList = [p.strip() for p in infoStr[index:lastIndex].split('/') if p.strip()]
            try:
                pcState['hp'] = int(hpList[0])
                pcState['maxhp'] = int(hpList[1])
            except:
                return f'{infoStr[index:lastIndex]} 不是有效的生命值信息'

        if '姓名' in infoStr:
            index = infoStr.find('姓名:') + 3
            lastIndex = infoStr[index:].find('\n')
            if lastIndex == -1:
                lastIndex = infoLength
            else:
                lastIndex += index
            nickName = infoStr[index:lastIndex].strip()
            if nickName:
                self.__UpdateNickName(groupId, personId, nickName)

        self.pcStateDict[groupId][personId] = pcState
        UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        return '角色卡录入成功, 查看角色卡请输入.角色卡'

    def __GetPlayerInfo(self, groupId, personId, name)->str:
        try:
            pcState = self.pcStateDict[groupId][personId]
            pcState['熟练加值']
        except:
            return '现在还没有录入角色卡呢~'

        result = f'姓名:{name} '
        if pcState['hp'] != 0 and pcState['maxhp'] != 0:
            result += f'hp:{pcState["hp"]}/{pcState["maxhp"]}\n'

        for ability in pcAbilityDict.keys():
            result += f'{ability}:{pcState[ability]} '
        result = f'{result[:-1]}\n熟练加值:{pcState["熟练加值"]}  熟练项:'
        for profItem in pcState['熟练项']:
            result += f'{profItem}/'
        result = result[:-1]

        if len(pcState['额外加值']) != 0:
            result += '\n额外加值:'
            for additionItem in pcState['额外加值']:
                result += f'{additionItem}/'
            result = result[:-1]
        return result

    def __GetPlayerInfoFull(self, groupId, personId, name)->str:
        try:
            pcState = self.pcStateDict[groupId][personId]
            pcState['熟练加值']
        except:
            return '现在还没有录入角色卡呢~'

        result = f'姓名:{name} '
        if pcState['hp'] != 0 and pcState['maxhp'] != 0:
            result += f'hp:{pcState["hp"]}/{pcState["maxhp"]} '
        result += f'熟练加值:{pcState["熟练加值"]}\n'

        for ability in pcAbilityDict.keys():
            result += f'{ability}:{pcState[ability]} {ability}调整值:{pcState[ability+"调整值"]} '
            result += f'{ability}检定:{pcState[ability+"调整值"]}{pcState["额外"+ability]} {ability}豁免:{pcState[ability+"豁免"]}{pcState["额外"+ability+"豁免"]}\n'
        result += f'技能:\n'
        for skill in pcSkillDict.keys():
            result += f'{skill}:{pcState[skill]}{pcState["额外"+skill]}\n'
        return result
        
    def __PlayerCheck(self, groupId, personId, item, diceCommand) -> (int, str):
        try:
            pcState = self.pcStateDict[groupId][personId]
            pcState['熟练加值']
        except:
            return -1, '请先录入角色卡~'

        if diceCommand.find('抗性') != -1 or diceCommand.find('易伤') != -1:
            return -1, '抗性与易伤关键字不能出现在此处!'
        if not item in pcCheckDictShort.keys():
            if item in pcAbilityDict.keys():
                itemKeyword = item + '调整值'
            else:
                return -1, f'关键字{item}无效~'
        else:
            itemKeyword = item

        #diceCommand 必须为调整值
        if not diceCommand or diceCommand[0] in ['+','-'] or diceCommand[:2] in ['优势','劣势']: #通过符号判断
            if pcState[itemKeyword] != 0:
                completeCommand = 'd20'+diceCommand+int2str(pcState[itemKeyword])+pcState['额外'+item]
            else:
                completeCommand = 'd20'+diceCommand+pcState['额外'+item]
            error, resultStr, resultValList = RollDiceCommond(completeCommand)
            if error: return -1, resultStr
            checkResult = sum(resultValList)
        else:
            return -1, f'输入的指令有点问题呢~'

        result = ''
        if not '豁免' in item: #说明是属性检定
            result += f'在{item}检定中掷出了{resultStr}, '
            if resultValList[0] == 20: result += '大成功!'
            elif resultValList[0] == 1: result += '大失败!'
            elif checkResult >= 30:  result += '"几乎不可能"成功!'
            elif checkResult >= 25:  result += '"非常困难"成功!'
            elif checkResult >= 20:  result += '"困难"成功!'
            elif checkResult >= 15:  result += '"中等"成功!'
            elif checkResult >= 10:  result += '"容易"成功!'
            elif checkResult >= 5:  result += '"非常容易"成功! 也不是很值得骄傲吧...'
            else:  result += '即使是非常容易的事情也失败了呢...'
        else:
            result += f'在{item}中掷出了{resultStr}, '
            if checkResult >= 30:  result += '无论如何都能豁免成功吧~'
            elif checkResult >= 25:  result += '豁免成功几乎是必然的事了~'
            elif checkResult >= 20:  result += '豁免成功的概率很高呢~'
            elif checkResult >= 15:  result += '发挥得还可以嘛~'
            elif checkResult >= 10:  result += '祝你好运!'
            elif checkResult >= 5:  result += '愿海神庇护你...'
            else:  result += '希望你豁免失败的后果不要太惨...'
        return 0, result


    def __ClearPlayerInfo(self, groupId, personId):
        try:
            del self.pcStateDict[groupId][personId]
            UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        except:
            pass

        
    def __GetJRRP(self, personId, date) -> int:
        seed = 0
        temp = 1
        seed += date.year + date.month*13 + date.day*6
        for c in personId:
            seed += ord(c) * temp
            temp += 3
            if temp > 10:
                temp = -4
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

        if initAdj.find('抗性') != -1 or initAdj.find('易伤') != -1:
            return '抗性与易伤关键字不能出现在此处!'
            
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
        name = name.lower()
        initInfo['initList'][name] = {'id':personId, 'init':initResult, 'hp':hp, 'maxhp':maxhp, 'alive':True, 'isPC':isPC}
        self.initInfoDict[groupId] = initInfo
        UpdateJson(self.initInfoDict, LOCAL_INITINFO_PATH)
        
        return f'{name}先攻:{resultStr}'

    #第一个返回值是执行状况, -1为异常, 0为正常
    def __CookCheck(self, cookAdj, keywordList)->(int, str):
        result = ''
        #cookAdj 有两种情况, 一是调整值, 二是固定值
        if not cookAdj or cookAdj[0] in ['+','-'] or cookAdj[:2] in ['优势','劣势']: #通过符号判断
            error, resultStr, resultValList = RollDiceCommond('d20'+cookAdj)
            if error: return -1, resultStr
            cookValue = sum(resultValList)
        else:
            error, resultStr, resultValList = RollDiceCommond(cookAdj)
            if error: return -1, resultStr
            cookValue = sum(resultValList)

        try:
            assert self.menuDict
        except:
            return -1, '菜谱资料库加载失败了呢...'

        possDish = []
        if keywordList:
            if len(keywordList) > 5:
                return -1, f'至多指定5个关键词噢~'
            for key in keywordList:
                if not key in MENU_KEYWORD_LIST:
                    return -1, f'{key}不是有效的关键词, 请查看.help烹饪'
            possDish, delKeyList = self.__FindDishList(keywordList)
            if len(possDish) == 0:
                return -1, f'想不到满足要求的食物呢...'
            if len(delKeyList) != 0:
                result += f'在无视了关键词{delKeyList}后, '
        else:
            possDish = list(self.menuDict.keys())

        SetNumpyRandomSeed()
        dishName = RandomSelectList(possDish)[0]
        result += f'于{len(possDish)}个备选中选择了{dishName}\n'
        dishInfo = self.menuDict[dishName]

        deliValue = 0
        result += f'在检定时掷出了{resultStr} '
        if cookValue >= dishInfo['难度']:
            if cookValue >= dishInfo['难度']+10:
                result += '完美!\n'
                deliValue += 10
            elif cookValue >= dishInfo['难度']+5:
                result += '非常成功\n'
                deliValue += 5
            else:
                result += '比较成功\n'
        else:
            if cookValue <= dishInfo['难度'] - 10:
                result += '大失败!\n'
                if keywordList:
                    possDish, delKeyList = self.__FindDishList(['黑暗']+keywordList)
                else:
                    possDish, delKeyList = self.__FindDishList(['黑暗'])
                dishName = RandomSelectList(possDish)[0]
                dishInfo = self.menuDict[dishName]
                result += f'{RandomSelectList(COOK_FAIL_STR_LIST)[0]} 在原来的基础上略加调整, 制作出了{dishName}\n'
                deliValue -= 10
            elif cookValue <= dishInfo['难度'] - 5:
                result += '非常失败!\n'
                deliValue -= 8
            else:
                result += '比较失败!\n'
                deliValue -= 5
        deliValue += dishInfo['美味']
        result += dishInfo['描述'] + '\n成品会因检定结果有所改变。\n'
        result += f'美味程度:{deliValue}'
        return 0, result

    def __OrderDish(self, numberStr, keywordList)->(int,str):
        result = ''
        number = 1
        if numberStr:
            error, resultStr, resultValList = RollDiceCommond(numberStr)
            if error: return -1, resultStr
            number = sum(resultValList)
            if number < 1:
                return -1, '呃,您要不要点菜呢?'
            if number > 5:
                return -1, '一个人点那么多会浪费的吧, 请将数量控制在5以内哦'
        try:
            assert self.menuDict
        except:
            return -1, '菜谱资料库加载失败了呢...'

        possDish = []
        if keywordList:
            if len(keywordList) > 5:
                return -1, f'至多指定5个关键词噢~'
            for key in keywordList:
                if not key in MENU_KEYWORD_LIST:
                    return -1, f'{key}不是有效的关键词, 请查看.help烹饪'
            possDish, delKeyList = self.__FindDishList(keywordList)
            if len(possDish) == 0:
                return -1, f'想不到满足要求的食物呢...'
            if len(delKeyList) != 0:
                result += f'在无视了关键词{delKeyList}后, '
        else:
            possDish = list(self.menuDict.keys())

        SetNumpyRandomSeed()
        dishNameList = RandomSelectList(possDish, number)
        result += f'于{len(possDish)}个备选中选择了{len(dishNameList)}种食物:\n'
        for dishName in dishNameList:
            dishInfo = self.menuDict[dishName]
            result += f'{dishName} {dishInfo["价格"]}\n{dishInfo["描述"]}\n'
        return 0, result[:-1]

            

    def __FindDishList(self, keywordList) -> (list, list):
        possDish = []
        delKeyList = []
        while len(keywordList) > 0:
            for dishName in self.menuDict.keys():
                isValid = True
                for key in keywordList:
                    if not key in self.menuDict[dishName]['关键词']:
                        isValid = False
                        break
                if isValid:
                    possDish.append(dishName)
            if len(possDish) == 0: # 如果没有找到一个合适的菜肴, 尝试删掉最后一个关键词
                delKeyList.append(keywordList.pop())
            else:
                break # 停止寻找
        return possDish, delKeyList


    def __BotSwitch(self, groupId, activeState) -> str:
        self.groupInfoDict[groupId]['Active'] = activeState
        UpdateJson(self.groupInfoDict, LOCAL_GROUPINFO_PATH)
        if activeState == 'False':
            return '那我就不说话咯~ #潜入水中 (咕嘟咕嘟)'
        else:
            return '伊丽莎白来啦~'

    @TypeAssert(times = int)
    def __DNDBuild(self, groupId, times) -> str:
        assert times > 0 and times < 10
        
        result = ''
        for i in range(times):
            error, resultStr, resultValList = RollDiceCommond(f'6#4d6k3')
            result += f'力量:{resultValList[0][0]}  敏捷:{resultValList[2][0]}  体质:{resultValList[1][0]}  '
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
        elif subType == 'hp':
            return HELP_COMMAND_SETHP_STR
        elif subType == 'jrrp':
            return HELP_COMMAND_JRRP_STR
        elif subType == 'draw':
            return HELP_COMMAND_DRAW_STR
        elif subType == '烹饪':
            return HELP_COMMAND_COOK_STR
        elif subType == '点菜':
            return HELP_COMMAND_ORDER_STR
        elif subType == '今日菜单':
            return HELP_COMMAND_MENU_STR
        elif subType == '角色卡':
            return HELP_COMMAND_PC_STR
        elif subType == '检定':
            return HELP_COMMAND_CHECK_STR
        else:
            return None

    @TypeAssert(targetStr = str)
    def __QueryInfo(self, targetStr) -> str:
        if not self.queryInfoDict:
            return '呃啊, 记忆好像不见了... 怎么办...'
        
        if not targetStr:
            return f'现在的记忆中共有{len(self.queryInfoDict)}个条目呢, 可查询内容请输入 .help查询 查看'

        try:
            result = str(self.queryInfoDict[targetStr])
            return result
        except:
            # 无法直接找到结果, 尝试搜索
            possResult = []
            keywordList = [k for k in targetStr.split('/') if k]
            if len(keywordList) > 5:
                return f'指定的关键词太多咯'

            # 开始逐个搜索
            for k in self.queryInfoDict.keys():
                isPoss = True
                for keyword in keywordList:
                    if k.find(keyword) == -1:
                        isPoss = False
                        break
                if isPoss:
                    possResult.append(k)

            if len(possResult) > 1:
                if len(possResult) <= 30:
                    result = f'找到多个匹配的条目: {possResult}'
                else:
                    result = f'找到多个匹配的条目: {possResult[:30]}等, 共{len(possResult)}个条目'
                return result
            elif len(possResult) == 1:
                result = str(self.queryInfoDict[possResult[0]])
                result = f'要找的是{possResult[0]}吗? \n{result}'
                return result
            else:
                return '唔...找不到呢...'

    @TypeAssert(targetStr = str)
    def __DrawInfo(self, targetStr) -> str:
        if not self.deckDict:
            return '呃啊, 记忆好像不见了... 怎么办...'
        if not targetStr:
            return f'现在的记忆中共有{len(self.deckDict)}个牌堆呢, 分别是{list(self.deckDict.keys())}'

        try:
            deckList = self.deckDict[targetStr]
            size = len(deckList)
            error, resultStr, resultValList = RollDiceCommond(f'd{size}')
            if error: return resultStr
            index = sum(resultValList)-1
            result = f'从{possResult[0]}中抽取的结果: \n{deckList[index]}'
            return result
        except:
            # 无法直接找到结果, 尝试搜索
            possResult = []
            keywordList = [k for k in targetStr.split('/') if k]
            if len(keywordList) > 5:
                return f'指定的关键词太多咯'

            # 开始逐个搜索
            for k in self.deckDict.keys():
                isPoss = True
                for keyword in keywordList:
                    if k.find(keyword) == -1:
                        isPoss = False
                        break
                if isPoss:
                    possResult.append(k)

            if len(possResult) > 1:
                if len(possResult) <= 30:
                    result = f'找到多个匹配的牌堆: {possResult}'
                else:
                    result = f'找到多个匹配的牌堆: {possResult[:30]}等, 共{len(possResult)}个牌堆'
                return result
            elif len(possResult) == 1:
                deckList = self.deckDict[possResult[0]]
                size = len(deckList)
                error, resultStr, resultValList = RollDiceCommond(f'd{size}')
                if error: return resultStr
                index = sum(resultValList)-1
                result = f'从{possResult[0]}中抽取的结果: \n{deckList[index]}'
                return result
            else:
                return '唔...找不到呢...'

    def __GetTodayMenu(self, personId, date) -> str:
        seed = 0
        temp = 1
        seed += date.year + date.month*13 + date.day*6
        for c in personId:
            seed += ord(c) * temp
            temp += 3
            if temp > 10:
                temp = -4
        seed = int(seed)
        np.random.seed(seed)

        try:
            assert self.menuDict
        except:
            return '菜谱资料库加载失败了呢...'

        result = ''
        todayCuisine = RandomSelectList(MENU_CUISINE_LIST)[0]
        todayStyle = RandomSelectList(MENU_STYLE_LIST)[0]
        result += f'今日菜单主题是{todayCuisine}与{todayStyle}噢~\n'

        possDish, delKeyList = self.__FindDishList(['小菜', todayCuisine, todayStyle])
        if len(possDish) != 0 and len(delKeyList) <= 1:
            dishNameList = RandomSelectList(possDish, 1)
            result += f'小菜:'
            for dishName in dishNameList:
                dishInfo = self.menuDict[dishName]
                result += f'{dishName} {dishInfo["价格"]}\n{dishInfo["描述"]}\n'

        possDish, delKeyList = self.__FindDishList(['主菜', todayCuisine, todayStyle])
        if len(possDish) != 0 and len(delKeyList) <= 1:
            dishNameList = RandomSelectList(possDish, 1)
            result += f'主食:'
            for dishName in dishNameList:
                dishInfo = self.menuDict[dishName]
                result += f'{dishName} {dishInfo["价格"]}\n{dishInfo["描述"]}\n'

        possDish, delKeyList = self.__FindDishList(['汤', todayCuisine, todayStyle])
        if len(possDish) != 0 and len(delKeyList) <= 1:
            dishNameList = RandomSelectList(possDish, 1)
            result += f'汤:'
            for dishName in dishNameList:
                dishInfo = self.menuDict[dishName]
                result += f'{dishName} {dishInfo["价格"]}\n{dishInfo["描述"]}\n'

        possDish, delKeyList = self.__FindDishList(['甜品', todayCuisine, todayStyle])
        if len(possDish) != 0 and len(delKeyList) <= 1:
            dishNameList = RandomSelectList(possDish, 1)
            result += f'餐后甜点:'
            for dishName in dishNameList:
                dishInfo = self.menuDict[dishName]
                result += f'{dishName} {dishInfo["价格"]}\n{dishInfo["描述"]}\n'

        possDish, delKeyList = self.__FindDishList(['酒', todayCuisine, todayStyle])
        if len(possDish) != 0 and len(delKeyList) <= 1:
            dishNameList = RandomSelectList(possDish, 1)
            result += f'酒:'
            for dishName in dishNameList:
                dishInfo = self.menuDict[dishName]
                result += f'{dishName} {dishInfo["价格"]}\n{dishInfo["描述"]}\n'

        possDish, delKeyList = self.__FindDishList(['饮料', todayCuisine, todayStyle])
        if len(possDish) != 0 and len(delKeyList) <= 1:
            dishNameList = RandomSelectList(possDish, 1)
            result += f'饮料:'
            for dishName in dishNameList:
                dishInfo = self.menuDict[dishName]
                result += f'{dishName} {dishInfo["价格"]}\n{dishInfo["描述"]}\n'

        return result[:-1]