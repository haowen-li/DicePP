import numpy as np
import os
import re
import math
import datetime

from .tool_dice import RollDiceCommond, SplitDiceCommand, SplitNumberCommand, isDiceCommand, RollResult
from .type_assert import TypeAssert
from .utils import *
from .custom_config import *
from .help_info import *
from .data_template import *

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
        # 参数包含两部分, 骰子表达式与原因, 原因为可选项
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
        # 参数包含两部分, 骰子表达式(加值)与名称, 名称为可选项
        diceCommand, name = SplitDiceCommand(commandStr)
        return Command(CommandType.RI,[diceCommand, name])
    elif commandType == 'bot':
        if commandStr.find('on') != -1:
            return Command(CommandType.BOT, ['on'])
        elif commandStr.find('off') != -1:
            return Command(CommandType.BOT, ['off'])
        else:
            return Command(CommandType.BOT, ['show'])
    elif commandType == 'dnd':
        number, reason = SplitNumberCommand(commandStr)
        return Command(CommandType.DND,[number, reason])
    elif commandType == 'help':
        # subType 可能为 '', '指令', '源码', '协议' 
        subType = commandStr.replace(' ', '')
        return Command(CommandType.HELP,[subType])
    elif commandType == 'send':
        return Command(CommandType.SEND,[commandStr])
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
    elif commandType == '角色卡' or commandType == '查看角色卡':
        return Command(CommandType.PC, ['查看', commandStr])
    elif commandType == '记录角色卡':
        return Command(CommandType.PC, ['记录', commandStr])
    elif commandType == '角色卡模板' or commandType == '角色卡模版':
        return Command(CommandType.PC, ['模板', commandStr])
    elif commandType == '清除角色卡':
        return Command(CommandType.PC, ['清除', commandStr])
    elif commandType == '完整角色卡':
        return Command(CommandType.PC, ['完整', commandStr])
    elif commandType == '加入队伍':
        return Command(CommandType.TEAM, ['加入', commandStr])
    elif commandType == '队伍信息':
        return Command(CommandType.TEAM, ['查看'])
    elif commandType == '完整队伍信息':
        return Command(CommandType.TEAM, ['完整'])
    elif commandType == '清除队伍':
        return Command(CommandType.TEAM, ['清除'])
    elif commandType == '记录金钱':
        return Command(CommandType.MONEY, ['记录', commandStr])
    elif commandType == '清除金钱':
        return Command(CommandType.MONEY, ['清除'])
    elif commandType == '查看金钱':
        return Command(CommandType.MONEY, ['查看'])
    elif commandType == 'savedata':
        return Command(CommandType.MASTER, ['savedata'])
    elif commandType == 'credit':
        return Command(CommandType.MASTER, ['credit', commandStr])
    elif commandType == '金钱':
        if commandStr == '':
            return Command(CommandType.MONEY, ['查看'])
        else:
            return Command(CommandType.MONEY, ['更改', commandStr])
    elif commandType == '好感度':
        return Command(CommandType.CREDIT, [])
    elif 'hp' in commandType:
        commandStr = commandType[:commandType.find('hp')]+commandStr
        subType = None
        targetStr = None
        hpCommand = None
        commandStr = commandStr.strip()
        if len(commandStr) == 0:
            return Command(CommandType.SHOWHP, [])
        if commandStr == 'clr':
            return Command(CommandType.CLRHP, [])
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
    elif '法术位' in commandType:
        if commandType == '清除法术位':
            return Command(CommandType.SpellSlot, ['清除', commandStr])
        elif commandType == '记录法术位':
            return Command(CommandType.SpellSlot, ['记录', commandStr])
        elif commandType[1:5] == '环法术位':
            level = -1
            try:
                level = int(commandType[0])
            except:
                try:
                    level = ChineseNumberToInt(commandType[0])
                except:
                    return None
            return Command(CommandType.SpellSlot, ['更改', level, commandStr])
        elif commandType == '法术位' or commandType == '查看法术位':
            return Command(CommandType.SpellSlot, ['查看', commandStr])
    elif '环' in commandType:
        level = -1
        try:
            level = int(commandType[0])
            return Command(CommandType.SpellSlot, ['更改', level, commandStr])
        except:
            return None
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
        self.userInfoDict = ReadJson(LOCAL_USERINFO_PATH)
        self.teamInfoDict = ReadJson(LOCAL_TEAMINFO_PATH)
        
        UpdateAllGroupInfo(self.groupInfoDict)
        UpdateAllUserInfo(self.userInfoDict)

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


    def UpdateLocalData(self):
        UpdateJson(self.nickNameDict, LOCAL_NICKNAME_PATH)
        UpdateJson(self.initInfoDict, LOCAL_INITINFO_PATH)
        UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        UpdateJson(self.groupInfoDict, LOCAL_GROUPINFO_PATH)
        UpdateJson(self.userInfoDict, LOCAL_USERINFO_PATH)
        UpdateJson(self.teamInfoDict, LOCAL_TEAMINFO_PATH)

    def DailyUpdate(self):
        for pId in self.userInfoDict.keys():
            userInfoCur = self.userInfoDict[pId]
            userInfoCur['warning'] = 0
            if GetCurrentDateRaw() - Str2Datetime(userInfoCur['commandDate']) <= datetime.timedelta(days = 1):
                userInfoCur['credit'] += 10
        return [CommandResult(CoolqCommandType.MESSAGE, '成功更新今日数据'), MASTER]

    # 接受输入字符串，返回输出字符串
    def ProcessInput(self, inputStr, personId, personName, groupId = None, only_to_me = False) -> list:
        if groupId: # 当是群聊信息时, 检查是否是激活状态
            try:
                assert groupId in self.groupInfoDict.keys()
            except:
                CreateNewGroupInfo(self.groupInfoDict, groupId)

            try:
                assert self.groupInfoDict[groupId]['active'] == True # 已有记录且是激活状态并继续执行命令
            except:
                if self.groupInfoDict[groupId]['active'] == False and only_to_me == False and inputStr.find('bot') == -1: # 已有记录且是非激活状态, 且不是单独指令, 则不执行命令
                    return None

        # 检测命令
        command = ParseInput(inputStr)
        if command is None:
            return None

        # 检查个人信息是否存在
        try:
            assert personId in self.userInfoDict.keys()
        except:
            CreateNewUserInfo(self.userInfoDict, personId)
        userInfoCur = self.userInfoDict[personId]

        # 尝试读取昵称
        try:
            nickName = self.nickNameDict[groupId][personId]
        except:
            try:
                nickName = self.nickNameDict['Default'][personId]
            except:
                nickName = personName



        # 处理命令
        commandResultList = []
        commandWeight = 1
        cType = command.cType
        if cType == CommandType.Roll:
            diceCommand = command.cArg[0]
            reason = command.cArg[1]
            isHide = command.cArg[2]
            if diceCommand == '':
                diceCommand = 'd'
            if len(reason) != 0:
                reason = f'由于{reason},'
            error, resultStr, rollResult = RollDiceCommond(diceCommand)
            finalResult = f'{reason}{nickName}掷出了{resultStr}'
            if error:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, resultStr)]
            else:
                try:
                    if (resultStr[:3] == 'D20' or resultStr[:4] == '1D20'):
                        if resultValList[0] == 20:
                            finalResult += ', 大成功!'
                        elif resultValList[0] == 1:
                            finalResult += ', 大失败!'
                    elif resultStr.find('次D20') != 1 or resultStr.find('次1D20') != 1:
                        succTimes = 0
                        failTimes = 0
                        for resList in resultValList:
                            if resList[0] == 20:
                                succTimes += 1
                            elif resList[0] == 1:
                                failTimes += 1
                        if succTimes != 0:
                            finalResult += f'\n{succTimes}次大成功!'
                        if failTimes != 0:
                            finalResult += f'\n{failTimes}次大失败!'
                except:
                    pass

                if isHide:
                    if not groupId: commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '群聊时才能暗骰哦~')]
                    finalResult = f'暗骰结果:{finalResult}'
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult, personIdList = [personId]),
                            CommandResult(CoolqCommandType.MESSAGE, f'{nickName}进行了一次暗骰')]
                else:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult)]

        elif cType == CommandType.BOT:
            commandWeight = 3
            if not groupId: commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            
            subType = command.cArg[0]
            if subType == 'show':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, SHOW_STR)]
            elif only_to_me:
                if subType == 'on':
                    result = self.__BotSwitch(groupId, True)
                else:
                    result = self.__BotSwitch(groupId, False)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.DISMISS:
            if not only_to_me: return None #'不指定我的话, 这个指令是无效的哦'
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '再见咯~'),
                                  CommandResult(CoolqCommandType.DISMISS,groupIdList = [groupId])]

        elif cType == CommandType.NickName:
            if not groupId: groupId = 'Default'
            newNickName = command.cArg[0]
            result = self.__UpdateNickName(groupId, personId, newNickName)
            if result == 1:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'要用本来的名字称呼你吗? 了解!')]
            elif result == 0:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'要称呼{personName}为{newNickName}吗? 没问题!')]

        elif cType == CommandType.HELP:
            subType = str(command.cArg[0])
            helpInfo = self.__GetHelpInfo(subType)
            if helpInfo:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, helpInfo)]

        elif cType == CommandType.INIT:
            commandWeight = 4
            subType = command.cArg[0]
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                if not subType:
                    result = self.__GetInitList(groupId)
                elif subType == 'clr':
                    result = self.__ClearInitList(groupId)
                elif subType[:3] == 'del':
                    result = self.__RemoveInitList(groupId, subType[3:].strip())
                else:
                    return None
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.RI:
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                initAdj = command.cArg[0]
                name = command.cArg[1]
                if not name:
                    isPC = True
                    name = nickName
                else:
                    isPC = False
                result = self.__JoinInitList(groupId, personId, name, initAdj, isPC)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.SETHP:
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                result = None
                # Args: [targetStr, subType , hpStr, maxhpStr]
                result = self.__UpdateHP(groupId, personId, *command.cArg, nickName)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.SHOWHP:
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                result = self.__ShowHP(groupId, personId)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'{nickName}{result}')]

        elif cType == CommandType.CLRHP:
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                self.__ClearHP(groupId, personId)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'已经忘记了{nickName}的生命值...')]

        elif cType == CommandType.PC:
            commandWeight = 3
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                subType = command.cArg[0]
                infoStr = command.cArg[1]
                if subType == '记录':
                    result = self.__SetPlayerInfo(groupId, personId, infoStr)
                elif subType == '查看':
                    result = self.__GetPlayerInfo(groupId, personId, nickName)
                elif subType == '完整':
                    result = self.__GetPlayerInfoFull(groupId, personId, nickName)
                elif subType == '清除':
                    self.__ClearPlayerInfo(groupId, personId)
                    result = f'成功删除了{nickName}的角色卡~'
                elif subType == '模板':
                    result = pcSheetTemplate
            
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.CHECK:
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                item = command.cArg[0]
                diceCommand = command.cArg[1]
                reason = command.cArg[2]
                error, result = self.__PlayerCheck(groupId, personId, item, diceCommand, nickName)
                if error == 0 and reason:
                        result = f'由于{reason}, {result}'
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.SpellSlot:
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                # Args: [subType, *args]
                subType = command.cArg[0]
                if subType == '记录':
                    error, result = self.__SetSpellSlot(groupId, personId, command.cArg[1])
                elif subType == '查看':
                    result = nickName + self.__ShowSpellSlot(groupId, personId)
                elif subType == '更改':
                    level = command.cArg[1]
                    try:
                        assert command.cArg[2][0] in ['+', '-']
                        adjVal = int(command.cArg[2])
                        assert adjVal > -10 and adjVal < 10
                    except:
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'{command.cArg[2]}是无效的法术位调整值~ 合法范围:[-9, +9]')]
                    result = nickName + self.__ModifySpellSlot(groupId, personId, level, adjVal)
                elif subType == '清除':
                    result = self.__ClearSpellSlot(groupId, personId)

                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.MONEY:
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                subType = command.cArg[0]
                if subType == '记录':
                    error, result = self.__SetMoney(groupId, personId, command.cArg[1])
                    result = result
                elif subType == '清除':
                    result = self.__ClearMoney(groupId, personId)
                elif subType == '更改':
                    result = nickName + self.__ModifyMoney(groupId, personId, command.cArg[1])
                elif subType == '查看':
                    result = nickName + '当前的财富:' +self.__ShowMoney(groupId, personId)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.TEAM:
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                subType = command.cArg[0]
                if subType == '加入':
                    result = self.__JoinTeam(groupId, personId, command.cArg[1])
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '清除':
                    result = self.__ClearTeam(groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '查看':
                    result = self.__ShowTeam(groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '完整':
                    result = self.__ShowTeamFull(groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result, personIdList=[personId]),
                            CommandResult(CoolqCommandType.MESSAGE, '已将队伍的完整信息私聊给你啦~')]

        elif cType == CommandType.SEND:
            commandWeight = 4
            if len(command.cArg[0]) < 10 or len(command.cArg[0])>100:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '请不要随便骚扰Master哦~ (信息长度限制为10~100)')]
            else:
                if groupId:
                    message = f'来自群{groupId} 用户{personId}的信息: {command.cArg[0]}'
                else:
                    message = f'来自用户{personId}的信息: {command.cArg[0]}'
                feedback = '已将信息转发给Master了~'
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, message, personIdList=MASTER),
                        CommandResult(CoolqCommandType.MESSAGE, feedback)]

        elif cType == CommandType.JRRP:
            commandWeight = 2
            date = GetCurrentDateRaw()
            value = self.__GetJRRP(personId, date)
            answer = f'{nickName}今天走运的概率是{value}%'
            if value >= 80:
                answer += ', 今天运气不错哦~'
            elif value <= 20:
                gift = GIFT_LIST[np.random.randint(0,len(GIFT_LIST))]
                answer += f', 今天跑团的时候小心点... 给你{gift}作为防身道具吧~'
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, answer)]

        elif cType == CommandType.DND:
            commandWeight = 3
            try:
                times = int(command.cArg[0])
                assert times > 0 and times <= 10
            except:
                times = 1
            reason = command.cArg[1]
            result = self.__DNDBuild(groupId, times)
            result = f'{nickName}的初始属性: {reason}\n{result}'
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.QUERY:
            commandWeight = 3
            targetStr = str(command.cArg[0])
            queryResult = self.__QueryInfo(targetStr)
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, queryResult)]

        elif cType == CommandType.DRAW:
            commandWeight = 3
            targetStr = str(command.cArg[0])
            drawResult = self.__DrawInfo(targetStr)
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, drawResult)]

        elif cType == CommandType.COOK:
            commandWeight = 4
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                cookAdj = command.cArg[0]
                keywordList = command.cArg[1]
                error, cookResult = self.__CookCheck(cookAdj, keywordList)
                if error == -1:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, cookResult)]
                else:
                    cookResult = f'{nickName}的烹饪结果是:\n{cookResult}'
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, cookResult)]

        elif cType == CommandType.ORDER:
            commandWeight = 4
            if not groupId:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                number = command.cArg[0]
                keywordList = command.cArg[1]
                error, orderResult = self.__OrderDish(number, keywordList)
                if error == -1:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, orderResult)]
                else:
                    orderResult = f'{nickName}的菜单:\n{orderResult}'
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, orderResult)]

        elif cType == CommandType.TodayMenu:
            commandWeight = 4
            date = GetCurrentDateRaw()
            result = self.__GetTodayMenu(personId, date)
            result = f'{nickName}的{result}'
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.CREDIT:
            try:
                credit = userInfoCur['credit']
                result = f'对{nickName}的好感度为{credit}~'
            except:
                result = '啊咧, 遇到一点问题, 请汇报给Master~'
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.MASTER:
            if personId not in MASTER:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有Master才能使用这个命令!')]
            else:
                subType = command.cArg[0]
                if subType == 'savedata':
                    self.UpdateLocalData()
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '成功将所有资料保存到本地咯~')]
                elif subType == 'credit':
                    try:
                        commandArgs = command.cArg[1].split(':')
                        targetId = commandArgs[0].strip()
                        value = int(commandArgs[1])
                        self.userInfoDict[targetId]['credit'] += value
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'{targetId}的好感度{int2str(value)}'),
                                              CommandResult(CoolqCommandType.MESSAGE, f'对你的好感度{int2str(value)}, 现在是{self.userInfoDict[targetId]["credit"]}', personIdList=[targetId])]
                    except Exception as e:
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'好感度调整失败, 原因是:\n{e}')]


        # 最后处理
        if len(commandResultList) > 0:
            userWarning = userInfoCur['warning']
            banTimes = userInfoCur['ban']
                # 黑名单检测
            if userWarning >= 2 or banTimes >= 3:
                return None

            if personId not in MASTER:
                # 刷屏检测
                try:
                    isSpam, dateStr, accuNum = DetectSpam(GetCurrentDateRaw(),
                        userInfoCur['commandDate'], userInfoCur['commandAccu'], commandWeight)
                    userInfoCur['commandDate'] = dateStr
                    userInfoCur['commandAccu'] = accuNum
                    if isSpam:
                        if userWarning == 0:
                            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'检测到{nickName} {personId}的刷屏行为, 黄牌警告!')]
                        elif userWarning == 1:
                            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'检测到{nickName} {personId}的刷屏行为, 不理你了!')]
                            userInfoCur['ban'] += 1
                        userInfoCur['warning'] += 1
                except:
                    pass
            return commandResultList
        else:
            return None





    
    def __UpdateNickName(self, groupId, personId, nickName) -> int:
        try:
            assert type(self.nickNameDict[groupId]) == dict
        except:
            self.nickNameDict[groupId] = {}

        if nickName: # 如果指定了昵称, 则更新昵称
            self.nickNameDict[groupId][personId] = nickName
            # UpdateJson(self.nickNameDict, LOCAL_NICKNAME_PATH)

            # 尝试修改先攻列表
            try:
                initList = self.initInfoDict[groupId]['initList']
                # 如果已有先攻列表有同名角色, 修改所有权
                if nickName in initList.keys():
                    # 先移除可能的原本角色
                    previousName = None
                    for itemName in initList.keys():
                        if initList[itemName]['id'] == personId and initList[itemName]['isPC']:
                            previousName = itemName
                            break
                    if previousName:
                        del initList[previousName]
                    #再修改所有权
                    initList[nickName]['id'] = personId
                    initList[nickName]['isPC'] = True
                else:
                    #在先攻列表中搜索该pc控制的角色
                    previousName = None
                    for itemName in initList.keys():
                        if initList[itemName]['id'] == personId and initList[itemName]['isPC']:
                            previousName = itemName
                            break
                    #如果找到, 就新建一份并且删除原有的记录
                    if previousName:
                        initList[nickName] = initList[previousName]
                        del initList[previousName]
                self.initInfoDict[groupId]['initList'] = initList
                # UpdateJson(self.initInfoDict, LOCAL_INITINFO_PATH)
            except:
                pass

            return 0
        else: # 否则移除原有的昵称
            try:
                del self.nickNameDict[groupId][personId]
            except:
                return 1
            # UpdateJson(self.nickNameDict, LOCAL_NICKNAME_PATH)
            return 1
   
    def __UpdateHP(self, groupId, personId, targetStr, subType, hpStr, maxhpStr, nickName) -> str:
        hp = None
        maxhp = None
        if subType != '=' and maxhpStr:
            return '增加或减少生命值的时候不能修改最大生命值哦'
        # 先尝试解读hpStr和maxhpStr
        # if hpStr.find('抗性') != -1 or hpStr.find('易伤') != -1:
        #     return '抗性与易伤关键字不能出现在此处!'
        error, resultStrHp, rollResult = RollDiceCommond(hpStr)
        if error: return error
        try:
            hp = rollResult.totalValueList[0]
        except Exception as e:
            print(e)
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
                pcState['hp']
            except:
                self.__CreateHP(groupId, personId)
                pcState = self.pcStateDict[groupId][personId]

            pcState, result = ModifyHPInfo(pcState, subType, hp, maxhp, nickName, resultStrHp)

            self.pcStateDict[groupId][personId] = pcState
            # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
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
                    pcState['hp']
                except:
                    self.__CreateHP(groupId, targetId)
                    pcState = self.pcStateDict[groupId][targetId]

                pcState, result = ModifyHPInfo(pcState, subType, hp, maxhp, targetStr, resultStrHp)

                self.pcStateDict[groupId][targetId] = pcState
                # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
                return result
            # 否则修改先攻列表中的信息并保存
            else:
                targetInfo, result = ModifyHPInfo(targetInfo, subType, hp, maxhp, targetStr, resultStrHp)
                self.initInfoDict[groupId]['initList'][targetStr] = targetInfo
                # UpdateJson(self.initInfoDict, LOCAL_INITINFO_PATH)
                return result

        return '未知的错误发生了'

    def __CreateHP(self, groupId, personId, hp=0, maxhp=0):
        try:
            assert type(self.pcStateDict[groupId]) == dict
        except:
            self.pcStateDict[groupId] = {}
        try:
            pcState = self.pcStateDict[groupId][personId]
        except:
            pcState = {}
        pcState.update({'hp':hp, 'maxhp':maxhp, 'alive':True})
        self.pcStateDict[groupId][personId] = pcState
        # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)

    def __ClearHP(self, groupId, personId):
        try:
            self.pcStateDict[groupId][personId]['hp'] = 0
            self.pcStateDict[groupId][personId]['maxhp'] = 0
            # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        except:
            pass

    def __ShowHP(self, groupId, personId) -> str:
        try:
            hp = self.pcStateDict[groupId][personId]['hp']
            maxhp = self.pcStateDict[groupId][personId]['maxhp']
            result = f'当前生命值为{hp}'
            if maxhp != 0:
                result += f'/{maxhp}'
            return result
        except:
            return '还没有设置生命值呢~'

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
        pcState['无调整值'] = 0
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
            if profItem in pcSkillSynonymDict.keys():
                profItem = pcSkillSynonymDict[profItem]

            if profItem in checkKeywordList:
                pcState[profItem] += pcState['熟练加值']
                pcState['熟练项'].append(profItem)
            else:
                return f'{profItem}不是有效的熟练关键词, 请查看.角色卡模板'
        pcState['额外加值'] = []
        # linesep = os.linesep
        linesep = '\n'
        if '额外加值:' in infoStr:
            index = infoStr.find('额外加值:') + 5
            lastIndex = infoStr[index:].find(linesep)
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

                if checkItem in pcSkillSynonymDict.keys():
                    checkItem = pcSkillSynonymDict[checkItem]

                if checkItem in checkKeywordList:
                    pcState['额外'+checkItem] += addStr
                elif checkItem == '豁免':  # 如: 豁免+2
                    for saving in pcSavingDict.keys():
                        pcState['额外'+saving] += addStr
                elif checkItem == '检定':  # 如: 豁免+2
                    for ability in pcAbilityDict.keys():
                        pcState['额外'+ability] += addStr
                    for skill in pcSkillDict.keys():
                        pcState['额外'+skill] += addStr
                # elif checkItem in pcAbilityDict.keys(): # 如: 力量+2
                #     pcState['额外'+checkItem] += addStr
                #     pcState['额外'+checkItem+'豁免'] += addStr
                #     for skill in pcSkillDict.keys():
                #         if checkItem in pcSkillDict[skill]:
                #             pcState['额外'+skill] += addStr
                else:
                    return f'额外加值中的{checkItem}不是有效的熟练关键词, 请查看.角色卡模板'
                pcState['额外加值'].append(additionItem)
        if 'hp:' in infoStr:
            index = infoStr.find('hp:') + 3
            lastIndex = infoStr[index:].find(linesep)
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
            lastIndex = infoStr[index:].find(linesep)
            if lastIndex == -1:
                lastIndex = infoLength
            else:
                lastIndex += index
            nickName = infoStr[index:lastIndex].strip()
            if nickName:
                self.__UpdateNickName(groupId, personId, nickName)

        if '最大法术位' in infoStr:
            index = infoStr.find('最大法术位:') + 6
            lastIndex = infoStr[index:].find(linesep)
            if lastIndex == -1:
                lastIndex = infoLength
            else:
                lastIndex += index
            command = infoStr[index:lastIndex].strip()
            if command:
                error, feedback = self.__SetSpellSlot(groupId, personId, command)
                if error != 0:
                    return feedback

        if '金钱:' in infoStr:
            index = infoStr.find('金钱:') + 3
            lastIndex = infoStr[index:].find(linesep)
            if lastIndex == -1:
                lastIndex = infoLength
            else:
                lastIndex += index
            command = infoStr[index:lastIndex].strip()
            if command:
                error, feedback = self.__SetMoney(groupId, personId, command)
                if error != 0:
                    return feedback

        # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        return '记录角色卡成功, 查看角色卡请输入.角色卡 或.角色卡 完整\n更多相关功能请查询.help检定, .helphp, .help法术位'

    def __GetPlayerInfo(self, groupId, personId, name)->str:
        try:
            pcState = self.pcStateDict[groupId][personId]
            pcState['熟练加值']
        except:
            return f'{name}还没有记录角色卡呢~'

        result = f'姓名:{name}\n'
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

        try:
            maxSlotList = pcState['最大法术位']
            newResult = result + '\n最大法术位:'
            for i in range(9):
                newResult += f'{maxSlotList[i]}/'
            result = newResult[:-1]
        except:
            pass

        try:
            moneyList = pcState['金钱']
            result += f'\n金钱:{moneyList[0]}gp'
            if moneyList[1] != 0:
                result += f' {moneyList[1]}sp'
            if moneyList[2] != 0:
                result += f' {moneyList[2]}sp'
        except:
            pass

        return result

    def __GetPlayerInfoShort(self, groupId, personId, name)->str:
        try:
            pcState = self.pcStateDict[groupId][personId]
            pcState['熟练加值']
        except:
            return f'{name}还没有记录角色卡呢~'

        result = name
        try:
            hp = pcState['hp']
            result += f' hp:{hp}'
        except: pass
        try:
            maxhp = pcState['maxhp']
            result += f'/{maxhp}'
        except: pass
        try:
            moneyList = pcState['金钱']
            result += f' 金钱:{moneyList[0]}gp'
            if moneyList[1] != 0:
                result += f' {moneyList[1]}sp'
            if moneyList[2] != 0:
                result += f' {moneyList[2]}sp'
        except:
            pass
        try:
            currentSlotList = pcState['当前法术位']
            maxSlotList = pcState['最大法术位']
            highestSlot = -1
            for i in range(9):
                if currentSlotList[i] != 0 or maxSlotList[i] != 0:
                    highestSlot = i+1
            assert highestSlot != -1
            result += ' 法术位:'
            for i in range(highestSlot):
                result += f'{currentSlotList[i]}({maxSlotList[i]})/'
            result = result[:-1]
        except: pass
        return result

    def __GetPlayerInfoFull(self, groupId, personId, name)->str:
        try:
            pcState = self.pcStateDict[groupId][personId]
            pcState['熟练加值']
        except:
            return f'{name}还没有记录角色卡呢~'

        result = f'姓名:{name} '
        if pcState['hp'] != 0 and pcState['maxhp'] != 0:
            result += f'hp:{pcState["hp"]}/{pcState["maxhp"]} '
        try:
            moneyList = pcState['金钱']
            result += f'金钱:{moneyList[0]}gp'
            if moneyList[1] != 0:
                result += f' {moneyList[1]}sp'
            if moneyList[2] != 0:
                result += f' {moneyList[2]}sp'
        except:
            pass
        result += f'熟练加值:{pcState["熟练加值"]}\n'

        for ability in pcAbilityDict.keys():
            result += f'{ability}:{pcState[ability]} 调整值:{pcState[ability+"调整值"]} '
            result += f'检定:{pcState[ability+"调整值"]}{pcState["额外"+ability]} 豁免:{pcState[ability+"豁免"]}{pcState["额外"+ability+"豁免"]}\n'
        result += f'技能:\n'
        current = '力量调整值'
        for skill in pcSkillDict.keys():
            if current != pcSkillDict[skill]:
                result += '\n'
                current = pcSkillDict[skill]
            result += f'{skill}:{pcState[skill]}{pcState["额外"+skill]}  '
        result = result[:-2]

        try:
            currentSlotList = pcState['当前法术位']
            maxSlotList = pcState['最大法术位']
            highestSlot = -1
            for i in range(9):
                if currentSlotList[i] != 0 or maxSlotList[i] != 0:
                    highestSlot = i+1
            assert highestSlot != -1
            result += '\n法术位:'
            for i in range(highestSlot):
                result += f'{currentSlotList[i]}({maxSlotList[i]})/'
            result = result[:-1]
        except: pass

        return result
        
    def __PlayerCheck(self, groupId, personId, item, diceCommand, nickName) -> (int, str):
        try:
            pcState = self.pcStateDict[groupId][personId]
            pcState['熟练加值']
        except:
            return -1, '请先记录角色卡~'

        if diceCommand.find('抗性') != -1 or diceCommand.find('易伤') != -1:
            return -1, '抗性与易伤关键字不能出现在此处!'

        if item in pcSkillSynonymDict.keys():
            item = pcSkillSynonymDict[item]

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
            error, resultStr, rollResult = RollDiceCommond(completeCommand)
            if error: return -1, resultStr
            checkResult = rollResult.totalValueList[0]
        else:
            return -1, f'输入的指令有点问题呢~'

        result = ''
        if not '豁免' in item: #说明是属性检定
            result += f'{nickName}在{item}检定中掷出了{resultStr}'
            if rollResult.rawResultList[0][0] == 20: result += ' 大成功!'
            elif rollResult.rawResultList[0][0] == 1: result += ' 大失败!'
        else:
            result += f'{nickName}在{item}中掷出了{resultStr}'
            if rollResult.rawResultList[0][0] == 20: result += ' 大成功!'
            elif rollResult.rawResultList[0][0] == 1: result += ' 大失败!'

        if item == '先攻':
            self.__JoinInitList(groupId, personId, nickName, '0'+int2str(checkResult), isPC=True)
            result += f'\n已将{nickName}加入先攻列表'
        return 0, result

    def __ClearPlayerInfo(self, groupId, personId):
        try:
            del self.pcStateDict[groupId][personId]
            # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        except:
            pass

    def __SetSpellSlot(self, groupId, personId, commandStr) -> (int, str):
        # commandStr示例: 4/2/0/0/0/0
        maxSpellSlotList = [0]*9
        sizeStrList = commandStr.split('/')
        isValid = False
        index = 0
        if len(sizeStrList)>9:
            return -1, '唔...法术环位好像最高只有九环呢...'
        for sizeStr in sizeStrList:
            try:
                size = int(sizeStr)
                maxSpellSlotList[index] = size
                assert size >=0 and size < 100
                if size > 0:
                    isValid = True
            except:
                return -1, f'{index+1}环法术位大小{sizeStr}无效~'
            index += 1

        try:
            pcState = self.pcStateDict[groupId][personId]
        except:
            pcState = {}
        if isValid:
            pcState['最大法术位'] = maxSpellSlotList
            pcState['当前法术位'] = maxSpellSlotList.copy()
            self.pcStateDict[groupId][personId] = pcState
            # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
            return 0, '法术环位已经记录好了~'
        else:
            return -1, '不会施法就请不要记录法术位咯~'

    def __ClearSpellSlot(self, groupId, personId) -> str:
        try:
            del self.pcStateDict[groupId][personId]['最大法术位']
            del self.pcStateDict[groupId][personId]['当前法术位']
            # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        except:
            pass
        return '已经将法术位信息忘记啦~'

    def __ShowSpellSlot(self, groupId, personId) -> str:
        try:
            maxSlotList = self.pcStateDict[groupId][personId]['最大法术位']
            currentSlotList = self.pcStateDict[groupId][personId]['当前法术位']
        except:
            return '还没有施法能力哦, 请先使用 .记录法术位 命令吧~'
        result = '当前法术位'
        index = 1
        for maxSize in maxSlotList:
            if maxSize != 0:
                result += f'\n{index}环法术位:{currentSlotList[index-1]}/{maxSize}'
            index += 1
        return result

    def __ModifySpellSlot(self, groupId, personId, level, adjVal):
        # level in [1, 9]
        # adjVal in [-9, 9]
        try:
            currentSlotList = self.pcStateDict[groupId][personId]['当前法术位']
        except:
            print('没有检测到相关信息, 请先使用 .记录法术位 命令吧~')
        preSlot = currentSlotList[level-1]
        if preSlot + adjVal < 0:
            return '没有这么多法术位了...'
        currentSlotList[level-1] += adjVal
        self.pcStateDict[groupId][personId]['当前法术位'] = currentSlotList
        # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        if adjVal < 0:
            return f'{level}环法术位减少了{-1*adjVal}个 ({preSlot}->{preSlot+adjVal})'
        else:
            return f'{level}环法术位增加了{adjVal}个 ({preSlot}->{preSlot+adjVal})'

    def __SetMoney(self, groupId, personId, commandStr) -> (int, str):
        error, reason, moneyList = Str2MoneyList(commandStr)
        if error != 0:
            return -1, reason
        try:
            pcState = self.pcStateDict[groupId][personId]
        except:
            pcState = {}
        pcState['金钱'] = moneyList
        self.pcStateDict[groupId][personId] = pcState
        # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        return 0, '牢牢记住你的财富咯~'

    def __ShowMoney(self, groupId, personId):
        try:
            moneyList = self.pcStateDict[groupId][personId]['金钱']
        except:
            return '现在身无分文呢~ 请先使用 .记录金钱 命令吧~'
        result = f'{moneyList[0]}gp'
        if moneyList[1] != 0:
            result += f' {moneyList[1]}sp'
        if moneyList[2] != 0:
            result += f' {moneyList[2]}cp'
        return result

    def __ClearMoney(self, groupId, personId):
        try:
            del self.pcStateDict[groupId][personId]['金钱']
            # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        except:
            pass
        return '已经将你的财富忘记啦~'

    def __ModifyMoney(self, groupId, personId, commandStr):
        try:
            moneyList = self.pcStateDict[groupId][personId]['金钱'].copy()
        except:
            return '现在身无分文呢~ 请先使用 .记录金钱 命令吧~'
        error, reason, adjList = Str2MoneyList(commandStr)
        if error != 0:
            return reason
        totalVal = moneyList[0]*100 + moneyList[1]*10+ moneyList[0]
        adjVal = adjList[0]*100 + adjList[1]*10+ adjList[0]
        if totalVal + adjVal < 0:
            return '余额不足, 请及时充值~'
        # 当前的铜币不足以支付要求的铜币, 则用银币或金币换取
        if moneyList[2] + adjList[2] < 0:
            # 加上银币
            if adjList[2]+moneyList[2]+moneyList[1]*10 < 0:
                # 依然不够则加上金币
                gpNum = math.ceil((adjList[2]+moneyList[2]+moneyList[1]*10)/-100)
                moneyList[2] = adjList[2]+moneyList[2]+moneyList[1]*10+gpNum*100
                moneyList[1] = 0
                moneyList[0] -= gpNum
            else:
                #换取部分银币
                spNum = math.ceil((adjList[2]+moneyList[2])/-10)
                moneyList[2] = adjList[2]+moneyList[2]+spNum*10
                moneyList[1] -= spNum
        else:
            moneyList[2] = adjList[2]+moneyList[2]

        # 当前的银币不足以支付要求的银币, 则用铜币或金币换取
        if moneyList[1] + adjList[1] < 0:
            # 加上铜币
            if adjList[1]+moneyList[1]+moneyList[2]//10 < 0:
                # 再加上金币
                gpNum = math.ceil((adjList[1]+moneyList[1]+moneyList[2]//10)/-10)
                moneyList[1] = adjList[1]+moneyList[1]+moneyList[2]//10+gpNum*10
                moneyList[2] -= moneyList[2]//10
                moneyList[0] -= gpNum
            else:
                #换取部分铜币支付
                cpNum = (adjList[1]+moneyList[1])*-10
                moneyList[1] = 0
                moneyList[2] -= cpNum
        else:
            moneyList[1] = adjList[1]+moneyList[1]

        # 当前的金币不足以支付要求的金币, 则用银币或铜币换取
        if moneyList[0] + adjList[0] < 0:
            # 加上银币
            if adjList[0]+moneyList[0]+moneyList[1]//10 < 0:
                # 依然不够则加上铜币支付
                cpNum = (adjList[0]+moneyList[0]+moneyList[1]//10)*-100
                moneyList[0] = 0
                moneyList[1] -= moneyList[1]//10
                moneyList[2] -= cpNum
            else:
                spNum = (adjList[0]+moneyList[0])*-10
                moneyList[0] = 0
                moneyList[1] -= spNum
        else:
            moneyList[0] = adjList[0]+moneyList[0]
        preMoneyStr = self.__ShowMoney(groupId, personId)
        self.pcStateDict[groupId][personId]['金钱'] = moneyList
        # UpdateJson(self.pcStateDict, LOCAL_PCSTATE_PATH)
        curMoneyStr = self.__ShowMoney(groupId, personId)
        return f'的金钱{commandStr} ({preMoneyStr}->{curMoneyStr})'


        
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
            del self.initInfoDict[groupId]
            # UpdateJson(self.initInfoDict, LOCAL_INITINFO_PATH)
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
        # UpdateJson(self.initInfoDict, LOCAL_INITINFO_PATH)
        return f'已经将{name}从先攻列表中删除'
   
    def __JoinInitList(self, groupId, personId, name, initAdj, isPC) -> str:
        try: #查找已存在的先攻信息
            initInfo = self.initInfoDict[groupId]
        except: #如未找到, 就创建一个新的先攻信息
            initInfo = {'date': GetCurrentDateStr(), 'initList':{}}

        if initAdj.find('抗性') != -1 or initAdj.find('易伤') != -1:
            return '抗性与易伤关键字不能出现在此处!'
            
        #initAdj 有两种情况, 一是调整值, 二是固定值
        if not initAdj or initAdj[0] in ['+','-'] or initAdj[:2] in ['优势','劣势']: #通过符号判断
            error, resultStr, rollResult = RollDiceCommond('d20'+initAdj)
        else:
            error, resultStr, rollResult = RollDiceCommond(initAdj)
        if error: return resultStr
        initResult = rollResult.totalValueList[0]
            
        if isPC: # maxhp = 0 或 -1 影响先攻列表的显示与否
            hp, maxhp = (0, 0)
        else:
            hp, maxhp = (0, 0)
        name = name.lower()
        initInfo['initList'][name] = {'id':personId, 'init':initResult, 'hp':hp, 'maxhp':maxhp, 'alive':True, 'isPC':isPC}
        self.initInfoDict[groupId] = initInfo
        # UpdateJson(self.initInfoDict, LOCAL_INITINFO_PATH)
        
        return f'{name}先攻:{resultStr}'

    def __JoinTeam(self, groupId, personId, name) -> str:
        try:
            self.pcStateDict[groupId][personId]['熟练加值']
        except:
            return '必须先记录角色卡才能加入队伍~'

        try:
            teamDict = self.teamInfoDict[groupId]
            name = teamDict['name']
        except:
            teamDict = {}
            if not name:
                name = '无名小队'
            teamDict['name'] = name
            teamDict['members'] = []
        teamDict['members'].append(personId)
        self.teamInfoDict[groupId] = teamDict
        # UpdateJson(self.teamInfoDict, LOCAL_TEAMINFO_PATH)
        return f'成功加入{name}, 当前共{len(teamDict["members"])}人。 查看队伍信息请输入 .队伍信息 或 .完整队伍信息'

    def __ClearTeam(self, groupId) -> str:
        try: #查找已存在的先攻信息
            del self.teamInfoDict[groupId]
            # UpdateJson(self.teamInfoDict, LOCAL_TEAMINFO_PATH)
            return '队伍信息已经删除啦'
        except: #如未找到, 返回错误信息
            return '无法删除不存在的队伍哦'

    def __ShowTeam(self, groupId) -> str:
        try:
            teamDict = self.teamInfoDict[groupId]
            name = teamDict['name']
        except:
            return '还没有创建队伍哦~'
        result = f'{name}:'
        for pId in teamDict['members']:
            try:
                nickName = self.nickNameDict[groupId][pId]
            except:
                nickName = pId
            result += f'\n{self.__GetPlayerInfoShort(groupId, pId, nickName)}'
            
        return result

    def __ShowTeamFull(self, groupId) -> str:
        try:
            teamDict = self.teamInfoDict[groupId]
            name = teamDict['name']
        except:
            return '还没有创建队伍哦~'
        result = f'{name}的完整信息:'

        for pId in teamDict['members']:
            try:
                nickName = self.nickNameDict[groupId][pId]
            except:
                nickName = pId
            result += f'\n{self.__GetPlayerInfoFull(groupId, pId, nickName)}'
        return result

    def __CookCheck(self, cookAdj, keywordList)->(int, str):
        #第一个返回值是执行状况, -1为异常, 0为正常
        result = ''
        #cookAdj 有两种情况, 一是调整值, 二是固定值
        if not cookAdj or cookAdj[0] in ['+','-'] or cookAdj[:2] in ['优势','劣势']: #通过符号判断
            error, resultStr, rollResult = RollDiceCommond('d20'+cookAdj)
        else:
            error, resultStr, rollResult = RollDiceCommond(cookAdj)
        if error: return -1, resultStr
        cookValue = rollResult.totalValueList[0]

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
            error, resultStr, rollResult = RollDiceCommond(numberStr)
            if error: return -1, resultStr
            number = rollResult.totalValueList[0]
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
        self.groupInfoDict[groupId]['active'] = activeState
        # UpdateJson(self.groupInfoDict, LOCAL_GROUPINFO_PATH)
        if activeState:
            return '伊丽莎白来啦~'
        else:
            return '那我就不说话咯~ #潜入水中 (咕嘟咕嘟)'

    @TypeAssert(times = int)
    def __DNDBuild(self, groupId, times) -> str:
        assert times > 0 and times < 10
        
        result = ''
        for i in range(times):
            error, resultStr, rollResult = RollDiceCommond(f'6#4d6k3')
            result += f'力量:{rollResult.rawResultList[0][0]}  敏捷:{rollResult.rawResultList[1][0]}  体质:{rollResult.rawResultList[2][0]}  '
            result += f'智力:{rollResult.rawResultList[3][0]}  感知:{rollResult.rawResultList[4][0]}  魅力:{rollResult.rawResultList[5][0]}'
            result += f'  共计:{sum(rollResult.totalValueList)}'
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
            return HELP_COMMAND_HP_STR
        elif '法术位' in subType:
            return HELP_COMMAND_SpellSlot_STR
        elif '金钱' in subType:
            return HELP_COMMAND_Money_STR
        elif subType == 'jrrp':
            return HELP_COMMAND_JRRP_STR
        elif subType == 'send':
            return HELP_COMMAND_SEND_STR
        elif subType == 'draw':
            return HELP_COMMAND_DRAW_STR
        elif subType == '烹饪':
            return HELP_COMMAND_COOK_STR
        elif subType == '点菜':
            return HELP_COMMAND_ORDER_STR
        elif subType == '今日菜单':
            return HELP_COMMAND_MENU_STR
        elif '角色卡' in subType or '人物卡' in subType:
            return HELP_COMMAND_PC_STR
        elif '队伍' in subType:
            return HELP_COMMAND_TEAM_STR
        elif '检定' in subType:
            return HELP_COMMAND_CHECK_STR
        elif subType == '技能':
            return HELP_COMMAND_SKILL_STR
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
            error, resultStr, rollResult = RollDiceCommond(f'd{size}')
            if error: return resultStr
            index = rollResult.totalValueList[0]-1
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
                error, resultStr, rollResult = RollDiceCommond(f'd{size}')
                if error: return resultStr
                index = rollResult.totalValueList[0]-1
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
        usedDishList = []
        for typeStr in MENU_TYPE_LIST:
            possDish, delKeyList = self.__FindDishList([typeStr, todayCuisine, todayStyle])
            if len(possDish) != 0 and len(delKeyList) <= 1:
                dishName = RandomSelectList(possDish, 1)[0]
                if dishName in usedDishList:
                    continue
                usedDishList.append(dishName)
                dishInfo = self.menuDict[dishName]
                result += f'{typeStr}:{dishName} {dishInfo["价格"]}\n{dishInfo["描述"]}\n'

        return result[:-1]

def ModifyHPInfo(stateDict, subType, hp, maxhp, name, resultStrHp) -> (dict, str):
    assert subType in ['=', '+', '-']
    result = ''
    preHP = stateDict['hp']
    if subType == '=':
        stateDict['hp'] = hp
        stateDict['alive'] = True
        result = f'成功将{name}的生命值设置为{resultStrHp}'
        if maxhp:
            stateDict['maxhp'] = maxhp
            result += f', 最大生命值是{maxhp}'
    elif subType == '+':
        stateDict['hp'] += hp
        stateDict['alive'] = True
        result = f'{name}的生命值增加了{resultStrHp} ({preHP}->{stateDict["hp"]})'
    elif subType == '-':
        if stateDict['alive']:
            if stateDict['hp'] > 0 and hp >= stateDict["hp"]:
                stateDict['hp'] = 0
                stateDict['alive'] = False
                result = f'{name}的生命值减少了{resultStrHp} ({preHP}->0)\n因为生命值降至0, {name}昏迷/死亡了!'
            else:
                stateDict['hp'] -= hp
                result = f'{name}的生命值减少了{resultStrHp} ({preHP}->{stateDict["hp"]})'
        else:
            result = f'{name}的生命值减少了{resultStrHp}\n{name}当前生命值已经是0, 无法再减少了 (0->0)'

    return stateDict, result

def Str2MoneyList(commandStr) -> (int, str, list):
    moneyList = [0,0,0]
    gpIndex = commandStr.find('gp')
    spIndex = commandStr.find('sp')
    cpIndex = commandStr.find('cp')
    if gpIndex == -1 and spIndex == -1 and cpIndex == -1:
        try:
            moneyList[0] = int(commandStr)
            return 0, '', moneyList
        except:
            return -1, '找不到有效的关键字["gp", "sp", "cp"]', None
    if gpIndex != -1:
        try:
            value = int(commandStr[0:gpIndex])
            moneyList[0] = value
            assert value >= -100000000 and value <= 100000000
            gpIndex += 2
        except:
            return -1, f'{commandStr[0:gpIndex]}不是有效的数额', None
    if spIndex != -1:
        try:
            startIndex = max(gpIndex, 0)
            value = int(commandStr[startIndex:spIndex])
            moneyList[1] = value
            assert value >= -100000000 and value <= 100000000
            spIndex += 2
        except:
            return -1, f'{commandStr[startIndex:spIndex]}不是有效的数额', None
    if cpIndex != -1:
        try:
            startIndex = max([0, gpIndex, spIndex])
            value = int(commandStr[startIndex:cpIndex])
            moneyList[2] = value
            assert value >= -100000000 and value <= 100000000
        except:
            return -1, f'{commandStr[startIndex:cpIndex]}不是有效的数额', None
    return 0, '', moneyList

def CreateNewUserInfo(userDict, personId):
    userDict[personId] = userInfoTemp

def CreateNewGroupInfo(groupDict, groupId):
    groupDict[groupId] = groupInfoTemp

def UpdateAllUserInfo(userDict):
    deletedUserList = []
    deletedList = []
    for userId in userDict.keys():
        userInfoCur = userDict[userId]
        if type(userInfoCur) != dict:
            deletedUserList.append(userId)
            continue

        for curK in userInfoCur.keys():
            if not curK in userInfoTemp.keys():
                deletedList.append((userId, curK))

        for k in userInfoTemp.keys():
            if not k in userInfoCur.keys():
                userInfoCur[k] = userInfoTemp[k]

    for pair in deletedList:
        del userDict[pair[0]][pair[1]]

    for userId in deletedUserList:
        del userDict[userId]

def UpdateAllGroupInfo(groupDict):
    deletedGroupList = []
    deletedList = []
    for groupId in groupDict.keys():
        groupInfoCur = groupDict[groupId]

        if type(groupInfoCur) != dict:
            deletedGroupList.append(groupId)
            continue

        # Temp code, delete after next update
        try:
            groupInfoCur['active'] = bool(groupInfoCur['Active'])
        except:
            pass

        for curK in groupInfoCur.keys():
            if not curK in groupInfoTemp.keys():
                deletedList.append((groupId, curK))

        for k in groupInfoTemp.keys():
            if not k in groupInfoCur.keys():
                groupInfoCur[k] = groupInfoTemp[k]

    for pair in deletedList:
        del groupDict[pair[0]][pair[1]]

    for groupId in deletedGroupList:
        del groupDict[groupId]

def DetectSpam(currentDate, lastDateStr, accuNum, weight = 1) -> (bool, str, int):
    lastDate = Str2Datetime(lastDateStr)
    if currentDate - lastDate > MESSAGE_LIMIT_TIME:
        return False, Datetime2Str(currentDate), 0
    else:
        if accuNum + weight < MESSAGE_LIMIT_NUM:
            return False, lastDateStr, accuNum+weight
        else:
            return True, lastDateStr, accuNum+weight
