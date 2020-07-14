import numpy as np
import os
import re
import math
import datetime
import collections
import copy
import asyncio

from .tool_dice import RollDiceCommand, SplitDiceCommand, SplitNumberCommand, isDiceCommand, RollResult
from .tool_pc import *
from .type_assert import TypeAssert
from .utils import *
from .utils import UpdateJsonAsync
from .custom_config import *
from .info_help import *
from .info_game import *
from .info_chat import *
from .data_template import *

@TypeAssert(str)
async def ParseInput(inputStr):
    # 接受用户的输入, 输出一个数组, 包含指令类型与对应参数
    # 如不是命令则返回None
    inputStr = inputStr.strip()
    # 空字符串直接返回
    if not inputStr:
        return None
    # 首字符不是 '.' 说明不是命令
    if ChineseToEnglishSymbol(inputStr[0]) != '.':
        return None
    # 将符号转为英文(半角)
    inputStr = ChineseToEnglishSymbol(inputStr)
    
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
            commandStrOri = commandStr[len(commandKeyword):]
            commandStr = commandStrOri.strip() # 参数
            findCommand = True
            break
    # 无法直接找到匹配的关键字则尝试使用正则表达式判定
    if not findCommand:
        for i in range(len(commandKeywordReList)):
            result = re.match(commandKeywordReList[i], commandStr)
            if result:
                index = result.span(0)[1]
                commandType = commandStr[:index].strip() # 类型
                commandStrOri = commandStr[index:]
                commandStr = commandStrOri.strip() # 参数
                findCommand = True
                break
    if not findCommand:
        return None
        
    
    # 判断命令类型, 解析参数, 生成Command类的实例并返回
    # 掷骰命令
    if commandType == 'r':
        # 参数包含两部分, 骰子表达式与原因, 原因为可选项
        isHide = False
        isShort = False
        if commandStr and commandStr[0] == 'h':
            commandStr = commandStr[1:]
            isHide = True
        if commandStr and commandStr[0] == 's':
            commandStr = commandStr[1:]
            isShort = True
        diceCommand, reason = SplitDiceCommand(commandStr)
        return Command(CommandType.Roll,[diceCommand, reason, isHide, isShort])
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
        diceCommand, name = SplitDiceCommand(commandStrOri)
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
        subType = commandStr.replace(' ', '')
        return Command(CommandType.HELP,[subType])
    elif commandType == 'send':
        return Command(CommandType.SEND,[commandStr])
    elif commandType == '查询':
        target = commandStr.replace(' ', '')
        return Command(CommandType.QUERY,[target])
    elif commandType == '索引':
        return Command(CommandType.INDEX,[commandStr])
    elif commandType == 'dismiss':
        return Command(CommandType.DISMISS, [])
    elif commandType == 'welcome':
        return Command(CommandType.WELCOME, [commandStr])
    elif commandType == 'name':
        return Command(CommandType.NAME, [commandStr])
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
    elif commandType == '今日笑话':
        return Command(CommandType.TodayJoke, [0])
    elif commandType == '昨日笑话':
        return Command(CommandType.TodayJoke, [-1])
    elif commandType == '明日笑话':
        return Command(CommandType.TodayJoke, [1])
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
    elif commandType == '队伍点名':
        return Command(CommandType.TEAM, ['点名'])
    elif commandType == '记录金钱':
        return Command(CommandType.MONEY, ['记录', commandStr])
    elif commandType == '清除金钱':
        return Command(CommandType.MONEY, ['清除'])
    elif commandType == '查看金钱':
        return Command(CommandType.MONEY, ['查看'])
    elif commandType == '记录笔记':
        return Command(CommandType.NOTE, ['记录', commandStr])
    elif commandType == '查看笔记' or commandType == '笔记':
        return Command(CommandType.NOTE, ['查看', commandStr])
    elif commandType == '清除笔记':
        return Command(CommandType.NOTE, ['清除', commandStr])
    elif commandType == '金钱':
        if commandStr == '':
            return Command(CommandType.MONEY, ['查看'])
        else:
            return Command(CommandType.MONEY, ['更改', commandStr])
    elif commandType == '队伍金钱':
        return Command(CommandType.TeamMoney, [commandStr])
    elif commandType == '长休':
            return Command(CommandType.REST, ['长休'])
    elif commandType == '答题':
            return Command(CommandType.Question, [commandStr])
    elif commandType == 'savedata':
        return Command(CommandType.MASTER, ['savedata'])
    elif commandType == 'credit':
        return Command(CommandType.MASTER, ['credit', commandStr])
    elif commandType == 'notice':
        return Command(CommandType.MASTER, ['notice', commandStr])
    elif commandType == 'dp':
        return Command(CommandType.MASTER, ['daily', commandStr])
    elif commandType == '好感度':
        return Command(CommandType.CREDIT, [])
    elif 'hp' in commandType:
        commandStr = commandType[:commandType.find('hp')]+commandStr
        subType = None
        targetStr = None
        hpCommand = None
        commandStr = commandStr.strip()
        if len(commandStr) == 0:
            return Command(CommandType.HP, ['查看'])
        if commandStr == 'clr':
            return Command(CommandType.HP, ['清除'])
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
        return Command(CommandType.HP, ['记录', targetStr, subType, hpStr, maxhpStr])
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
        if commandType[:2] == '队伍':
            diceCommand, reason = SplitDiceCommand(commandStr)
            return Command(CommandType.TeamCheck, [commandType[2:-2], diceCommand, reason])
        else:
            diceCommand, reason = SplitDiceCommand(commandStr)
            return Command(CommandType.CHECK, [commandType[:-2], diceCommand, reason])
    elif '豁免' in commandType:
        diceCommand, reason = SplitDiceCommand(commandStr)
        return Command(CommandType.CHECK, [commandType, diceCommand, reason])
    elif '攻击' in commandType:
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
        self.dailyInfoDict = ReadJson(LOCAL_DAILYINFO_PATH)
        
        UpdateAllGroupInfo(self.groupInfoDict)
        UpdateAllUserInfo(self.userInfoDict)
        self.dailyInfoDict = UpdateDailyInfoDict(self.dailyInfoDict)

        print(f'个人资料库加载成功!')
        # 尝试加载查询资料库
        try:
            filesPath = os.listdir(LOCAL_QUERYINFO_DIR_PATH) #读取所有文件名
            filesPath = sorted(filesPath)
            print(f'找到以下查询资料: {filesPath}')
            self.queryInfoDict = collections.OrderedDict()
            self.querySynDict = {}
            for fp in filesPath:
                try:
                    assert fp[-5:] == '.json'
                    absPath = os.path.join(LOCAL_QUERYINFO_DIR_PATH, fp)
                    currentQueryInfoDict = ReadJson(absPath)
                    if fp[:3] == 'syn':
                        self.querySynDict.update(currentQueryInfoDict)
                        print(f'成功加载同义词表{fp}, 共{len(currentQueryInfoDict)}个条目')
                    else:
                        self.queryInfoDict.update(currentQueryInfoDict)
                        # print(f'成功加载{fp}, 共{len(currentQueryInfoDict)}个条目')
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
            filesPath = sorted(filesPath)
            print(f'找到以下牌堆: {filesPath}')
            self.deckDict = collections.OrderedDict()
            for fp in filesPath:
                try:
                    assert fp[-5:] == '.json'
                    absPath = os.path.join(LOCAL_DECKINFO_DIR_PATH, fp)
                    currentDeckDict = ReadJson(absPath)
                    assert len(currentDeckDict['list']) > 0, f'{fp}是一个空牌堆!'
                    self.deckDict[currentDeckDict['title']] = currentDeckDict
                    # print(f'成功加载{fp}, 牌堆名为{currentDeckDict["title"]}, 共{len(currentDeckDict["list"])}个条目')
                except Exception as e:
                    print(e)
            # 检查依赖是否存在
            invalidDeck = []
            hasInvalid = False
            hasCheck = False
            while hasCheck and not hasInvalid:
                hasCheck = True
                for deck in self.deckDict.keys():
                    for relay in deckDict[deck]['relay']:
                        if not relay in self.deckDict.keys():
                            invalidDeck.append([deck, f'依赖的牌堆{relay}不存在'])
                            hasInvalid = True
                if hasInvalid:
                    for invalid in invalidDeck:
                        del self.deckDict[invalid[0]]
                        print(f'移除无效牌堆:{invalid[0]}, 原因是{invalid[1]}')
                    hasInvalid = False
                    hasCheck = False # 需要重新检查依赖

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
                    # print(f'成功加载{fp}, 共{len(currentMenuDict)}个菜谱')
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

        # 尝试加载笑话资料库
        try:
            self.jokeDict = ReadJson(LOCAL_JOKEINFO_PATH)
            validImgList = []
            for imgPath in self.jokeDict['img']:
                absPath = os.path.join(LOCAL_JOKEIMG_DIR_PATH, imgPath)
                if os.path.exists(absPath):
                    validImgList.append(imgPath)
            print(f'共{len(validImgList)}个有效图片')
            self.jokeDict['img'] = validImgList

            assert len(self.jokeDict['word']) > 0
            assert self.jokeDict['img']
            print(f'笑话资料库加载成功! 共{len(self.jokeDict["word"])}个文字条目, {len(self.jokeDict["img"])}个图片条目')
        except: 
            print(f'笑话资料库加载失败!')
            self.jokeDict = None

        # 尝试加载表情包
        try:
            self.emotionDict = {}
            filesPath = os.listdir(LOCAL_EMOTIMG_DIR_PATH)
            for fp in filesPath:
                try:
                    name, suffix = fp.split('.')
                    assert suffix in ['jpg', 'png', 'gif']
                    absPath = os.path.join(LOCAL_EMOTIMG_DIR_PATH, fp)
                    if os.path.exists(absPath):
                        self.emotionDict[name] = absPath
                except:
                    pass
            assert len(self.emotionDict) != 0
            print(f'表情包加载成功! 共{len(self.emotionDict)}个条目, 分别是{self.emotionDict.keys()}')
        except:
            print(f'表情包加载失败!')
            self.emotionDict = None

        # 尝试加载姓名资料库
        try:
            self.nameInfoDict = ReadJson(LOCAL_NAMEINFO_PATH)
            # 校验有效性
            for index in self.nameInfoDict['meta'].keys():
                for info in self.nameInfoDict['meta'][index]:
                    assert info[0] in self.nameInfoDict['info'].keys()
                    assert len(info) > 1
                    for i in range(1, len(info)):
                        assert i >= 0
                        assert i < len(self.nameInfoDict['info'][info[0]])
            print(f'姓名资料库加载成功! 共{len(self.nameInfoDict["meta"])}个种类, {len(self.nameInfoDict["info"])}个词库')
        except Exception as e:
            print(f'姓名资料库加载失败! {e}')
            self.nameInfoDict = None

        # 尝试加载题库
        try:
            self.questionDict = ReadJson(LOCAL_QUESINFO_PATH)
            for k in self.questionDict.keys():
                assert len(self.questionDict[k]) != 0
            assert len(self.questionDict) != 0
            print(f'题库加载成功! 共{len(self.questionDict)}个条目, 分别是{[(k, len(self.questionDict[k])) for k in self.questionDict.keys()]}')
        except:
            print(f'题库加载失败!')
            self.questionDict = None


    async def UpdateLocalData(self):
        await UpdateJsonAsync(self.nickNameDict, LOCAL_NICKNAME_PATH)
        await UpdateJsonAsync(self.initInfoDict, LOCAL_INITINFO_PATH)
        await UpdateJsonAsync(self.pcStateDict, LOCAL_PCSTATE_PATH)
        await UpdateJsonAsync(self.groupInfoDict, LOCAL_GROUPINFO_PATH)
        await UpdateJsonAsync(self.userInfoDict, LOCAL_USERINFO_PATH)
        await UpdateJsonAsync(self.teamInfoDict, LOCAL_TEAMINFO_PATH)
        await UpdateJsonAsync(self.dailyInfoDict, LOCAL_DAILYINFO_PATH)

    async def UpdateGroupInfo(self, groupInfoDictUpdate):
        result = []
        invalidGroupId = []
        try:
            for gId in self.groupInfoDict.keys():
                if not gId in groupInfoDictUpdate.keys():
                    invalidGroupId.append(gId)
                else:
                    self.groupInfoDict[gId]['name'] = groupInfoDictUpdate[gId]
            if len(invalidGroupId) != 0:
                for gId in invalidGroupId:
                    del self.groupInfoDict[gId]
                result += [CommandResult(CoolqCommandType.MESSAGE, f'已删除不存在群: {invalidGroupId}', personIdList = MASTER)]
        except Exception as e:
            result = [CommandResult(CoolqCommandType.MESSAGE, f'更新群信息时出现错误: {e}', personIdList = MASTER)]
        # 清除无用信息
        DeleteInvalidInfo(self.nickNameDict, self.groupInfoDict.keys())
        DeleteInvalidInfo(self.initInfoDict, self.groupInfoDict.keys())
        DeleteInvalidInfo(self.pcStateDict, self.groupInfoDict.keys())
        DeleteInvalidInfo(self.teamInfoDict, self.groupInfoDict.keys())
        return result

    async def DailyUpdate(self):
        # 只保留键在sourceKeys中的targetDict条目
        result = []
        errorInfo = ''
        # 逐个处理用户信息
        liveUserNum = 0
        activeUserNum = 0
        invalidUser = []
        for pId in self.userInfoDict.keys():
            try:
                userInfoCur = self.userInfoDict[pId]
                userInfoCur['warning'] = 0
                userInfoCur['seenJoke'][0] = userInfoCur['seenJoke'][1]
                userInfoCur['seenJoke'][1] = userInfoCur['seenJoke'][2]
                userInfoCur['seenJoke'][2] = 1
                userInfoCur['seenJRRP'] = False
                userInfoCur['seenJRCD'] = False
                userInfoCur['seenCredit'] = False
                # 最近一天有过dnd指令则增加好感度
                if userInfoCur['dndCommandDaily'] != 0:
                    userInfoCur['credit'] += DAILY_CREDIT_FIX
                    liveUserNum += 1 # 统计用户
                if userInfoCur['dailyCredit'] >= DAILY_CREDIT_LIMIT:
                    activeUserNum += 1 # 统计活跃用户
                if userInfoCur['credit'] < 0:
                    userInfoCur['credit'] = min(0, userInfoCur['credit'] + 10)
                userInfoCur['dailyCredit'] = 0
                userInfoCur['commandDaily'] = 0
                userInfoCur['messageDaily'] = 0
                userInfoCur['dndCommandDaily'] = 0
                # 处理过期的IA交互信息
                for i in range(len(userInfoCur['IACommand'])-1, -1, -1):
                    IAInfo = userInfoCur['IACommand'][i]
                    if Str2Datetime(IAInfo['date']) < GetCurrentDateRaw():
                        userInfoCur['IACommand'].pop(i)
                # 清除过久没有使用的用户 (不清除拉黑用户)
                lastTime = GetCurrentDateRaw() - Str2Datetime(groupInfoCur['activeDate'])
                if lastTime >= datetime.timedelta(days = 10) and userInfoCur['credit'] >= 0:
                    userInfoCur['credit'] -= 10
                    if userInfoCur['credit'] < 0:
                        invalidUser.append(pId)
            except Exception as e:
                errorInfo += f'\n处理用户{pId}时的异常:{e}'

        for pId in invalidUser:
            del self.userInfoDict[pId]

        warningGroup = []
        dismissGroup = []
        for gId in self.groupInfoDict.keys():
            try:
                groupInfoCur = self.groupInfoDict[gId]
                lastTime = GetCurrentDateRaw() - Str2Datetime(groupInfoCur['activeDate'])
                if lastTime >= datetime.timedelta(days = 7):
                    if groupInfoCur['warning'] <= 1:
                        groupInfoCur['warning'] += 1
                        warningGroup.append(gId)
                    else:
                        dismissGroup.append(gId)
                else:
                    groupInfoCur['warning'] = 0
                # 更新每日数据
                groupInfoCur['commandDaily'] = 0
                groupInfoCur['messageDaily'] = 0
                groupInfoCur['dndCommandDaily'] = 0
                groupInfoCur['days'] += 1
            except Exception as e:
                errorInfo += f'\n处理群{gId}时的异常:{e}'

        if warningGroup:
            result += [CommandResult(CoolqCommandType.MESSAGE, LEAVE_WARNING_STR, groupIdList = warningGroup)]
        if dismissGroup:
            result += [CommandResult(CoolqCommandType.DISMISS, LEAVE_NOTICE_STR, groupIdList = dismissGroup)]
            for gId in dismissGroup:
                del self.groupInfoDict[gId]
        
        # 更新日志信息
        try:
            self.dailyInfoDict = UpdateDailyInfoDict(self.dailyInfoDict)
        except Exception as e:
            errorInfo += f'\n更新日志时的异常:{e}'

        # 清除无用信息
        DeleteInvalidInfo(self.nickNameDict, self.groupInfoDict.keys())
        DeleteInvalidInfo(self.initInfoDict, self.groupInfoDict.keys())
        DeleteInvalidInfo(self.pcStateDict, self.groupInfoDict.keys())
        DeleteInvalidInfo(self.teamInfoDict, self.groupInfoDict.keys())

        result += [CommandResult(CoolqCommandType.MESSAGE, f'成功更新今日数据 警告:{warningGroup} 退群:{dismissGroup}\n昨日发言用户:{liveUserNum} 活跃用户:{activeUserNum}', MASTER)]
        if errorInfo:
            result += [CommandResult(CoolqCommandType.MESSAGE, '异常信息:'+errorInfo, MASTER)]
        await self.UpdateLocalData()
        return result

    async def ProcessMessage(self, inputStr, personId, personName, groupId = None, onlyToMe = False):
        # 检查个人信息是否存在
        try:
            assert personId in self.userInfoDict.keys()
        except:
            CreateNewUserInfo(self.userInfoDict, personId)
        userInfoCur = self.userInfoDict[personId]

        if groupId: # 当是群聊信息时, 检查群聊信息是否存在
            try:
                assert groupId in self.groupInfoDict.keys()
            except:
                CreateNewGroupInfo(self.groupInfoDict, groupId)
            groupInfoCur = self.groupInfoDict[groupId]

        # 统计信息次数
        userInfoCur['messageAccu'] += 1
        userInfoCur['messageDaily'] += 1
        if groupId:
            groupInfoCur['messageAccu'] += 1
            groupInfoCur['messageDaily'] += 1

        # 黑名单检测
        if userInfoCur['credit'] < 0:
            return None
        if userInfoCur['warning'] >= 2 or userInfoCur['ban'] >= 3:
            return None

        # 检测彩蛋
        if groupId and userInfoCur['credit'] >= CHAT_CREDIT_LV0:
            diffTime = Str2Datetime(groupInfoCur['chatDate'])-GetCurrentDateRaw()
            if diffTime <= CHAT_LIMIT_TIME:
                resultList = await self.ProcessChatCommand(inputStr, userInfoCur['credit'])
            if resultList:
                groupInfoCur['chatDate'] = GetCurrentDateStr()
                return resultList

        # 检测交互命令
        resultList = []
        if userInfoCur['IACommand']:
            newIAList = []
            # 先检查有效性
            for i in range(len(userInfoCur['IACommand'])):
                IAInfo = userInfoCur['IACommand'][i]
                # 如果该条交互指令且已经过期或已经处理该条交互指令, 则不保留该条交互指令
                if Str2Datetime(IAInfo['date']) < GetCurrentDateRaw():
                    try:
                        if IAInfo['warning']:
                            if groupId:
                                resultList += [CommandResult(CoolqCommandType.MESSAGE, IAInfo['warning'], personIdList = [personId], groupIdList = [groupId])]
                            else:
                                resultList += [CommandResult(CoolqCommandType.MESSAGE, IAInfo['warning'], personIdList = [personId])]
                    except:
                        pass
                else:
                    newIAList.append(IAInfo)
            userInfoCur['IACommand'] = newIAList

            # 再处理指令 (要考虑有些指令可能会在中途注册指令)
            for i in range(len(userInfoCur['IACommand'])):
                IAInfo = userInfoCur['IACommand'][i]
                if (groupId and IAInfo['groupId'] == groupId) or (not groupId and IAInfo['groupId'] == 'Private'):
                    targetFun = getattr(self, IAInfo['name'])
                    result = targetFun(IAInfo, inputStr)
                    try:
                        if not IAInfo['isRepeat'] or inputStr in ['q', 'Q']:
                            IAInfo['isValid'] = False
                    except:
                        IAInfo['isValid'] = False
                    if result:
                        self.dailyInfoDict['IACommand'] += 1
                        resultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

            # 最后删除valid不为false的指令
            newIAList = []
            for i in range(len(userInfoCur['IACommand'])):
                IAInfo = userInfoCur['IACommand'][i]
                try:
                    if IAInfo['isValid']:
                        newIAList.append(IAInfo)
                except:
                    pass
            userInfoCur['IACommand'] = newIAList

        if len(resultList) != 0:
            commandWeight = 2
            # 刷屏检测
            try:
                isSpam, dateStr, accuNum = DetectSpam(GetCurrentDateRaw(),
                    userInfoCur['activeDate'], userInfoCur['spamAccu'], commandWeight)
                userInfoCur['activeDate'] = dateStr
                userInfoCur['spamAccu'] = accuNum
                if isSpam and not personId in MASTER:
                    userInfoCur['credit'] -= 100
                    userWarning = userInfoCur['warning']
                    if userWarning == 0:
                        resultList = [CommandResult(CoolqCommandType.MESSAGE, f'检测到{nickName} {personId}的刷屏行为, 黄牌警告!')]
                    elif userWarning == 1:
                        resultList = [CommandResult(CoolqCommandType.MESSAGE, f'检测到{nickName} {personId}的刷屏行为, 不理你了!')]
                        userInfoCur['ban'] += 1
                    userInfoCur['warning'] += 1
            except Exception as e:
                print(f'DetectSpam:{e}')
            return resultList

        # 检测命令(以.开头)
        command = await ParseInput(inputStr)
        if command is None:
            return None
        # 检查激活状态
        if groupId:
            try:
                assert groupInfoCur['active'] == True # 已有记录且是激活状态并继续执行命令
            except:
                if groupInfoCur['active'] == False and onlyToMe == False and inputStr.find('bot') == -1: # 已有记录且是非激活状态, 且不是单独指令, 则不执行命令
                    return None
        else:
            groupInfoCur = None

        # 统计命令次数
        userInfoCur['commandAccu'] += 1
        userInfoCur['commandDaily'] += 1
        if groupId:
            groupInfoCur['commandAccu'] += 1
            groupInfoCur['commandDaily'] += 1
        # 统计dnd命令次数
        if command.cType in dndCommandDict:
            userInfoCur['dndCommandAccu'] += 1
            userInfoCur['dndCommandDaily'] += 1
            if groupId:
                groupInfoCur['dndCommandAccu'] += 1
                groupInfoCur['dndCommandDaily'] += 1

        # 尝试读取昵称
        try:
            nickName = self.nickNameDict[groupId][personId]
        except:
            try:
                nickName = self.nickNameDict['Private'][personId]
            except:
                nickName = personName

        resultList, commandWeight = await self.__ProcessInput(command, personId, nickName, userInfoCur, groupId, groupInfoCur, onlyToMe)

        # 最后处理
        if len(resultList) == 0:
            return None

        # 刷屏检测
        try:
            isSpam, dateStr, accuNum = DetectSpam(GetCurrentDateRaw(),
                userInfoCur['activeDate'], userInfoCur['spamAccu'], commandWeight)
            userInfoCur['activeDate'] = dateStr
            userInfoCur['spamAccu'] = accuNum
            if isSpam and not personId in MASTER:
                userInfoCur['credit'] -= 100
                userWarning = userInfoCur['warning']
                if userWarning == 0:
                    resultList = [CommandResult(CoolqCommandType.MESSAGE, f'检测到{nickName} {personId}的刷屏行为, 黄牌警告!')]
                elif userWarning == 1:
                    resultList = [CommandResult(CoolqCommandType.MESSAGE, f'检测到{nickName} {personId}的刷屏行为, 不理你了!')]
                    userInfoCur['ban'] += 1
                userInfoCur['warning'] += 1
        except Exception as e:
            print(f'DetectSpam:{e}')

        if groupId:
            groupInfoCur['activeDate'] = GetCurrentDateStr()
            if groupInfoCur['noticeBool']:
                resultList += [CommandResult(CoolqCommandType.MESSAGE, groupInfoCur['noticeStr'])]
                groupInfoCur['noticeBool'] = False
        self.dailyInfoDict['totalCommand'] += 1
        if userInfoCur['dailyCredit'] < DAILY_CREDIT_LIMIT:
            userInfoCur['dailyCredit'] += 1
            userInfoCur['credit'] += 1

        return resultList
            
    async def ProcessChatCommand(self, inputStr, credit):
        # 检测可能的聊天信息
        possChatList = []

        for keyRe in CHAT_COMMAND_COMMON.keys():
            result = re.match(keyRe, inputStr, flags = re.I)
            if result:
                possChatList.append(CHAT_COMMAND_COMMON[keyRe])
        if len(possChatList) != 0:
            possChatList = RandomSelectList(possChatList)[0]
            possChatList = [info[1] for info in possChatList if credit>=info[0] and ((len(info))!=3 or credit<= info[2])]
            if possChatList == 0:
                return None
            result = RandomSelectList(possChatList)[0]
            result = InsertEmotion(result, self.emotionDict)
            return [CommandResult(CoolqCommandType.MESSAGE, result)]

        for keyRe in CHAT_COMMAND_FUNCTION.keys():
            result = re.match(keyRe, inputStr, flags = re.I)
            if result:
                possChatList.append(CHAT_COMMAND_FUNCTION[keyRe])
        if len(possChatList) != 0:
            targetFun = RandomSelectList(possChatList)[0]
            result = targetFun(inputStr, credit)
            if result:
                return [CommandResult(CoolqCommandType.MESSAGE, result)]
        return None


    # 接受输入字符串，返回输出字符串
    async def __ProcessInput(self, command, personId, nickName, userInfoCur, groupId, groupInfoCur, onlyToMe) -> list:
        # 处理命令
        commandResultList = []
        commandWeight = 1
        cType = command.cType
        if not groupId:
            groupId = 'Private'
        if cType == CommandType.Roll:
            self.dailyInfoDict['rollCommand'] += 1
            diceCommand = command.cArg[0]
            reason = command.cArg[1]
            isHide = command.cArg[2]
            isShort = command.cArg[3]
            if diceCommand == '':
                diceCommand = 'd'
            if len(reason) != 0:
                reason = f'由于{reason},'
            error, resultStr, rollResult = RollDiceCommand(diceCommand)
            if error:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, resultStr)]
            else:
                if isShort:
                    if len(rollResult.totalValueList) == 1:
                        resultStr = str(rollResult.totalValueList[0])
                    else:
                        resultStr = '{'
                        for totalVal in rollResult.totalValueList:
                            resultStr += f'{totalVal}, '
                        resultStr = resultStr[:-2] + '}'
                finalResult = f'{reason}{nickName}掷出了{resultStr}'
                try:
                    if (resultStr[:3] == 'D20' or resultStr[:4] == '1D20'):
                        if rollResult.rawResultList[0][0] == 20:
                            finalResult += ', 大成功!'
                        elif rollResult.rawResultList[0][0] == 1:
                            finalResult += ', 大失败!'
                    elif resultStr.find('次D20') != -1 or resultStr.find('次1D20') != -1:
                        succTimes = 0
                        failTimes = 0
                        for resList in rollResult.rawResultList:
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
                    if groupId == 'Private': commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '群聊时才能暗骰哦~')]
                    finalResult = f'暗骰结果:{finalResult}'
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult, personIdList = [personId]),
                            CommandResult(CoolqCommandType.MESSAGE, f'{nickName}进行了一次暗骰')]
                else:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult)]

        elif cType == CommandType.BOT:
            commandWeight = 3
            if groupId == 'Private': commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            
            subType = command.cArg[0]
            if subType == 'show':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, SHOW_STR)]
            elif onlyToMe:
                if subType == 'on':
                    result = self.__BotSwitch(groupId, True)
                else:
                    result = self.__BotSwitch(groupId, False)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.DISMISS:
            if not onlyToMe: return None #'不指定我的话, 这个指令是无效的哦'
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '再见咯~'),
                                  CommandResult(CoolqCommandType.DISMISS,groupIdList = [groupId])]

        elif cType == CommandType.NickName:
            newNickName = command.cArg[0]
            if len(newNickName) <= 20:
                result = self.UpdateNickName(groupId, personId, newNickName)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
            else:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'你的名字是什么呀...记不住啦~')]

        elif cType == CommandType.HELP:
            subType = str(command.cArg[0])
            helpInfo = self.__GetHelpInfo(subType)
            if helpInfo:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, helpInfo)]

        elif cType == CommandType.INIT:
            self.dailyInfoDict['initCommand'] += 1
            commandWeight = 4
            subType = command.cArg[0]
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                if not subType:
                    result = self.__GetInitList(groupId)
                elif subType == 'clr':
                    result = self.__ClearInitList(groupId)
                elif subType[:3] == 'del':
                    nameList = subType[3:].split('/')
                    result = ''
                    for name in nameList:
                        if not result:
                            result = self.__RemoveInitList(groupId, name.strip())
                        else:
                            result += '\n' + self.__RemoveInitList(groupId, name.strip())
                else:
                    return None
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.RI:
            self.dailyInfoDict['initCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                initAdj = command.cArg[0]
                if not command.cArg[1]:
                    isPC = True
                    nameList = [nickName]
                else:
                    isPC = False
                    nameList = command.cArg[1].split('/')
                finalResult = ''
                for name in nameList:
                    initAdjSub = initAdj
                    for i in range(len(name)):
                        if name[i] in ['+', '-'] and name[i+1:] and isDiceCommand(name[i+1:]):
                            initAdjSub += name[i:]
                            name = name[:i]
                            break
                    result = self.JoinInitList(groupId, personId, name, initAdjSub, isPC)
                    if not finalResult:
                        finalResult = result
                    else:
                        finalResult += f'\n{result}'
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult)]

        elif cType == CommandType.HP:
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                self.dailyInfoDict['hpCommand'] += 1
                subType = command.cArg[0]
                if subType == '记录':
                    # Args: [targetStr, subType , hpStr, maxhpStr]
                    result = UpdateHP(self, groupId, personId, *command.cArg[1:], nickName)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '查看':
                    result = ShowHP(self, groupId, personId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'{nickName}{result}')]
                elif subType == '清除':
                    ClearHP(self, groupId, personId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'已经忘记了{nickName}的生命值...')]

        elif cType == CommandType.PC:
            self.dailyInfoDict['pcCommand'] += 1
            commandWeight = 3
            subType = command.cArg[0]
            infoStr = command.cArg[1]
            if groupId == 'Private' and subType != '模板':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                if subType == '记录':
                    result = SetPlayerInfo(self, groupId, personId, infoStr)
                elif subType == '查看':
                    result = GetPlayerInfo(self, groupId, personId, nickName)
                elif subType == '完整':
                    result = GetPlayerInfoFull(self, groupId, personId, nickName)
                elif subType == '清除':
                    ClearPlayerInfo(self, groupId, personId)
                    result = f'成功删除了{nickName}的角色卡~'
                elif subType == '模板':
                    result = PC_SHEET_TEMPLATE
            
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.CHECK:
            self.dailyInfoDict['checkCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                itemArgs = command.cArg[0].split('#')
                if len(itemArgs) == 1:
                    item = itemArgs[0]
                    times = 1
                else:
                    try:
                        times = int(itemArgs[0])
                        assert times <= 10 and times >= 1
                    except:
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '重复的次数必须在1~9之间哦~')]
                        times = None
                    item = itemArgs[1]

                if times:
                    diceCommand = command.cArg[1]
                    reason = command.cArg[2]
                    error, result = PlayerCheck(self, groupId, personId, item, times, diceCommand, nickName)
                    if error == 0 and reason:
                        result = f'由于{reason}, {result}'
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.TeamCheck:
            self.dailyInfoDict['checkCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                valid = False
                try:
                    teamName = self.teamInfoDict[groupId]['name']
                    membersList = self.teamInfoDict[groupId]['members']
                    assert len(membersList) >= 1
                    valid = True
                except:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '必须先加入队伍哦~')]
                if valid:
                    item = command.cArg[0]
                    diceCommand = command.cArg[1]
                    reason = command.cArg[2]
                    times = 1

                    finalResult = f'{teamName}进行队伍{item}检定'
                    if reason:
                        finalResult = f'由于{reason}, {finalResult}'
                    errorInfo = None
                    for memberId in membersList:
                        try:
                            nickName = self.nickNameDict[groupId][memberId]
                        except:
                            nickName = memberId
                        error, result = PlayerCheck(self, groupId, memberId, item, times, diceCommand, nickName)
                        if error != 0:
                            errorInfo = result
                            break
                        finalResult += f'\n{result}'

                    if errorInfo:
                        finalResult = errorInfo
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult)]

        elif cType == CommandType.SpellSlot:
            self.dailyInfoDict['slotCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                # Args: [subType, *args]
                subType = command.cArg[0]
                if subType == '记录':
                    error, result = SetSpellSlot(self, groupId, personId, command.cArg[1])
                elif subType == '查看':
                    result = nickName + ShowSpellSlot(self, groupId, personId)
                elif subType == '更改':
                    level = command.cArg[1]
                    try:
                        assert command.cArg[2][0] in ['+', '-']
                        adjVal = int(command.cArg[2])
                        assert adjVal > -10 and adjVal < 10
                    except:
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'{command.cArg[2]}是无效的法术位调整值~ 合法范围:[-9, +9]')]
                    result = nickName + ModifySpellSlot(self, groupId, personId, level, adjVal)
                elif subType == '清除':
                    result = ClearSpellSlot(self, groupId, personId)

                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.MONEY:
            self.dailyInfoDict['moneyCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                subType = command.cArg[0]
                if subType == '记录':
                    error, result = SetMoney(self, groupId, personId, command.cArg[1])
                elif subType == '清除':
                    result = ClearMoney(self, groupId, personId)
                elif subType == '更改':
                    result = nickName + ModifyMoney(self, groupId, personId, command.cArg[1])
                elif subType == '查看':
                    result = nickName + '当前的财富:' + ShowMoney(self, groupId, personId)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.TeamMoney:
            self.dailyInfoDict['moneyCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                valid = False
                try:
                    teamName = self.teamInfoDict[groupId]['name']
                    membersList = self.teamInfoDict[groupId]['members']
                    assert len(membersList) >= 1
                    valid = True
                except:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '必须先加入队伍哦~')]
                if valid:
                    modifier = command.cArg[0]
                    finalResult = f'{teamName}{modifier}:'
                    for memberId in membersList:
                        try:
                            nickName = self.nickNameDict[groupId][memberId]
                        except:
                            nickName = memberId
                        result = nickName + ModifyMoney(self, groupId, memberId, modifier)
                        finalResult += f'\n{result}'
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult)]


        elif cType == CommandType.NOTE:
            self.dailyInfoDict['noteCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                subType = command.cArg[0]
                if subType == '记录':
                    info = command.cArg[1].split(':', 1)
                    if len(info) == 1:
                        index = ''
                        content = info[0]
                    else:
                        index = info[0]
                        content = info[1]
                    result = self.__SetNote(groupId, index, content)
                elif subType == '清除':
                    index = command.cArg[1]
                    result = self.__ClearNote(groupId, index)
                elif subType == '查看':
                    index = command.cArg[1]
                    result = self.__ShowNote(groupId, index)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.TEAM:
            self.dailyInfoDict['teamCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                subType = command.cArg[0]
                if subType == '加入':
                    result = JoinTeam(self, groupId, personId, command.cArg[1])
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '清除':
                    result = ClearTeam(self, groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '查看':
                    result = ShowTeam(self, groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '点名':
                    result = CallTeam(self, groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '完整':
                    result = ShowTeamFull(self, groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result, personIdList=[personId]),
                            CommandResult(CoolqCommandType.MESSAGE, '已将队伍的完整信息私聊给你啦~')]

        elif cType == CommandType.REST:
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                subType = command.cArg[0]
                if subType == '长休':
                    result = LongRest(self, groupId, personId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, nickName+result)]

        elif cType == CommandType.SEND:
            commandWeight = 4
            if len(command.cArg[0]) < 10 or len(command.cArg[0])>100:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '请不要随便骚扰Master哦~ (信息长度限制为10~100)')]
            else:
                if groupId != 'Private':
                    message = f'来自群{groupId} 用户{personId}的信息: {command.cArg[0]}'
                else:
                    message = f'来自用户{personId}的信息: {command.cArg[0]}'
                feedback = '已将信息转发给Master了~'
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, message, personIdList=MASTER),
                        CommandResult(CoolqCommandType.MESSAGE, feedback)]

        elif cType == CommandType.Question:
            commandWeight = 4
            if not command.cArg[0]:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'当前可用的题库是: {list(self.questionDict.keys())}')]
            else:
                possKey = PairSubstring(command.cArg[0].strip(), self.questionDict.keys())
                if len(possKey) == 0:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'找不到这个题库哦~')]
                elif len(possKey) > 1:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'想找的是哪一个题库呢?\n{possKey}')]
                else:
                    result = self.__StartExam(possKey[0], personId, groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.WELCOME:
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有在群聊中才能使用该功能哦')]
            else:
                info = command.cArg[0].strip()
                groupInfoCur['welcome'] = info
                if info:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '已将入群欢迎词设为:\n'+info)]
                else:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '已经关闭入群欢迎')]

        elif cType == CommandType.NAME:
            temp = command.cArg[0].split('#')
            times = 1
            target = None
            try:
                assert len(temp) <= 2 and len(temp) >= 1
                if len(temp) == 1:
                    target = temp[0].strip()
                else:
                    times = int(temp[0])
                    target = temp[1].strip()
            except:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '输入的格式有些错误呢~')]
            if target != None:
                if times > 10 or times <= 0:
                    result = '生成的名字个数必须在1~10之间哦~'
                else:
                    result = GenerateName(self.nameInfoDict, target, times)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]


        elif cType == CommandType.JRRP:
            commandWeight = 2
            date = GetCurrentDateRaw()
            value = self.__GetJRRP(personId, date)
            if not userInfoCur['seenJRRP']:
                userInfoCur['seenJRRP'] = True
                self.dailyInfoDict['jrrpCommand'] += 1
                answer = f'{nickName}今天走运的概率是{value}%'
                if value >= 80:
                    answer += ', 今天运气不错哦~'
                elif value <= 20:
                    gift = GIFT_LIST[np.random.randint(0,len(GIFT_LIST))]
                    answer += f', 今天跑团的时候小心点... 给你{gift}作为防身道具吧~'
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, answer)]
            else:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'不是已经问过了嘛~ 你走运的概率是{value}%, 记好了哦!')]

        elif cType == CommandType.DND:
            commandWeight = 3
            try:
                times = int(command.cArg[0])
                assert times > 0 and times <= 10
            except:
                times = 1
            reason = command.cArg[1]
            result = self.__DNDBuild(times)
            result = f'{nickName}的初始属性: {reason}\n{result}'
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.QUERY:
            self.dailyInfoDict['queryCommand'] += 1
            commandWeight = 3
            targetStr = str(command.cArg[0])
            queryResult = self.__QueryInfo(targetStr, personId, groupId)
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, queryResult)]

        elif cType == CommandType.INDEX:
            self.dailyInfoDict['queryCommand'] += 1
            commandWeight = 3
            targetStr = str(command.cArg[0])
            queryResult = self.__IndexInfo(targetStr, personId, groupId)
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, queryResult)]

        elif cType == CommandType.DRAW:
            self.dailyInfoDict['drawCommand'] += 1
            commandWeight = 3
            args = str(command.cArg[0]).split('#')
            if len(args) == 1:
                targetStr = args[0]
                timesStr = '1'
            elif len(args) == 0:
                targetStr = ''
                timesStr = '1'
            else:
                targetStr = args[1]
                timesStr = args[0]
            drawResult = self.__DrawInfo(targetStr, timesStr)
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, drawResult)]

        elif cType == CommandType.COOK:
            self.dailyInfoDict['cookCommand'] += 1
            commandWeight = 4
            cookAdj = command.cArg[0]
            keywordList = command.cArg[1]
            error, cookResult = self.__CookCheck(cookAdj, keywordList)
            if error == -1:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, cookResult)]
            else:
                cookResult = f'{nickName}的烹饪结果是:\n{cookResult}'
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, cookResult)]

        elif cType == CommandType.ORDER:
            self.dailyInfoDict['cookCommand'] += 1
            commandWeight = 4
            number = command.cArg[0]
            keywordList = command.cArg[1]
            error, orderResult = self.__OrderDish(number, keywordList)
            if error == -1:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, orderResult)]
            else:
                orderResult = f'{nickName}的菜单:\n{orderResult}'
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, orderResult)]

        elif cType == CommandType.TodayMenu:
            if not userInfoCur['seenJRCD']:
                userInfoCur['seenJRCD'] = True
                self.dailyInfoDict['cookCommand'] += 1
                commandWeight = 4
                date = GetCurrentDateRaw()
                result = self.__GetTodayMenu(personId, date)
                result = f'{nickName}的{result}'
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result, personIdList = [personId])]
            else:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '每天只有一次机会哦~')]

        elif cType == CommandType.TodayJoke:
            flag = ''
            if True:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '今日笑话功能将在收到足够数量的投稿后恢复~敬请期待吧~')]
            else:
                if command.cArg[0] == 0 and userInfoCur['seenJoke'][1] != 0:
                    flag = '今'
                    userInfoCur['seenJoke'][1] = 0
                elif command.cArg[0] == -1 and userInfoCur['seenJoke'][0] != 0:
                    flag = '昨'
                    userInfoCur['seenJoke'][0] = 0
                elif command.cArg[0] == 1 and userInfoCur['seenJoke'][2] != 0:
                    flag = '明'
                    userInfoCur['seenJoke'][2] = 0
                if flag:
                    self.dailyInfoDict['jokeCommand'] += 1
                    commandWeight = 2
                    date = GetCurrentDateRaw() + command.cArg[0] * datetime.timedelta(days = 1)
                    result = self.__GetTodayJoke(personId, date)
                    result = f'{nickName}的{flag}日随机TRPG笑话:\n{result}'
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                else:
                    if command.cArg[0] == -1:
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有一次机会哦~昨天的今日笑话就是今天的昨日笑话, 你已经看过啦~')]
                    elif command.cArg[0] == 0:
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有一次机会哦~昨天的明日笑话就是今天的今日笑话, 你已经看过啦~')]
                    elif command.cArg[0] == 1:
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有一次机会哦~你已经提前把明天的笑话看过啦~')]

        elif cType == CommandType.CREDIT:
            if userInfoCur['seenCredit']:
                result = '哎~今天已经问过了呀~'
            else:
                try:
                    credit = userInfoCur['credit']
                    level = 0
                    for i in CREDIT_LEVEL_FEED.keys():
                        if credit >= i and i > level:
                            level = i
                    result = RandomSelectList(CREDIT_LEVEL_FEED[level])[0]
                    result = result.format(name=nickName)
                    result = InsertEmotion(result, self.emotionDict)
                    userInfoCur['seenCredit'] = True
                except:
                    result = '啊咧, 遇到一点问题, 请汇报给Master~'
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.MASTER:
            if personId not in MASTER:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '只有Master才能使用这个命令!')]
            else:
                subType = command.cArg[0]
                if subType == 'savedata':
                    await self.UpdateLocalData()
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '成功将所有资料保存到本地咯~')]
                elif subType == 'credit':
                    try:
                        commandArgs = command.cArg[1].split(':')
                        targetId = commandArgs[0].strip()
                        if len(commandArgs) > 1: # 修改
                            value = int(commandArgs[1])
                            self.userInfoDict[targetId]['credit'] += value
                            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'{targetId}的好感度{int2str(value)}, 现在是{self.userInfoDict[targetId]["credit"]}'),
                                                  CommandResult(CoolqCommandType.MESSAGE, f'对你的好感度{int2str(value)}, 现在是{self.userInfoDict[targetId]["credit"]}',
                                                   personIdList=[targetId])]
                        else: # 查看
                            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'{targetId}的好感度是{self.userInfoDict[targetId]["credit"]}')]
                    except Exception as e:
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'好感度调整失败, 原因是:\n{e}')]
                elif subType == 'notice':
                    for gId in self.groupInfoDict.keys():
                        self.groupInfoDict[gId]['noticeBool'] = True
                        self.groupInfoDict[gId]['noticeStr'] = command.cArg[1]
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'通知已成功设置, 内容是:\n{command.cArg[1]}')]
                elif subType == 'daily':
                    result = f'日期:{self.dailyInfoDict["date"]}\n'
                    result += f'全部指令:{self.dailyInfoDict["totalCommand"]}\n投骰指令:{self.dailyInfoDict["rollCommand"]}\n'
                    result += f'先攻指令:{self.dailyInfoDict["initCommand"]}\n人品指令:{self.dailyInfoDict["jrrpCommand"]}\n'
                    result += f'笑话指令:{self.dailyInfoDict["jokeCommand"]}\n查询指令:{self.dailyInfoDict["queryCommand"]} '
                    result += f'成功:{self.dailyInfoDict["querySucc"]} 失败:{self.dailyInfoDict["queryFail"]} 多结果:{self.dailyInfoDict["queryMult"]}\n'
                    result += f'抽卡指令:{self.dailyInfoDict["drawCommand"]}\n角色卡指令:{self.dailyInfoDict["pcCommand"]}\n'
                    result += f'金钱指令:{self.dailyInfoDict["moneyCommand"]}\n生命值指令:{self.dailyInfoDict["hpCommand"]}\n'
                    result += f'检定指令:{self.dailyInfoDict["checkCommand"]}\n法术位指令:{self.dailyInfoDict["slotCommand"]}\n'
                    result += f'烹饪指令:{self.dailyInfoDict["cookCommand"]}\n'
                    result += f'笔记指令:{self.dailyInfoDict["noteCommand"]}\n'
                    result += f'交互指令:{self.dailyInfoDict["IACommand"]}'
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        return commandResultList, commandWeight

    async def ValidateGroupInvite(self, groupId, inviterId) -> bool:
        try:
            assert self.userInfoDict[inviterId]['credit'] >= 0
            CreateNewGroupInfo(self.groupInfoDict, groupId)
            self.groupInfoDict[groupId]['inviter'] = inviterId
            return True
        except:
            return False
        
    def RegisterIACommand(self, personId, groupId, funcName, argsList, IAType = -1, expireTime = IA_EXPIRE_TIME, expireWarning = '', isRepeat = False):
        # 查找已有的同类交互指令并删除
        for i in range(len(self.userInfoDict[personId]['IACommand'])-1, -1, -1):
            if self.userInfoDict[personId]['IACommand'][i]['groupId'] == groupId and self.userInfoDict[personId]['IACommand'][i]['IAType'] == IAType:
                self.userInfoDict[personId]['IACommand'].pop(i)
                break

        if len(self.userInfoDict[personId]['IACommand']) >= IA_LIMIT_NUM:
            self.userInfoDict[personId]['IACommand'].pop(0)
        
        info = {}
        info['name'] = funcName
        info['date'] = Datetime2Str(GetCurrentDateRaw()+expireTime)
        info['personId'] = personId
        info['groupId'] = groupId
        info['args'] = argsList
        info['IAType'] = IAType
        info['warning'] = expireWarning
        info['isRepeat'] = isRepeat
        info['isValid'] = True
        self.userInfoDict[personId]['IACommand'].append(info)

    def UpdateNickName(self, groupId, personId, nickName) -> str:
        try:
            assert type(self.nickNameDict[groupId]) == dict
        except:
            self.nickNameDict[groupId] = {}

        if nickName: # 如果指定了昵称, 则更新昵称
            imposterList = []
            for strCur in NAME2TITLE.keys():
                if nickName.find(strCur) != -1:
                    imposterList.append(strCur)
            if imposterList:
                return f'{imposterList[0]}是{NAME2TITLE[imposterList[0]]}哦~请换个名字吧!'
            self.nickNameDict[groupId][personId] = nickName
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

            return f'要称呼你为{nickName}吗? 没问题!'
        else: # 否则移除原有的昵称
            try:
                del self.nickNameDict[groupId][personId]
            except:
                pass
            return '要用本来的名字称呼你吗? 了解!'

    def __SetNote(self, groupId, index, content) -> str:
        try:
            currentGroupInfo = self.groupInfoDict[groupId]
        except:
            return '未知的错误发生了:群信息不存在'
        if content[0] == '+':
            try:
                newContent = currentGroupInfo['note'][index]+'。'+content[1:]
            except:
                newContent = content[1:]
            content = newContent
        if not index:
            index = '临时记录'
        if len(currentGroupInfo['note']) > 20:
            return f'一个群里最多只允许20条笔记哦~'
        if len(content) > 300:
            return '呜...记不住啦~ 超过三百个字的内容就不要记到笔记上了吧...'
        totalWords = 0
        for k in currentGroupInfo['note'].keys():
            totalWords += len(currentGroupInfo['note'][k])
        if totalWords + len(content) > 1000:
            return f'呜...记不住啦~ 一个群的笔记总共最多只能保存一千个字哦~'
        currentGroupInfo['note'][index] = content
        return f'记下来咯~ 索引是"{index}"'

    def __ClearNote(self, groupId, index) -> str:
        try:
            currentGroupInfo = self.groupInfoDict[groupId]
        except:
            return '未知的错误发生了:群信息不存在'

        if not index:
            index = '临时记录'
        if index == '所有笔记':
            currentGroupInfo['note'] = {}
            return '成功删除所有笔记~'
        else:
            if not index in currentGroupInfo['note'].keys():
                resList = PairSubstring(index, currentGroupInfo['note'].keys())
                if len(resList) == 1:
                    index = resList[0]
                elif len(resList) > 1:
                    return f'可能的笔记索引:{resList}'
                else:
                    return f'无法找到相应的笔记索引'
            del currentGroupInfo['note'][index]
            return f'成功删除索引为{index}的笔记~'

    def __ShowNote(self, groupId, index) -> str:
        try:
            currentGroupInfo = self.groupInfoDict[groupId]
        except:
            return '未知的错误发生了:群信息不存在'

        result = ''
        if not index:
            result = '所有笔记:\n'
            for k in currentGroupInfo['note'].keys():
                result += f'{k}:{currentGroupInfo["note"][k]}\n'
            result = result[:-1]
        else:
            if not index in currentGroupInfo['note'].keys():
                resList = PairSubstring(index, currentGroupInfo['note'].keys())
                if len(resList) == 1:
                    index = resList[0]
                elif len(resList) > 1:
                    return f'可能的笔记索引:{resList}'
                else:
                    return f'无法找到相应的笔记索引'
            result = f'{index}:{currentGroupInfo["note"][index]}\n'
        return result


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
   
    def JoinInitList(self, groupId, personId, name, initAdj, isPC) -> str:
        try: #查找已存在的先攻信息
            initInfo = self.initInfoDict[groupId]
        except: #如未找到, 就创建一个新的先攻信息
            initInfo = {'date': GetCurrentDateStr(), 'initList':{}}

        if initAdj.find('抗性') != -1 or initAdj.find('易伤') != -1:
            return '抗性与易伤关键字不能出现在此处!'
            
        #initAdj 有两种情况, 一是调整值, 二是固定值
        if not initAdj or initAdj[0] in ['+','-'] or initAdj[:2] in ['优势','劣势']: #通过符号判断
            error, resultStr, rollResult = RollDiceCommand('d20'+initAdj)
        else:
            error, resultStr, rollResult = RollDiceCommand(initAdj)
        if error: return resultStr
        initResult = rollResult.totalValueList[0]
            
        hp, maxhp = (0, 0)
        name = name.lower()
        flag = True
        # 处理重复投先攻的情况
        if not isPC and name.find('#') != -1:
            index = name.find('#')
            if isDiceCommand(name[:index]):
                error, resultStrMulti, rollResultMulti = RollDiceCommand(name[:index])
                try:
                    assert error == 0, f'对象次数投骰时出现错误:{resultStrMulti}'
                    number = rollResultMulti.totalValueList[0]
                    assert number <= 10, '重复次数超过10次!'
                    first = ord('a')
                    nameListStr = ''
                    for n in range(number):
                        nameMulti = name[index+1:] + chr(first+n)
                        nameListStr += nameMulti + ' '
                        initInfo['initList'][nameMulti] = {'id':personId, 'init':initResult, 'hp':hp, 'maxhp':maxhp, 'alive':True, 'isPC':isPC}
                    result = f'{nameListStr.strip()}先攻:{resultStr}'
                    flag = False
                except Exception as e:
                    flag = False
                    result = f'关于{name}的先攻指令不正确:{e}'
        if flag:
            initInfo['initList'][name] = {'id':personId, 'init':initResult, 'hp':hp, 'maxhp':maxhp, 'alive':True, 'isPC':isPC}
            result = f'{name}先攻:{resultStr}'
        try:
            if GetCurrentDateRaw() - Str2Datetime(initInfo['date']) > datetime.timedelta(hours=1):
                result += '\n先攻列表上一次更新是一小时以前, 请注意~'
            initInfo['date'] = GetCurrentDateStr()
        except:
            pass
        self.initInfoDict[groupId] = initInfo
        return result

    def __CookCheck(self, cookAdj, keywordList)->(int, str):
        #第一个返回值是执行状况, -1为异常, 0为正常
        result = ''
        #cookAdj 有两种情况, 一是调整值, 二是固定值
        if not cookAdj or cookAdj[0] in ['+','-'] or cookAdj[:2] in ['优势','劣势']: #通过符号判断
            error, resultStr, rollResult = RollDiceCommand('d20'+cookAdj)
        else:
            error, resultStr, rollResult = RollDiceCommand(cookAdj)
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
            error, resultStr, rollResult = RollDiceCommand(numberStr)
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
    def __DNDBuild(self, times) -> str:        
        result = ''
        for i in range(times):
            error, resultStr, rollResult = RollDiceCommand(f'6#4d6k3')
            result += f'力量:{rollResult.rawResultList[0][0]}  敏捷:{rollResult.rawResultList[1][0]}  体质:{rollResult.rawResultList[2][0]}  '
            result += f'智力:{rollResult.rawResultList[3][0]}  感知:{rollResult.rawResultList[4][0]}  魅力:{rollResult.rawResultList[5][0]}'
            result += f'  共计:{sum(rollResult.totalValueList)}'
            if i != (times-1) and times != 1:
                result += '\n'
        return result

    @TypeAssert(targetStr = str)
    def __QueryInfo(self, targetStr, personId, groupId) -> str:
        if not self.queryInfoDict:
            return '呃啊, 记忆好像不见了... 怎么办...'
        
        if not targetStr:
            return f'现在的记忆中共有{len(self.queryInfoDict)}个条目呢, 可查询内容请输入 .help查询 查看'

        try:
            result = self.queryInfoDict[targetStr]
            self.dailyInfoDict['querySucc'] += 1
            return result
        except:
            # 尝试替换同义词
            if targetStr in self.querySynDict.keys():
                targetStr = self.querySynDict[targetStr]
                result = self.queryInfoDict[targetStr]
                self.dailyInfoDict['querySucc'] += 1
                return result

            # 无法直接找到结果, 尝试搜索
            keywordList = [k for k in targetStr.split('/') if k]
            if len(keywordList) > 5:
                return f'指定的关键词太多咯'
            possResult = PairSubstringList(keywordList, self.queryInfoDict.keys())

            if len(possResult) > 1:
                result = ''
                for i in range(min(len(possResult), QUERY_SHOW_LIMIT)):
                    result += f'{i+1}.{possResult[i]} '
                if len(possResult) <= QUERY_SHOW_LIMIT:
                    result = f'找到多个匹配的条目: {result[:-1]}\n回复序号可直接查询对应内容'
                else:
                    result = f'找到多个匹配的条目: {result[:-1]}等, 共{len(possResult)}个条目\n回复序号可直接查询对应内容'
                self.dailyInfoDict['queryMult'] += 1
                self.RegisterIACommand(personId, groupId, 'IA_QueryInfoWithIndex', [targetStr], 0, isRepeat = True)
                return result
            elif len(possResult) == 1:
                result = str(self.queryInfoDict[possResult[0]])
                result = f'要找的是{possResult[0]}吗?\n{result}'
                self.dailyInfoDict['querySucc'] += 1
                return result
            else:
                self.dailyInfoDict['queryFail'] += 1
                return '唔...找不到呢...'

    def IA_QueryInfoWithIndex(self, IAInfo, index) -> str:
        targetStr = IAInfo['args'][0]
        try:
            index = int(index)
            assert index > 0 and index <= QUERY_SHOW_LIMIT
        except:
            return None
        keywordList = [k for k in targetStr.split('/') if k]
        possResult = PairSubstringList(keywordList, self.queryInfoDict.keys())
        try:
            assert index <= len(possResult)
            return self.queryInfoDict[possResult[index-1]]
        except:
            return None


    @TypeAssert(targetStr = str)
    def __IndexInfo(self, targetStr, personId, groupId) -> str:
        if not self.queryInfoDict:
            return '呃啊, 记忆好像不见了... 怎么办...'
        
        if not targetStr:
            return f'现在的记忆中共有{len(self.queryInfoDict)}个条目呢, 可查询内容请输入 .help查询 查看'

        possResult = []
        keywordList = [k for k in targetStr.split('/') if k]
        if len(keywordList) > 5:
            return f'指定的关键词太多咯'

        # 开始索引
        for item in self.queryInfoDict:
            valid = True
            itemInfo = item.lower() + self.queryInfoDict[item].lower()
            for k in keywordList:
                if not k in itemInfo:
                    valid = False
                    break
            if valid:
                possResult.append(item)
        if len(possResult) == 0:
            return f'资料库中找不到任何含有关键字{keywordList}的词条呢~'
        elif len(possResult) == 1:
            return f'要找的是{possResult[0]}吗?\n{self.queryInfoDict[possResult[0]]}'
        else:
            result = ''
            for i in range(min(len(possResult), QUERY_SHOW_LIMIT)):
                result += f'{i+1}.{possResult[i]} '
            if len(possResult) <= QUERY_SHOW_LIMIT:
                result = f'以下词条含有关键字{keywordList}:\n{result[:-1]}\n回复序号可直接查询对应内容'
            else:
                result = f'以下词条含有关键字{keywordList}:\n{result[:-1]}等, 共{len(possResult)}个条目\n回复序号可直接查询对应内容'
            self.RegisterIACommand(personId, groupId, 'IA_IndexInfoWithIndex', [targetStr], 0, isRepeat = True)
            return result

    def IA_IndexInfoWithIndex(self, IAInfo, index) -> str:
        targetStr = IAInfo['args'][0]
        try:
            index = int(index)
            assert index > 0 and index <= QUERY_SHOW_LIMIT
        except:
            return None
        keywordList = [k for k in targetStr.split('/') if k]
        possResult = []
        # 开始索引
        for item in self.queryInfoDict:
            valid = True
            itemInfo = item.lower() + self.queryInfoDict[item].lower()
            for k in keywordList:
                if not k in itemInfo:
                    valid = False
                    break
            if valid:
                possResult.append(item)
        try:
            assert index <= len(possResult)
            return self.queryInfoDict[possResult[index-1]]
        except:
            return None

    @TypeAssert(targetStr = str)
    def __DrawInfo(self, targetStr, timesStr = '1') -> str:
        if not self.deckDict:
            return '呃啊, 记忆好像不见了... 怎么办...'
        if not targetStr:
            return f'现在的记忆中共有{len(self.deckDict)}个牌堆呢, 分别是{list(self.deckDict.keys())}'

        try:
            times = int(timesStr)
            assert times >= 1
            assert times <= 10
        except:
            return f'抽取的数量必须为1到10之间的整数~'

        try:
            targetDeck = self.deckDict[targetStr]
            result = DrawFromDeck(targetDeck, self.deckDict, times = times)
            result = f'从{targetStr}中抽取的结果: \n{result}'
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
                result = DrawFromDeck(self.deckDict[possResult[0]], self.deckDict, times = times)
                result = f'从{possResult[0]}中抽取的结果:\n{result}'
                return result
            else:
                return '唔...找不到呢...'

    def __StartExam(self, examKey, personId, groupId, questionNum = 10) -> str:
        if not examKey in self.questionDict.keys():
            return f'{examKey}不是可用的题库!'

        size = len(self.questionDict[examKey])
        questionNum = min(size, questionNum)
        questionIndexList = np.random.permutation(size)[:questionNum].tolist()
        examState = [0,0,0] # 当前序号, 正确, 错误数量
        self.RegisterIACommand(personId, groupId, 'IA_AnserQuestion', [examKey, questionIndexList, examState], 1, datetime.timedelta(seconds = 120), '时间到咯, 请你重新开始吧~')
        result = f'{examKey}考试开始啦, 下面是从{size}道题中为你随机选择的{questionNum}道题~\n'
        result += '判断题输入T/F 或 Y/N回答, 选择题请输入序号。答案是大小写都可以\n每道题只有2分钟的有效时间, 错过了就请重新开始吧~\n'
        result += '输入Q即可中止考试\n'
        result += f'听好咯, 第一道题目是:\n{self.questionDict[examKey][questionIndexList[0]][0]}'
        return result

    def IA_AnserQuestion(self, IAInfo, answer) -> str:
        personId = IAInfo['personId']
        groupId = IAInfo['groupId']
        examKey, questionIndexList, examState = IAInfo['args']
        questionInfo = self.questionDict[examKey][questionIndexList[examState[0]]]
        answer = answer.strip().upper()
        if answer == 'Q':
            return f'那么考试就到这里咯~ 你总共答对了{examState[1]}道题, 答错了{examState[2]}道题'
        groundTruth = questionInfo[1]
        explaination = questionInfo[2]
        isCorrect = False
        if groundTruth == 'T' or groundTruth == 'F':
            if groundTruth == 'T' and (answer == 'T' or answer == 'Y'):
                isCorrect = True
            elif groundTruth == 'F' and (answer == 'F' or answer == 'N'):
                isCorrect = True
        elif groundTruth == answer:
            isCorrect = True
        result = ''
        if isCorrect:
            result += '回答正确~\n'
            examState[1] += 1
        else:
            result += f'回答错误~ 答案是{groundTruth}\n'
            examState[2] += 1
        if explaination:
            result += f'解析: {explaination}\n\n'

        examState[0] += 1
        if examState[0] < len(questionIndexList):
            self.RegisterIACommand(personId, groupId, 'IA_AnserQuestion', [examKey, questionIndexList, examState], 1, datetime.timedelta(seconds = 120), '时间到咯, 请你重新开始吧~')
            result += f'下一道题来咯!\n第{examState[0]+1}题:{self.questionDict[examKey][questionIndexList[examState[0]]][0]}'
        else:
            result += f'考试结束咯, 你答对了{len(questionIndexList)}道题中的{examState[1]}道, 正确率为{100*examState[1]/len(questionIndexList)}%~'
        return result

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

    def __GetTodayJoke(self, personId, date) -> str:
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
            assert self.jokeDict
        except:
            return '笑话资料库加载失败了呢...'

        wordSize = len(self.jokeDict['word'])
        imgSize = len(self.jokeDict['img'])
        index = np.random.randint(wordSize+imgSize)
        if index < wordSize or IS_COOLQ_PRO == False:
            jokeCur = RandomSelectList(self.jokeDict['word'], 1)[0]
        else:
            index = index - wordSize
            fileName = self.jokeDict['img'][index]
            absPath = os.path.join(LOCAL_JOKEIMG_DIR_PATH, fileName)
            jokeCur = f'[CQ:image,file=file:///{absPath}]'
        return jokeCur

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
        elif subType == '交互':
            return HELP_IA_STR
        elif subType == 'r':
            return HELP_COMMAND_R_STR
        elif subType == 'nn':
            return HELP_COMMAND_NN_STR
        elif subType == 'ri':
            return HELP_COMMAND_RI_STR
        elif subType == 'dnd':
            return HELP_COMMAND_DND_STR
        elif subType == 'init':
            return HELP_COMMAND_INIT_STR
        elif subType == 'welcome':
            return HELP_COMMAND_WELCOME_STR
        elif subType == 'name':
            return HELP_COMMAND_NAME_STR
        elif subType == '查询':
            return HELP_COMMAND_QUERY_STR
        elif subType == 'hp':
            return HELP_COMMAND_HP_STR
        elif '法术位' in subType:
            return HELP_COMMAND_SpellSlot_STR
        elif '金钱' in subType:
            return HELP_COMMAND_Money_STR
        elif subType == '长休':
            return HELP_COMMAND_LONGREST_STR
        elif subType == '笔记':
            return HELP_COMMAND_NOTE_STR
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
        elif subType == '答题':
            return HELP_COMMAND_QUESTION_STR
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

    def GetWelcome(self, groupId) -> str:
        result = ''
        try:
            groupId = str(groupId)
            result = self.groupInfoDict[groupId]['welcome']
        except Exception as e:
            print(e)
        return result



def DrawFromDeck(deck, allDeck, deep=1, times = 1) -> str:
    result = ''
    if times < 1:
        return '抽卡次数不能为0'
    if times > 10:
        return '抽卡上限为10'
    if deep > 5:
        return '达到迭代上限: 5'
    for t in range(times):
        for d in range(deep):
            result += '  '
        if times != 1:
            result += f'\n第{t+1}次:'
        randWeight = np.random.randint(deck['totalWeight'])+1
        selectedItem = None
        for item in deck['list']:
            randWeight -= item['weight']
            if randWeight <= 0:
                selectedItem = item
                break
        if not selectedItem:
            return f'未知的错误发生了: 权重总值不正确'
        for c in item['content']:
            if c[0] == 'TEXT':
                result += c[1]
            elif c[0] == 'ROLL':
                error, resultStr, rollResult = RollDiceCommand(c[1])
                if error: # 不应该发生的情况
                    return f'牌堆信息存在错误: 投骰表达式不正确 {resultStr} raw:{selectedItem["raw"]}'
                result += resultStr
            elif c[0] == 'DRAW':
                args = c[1].split('/')
                target = args[0]
                try:
                    drawTimes = args[1]
                    error, resultStr, rollResult = RollDiceCommand(drawTimes)
                    assert error == 0
                    drawTimes = rollResult.totalValueList[0]
                    timeStr = resultStr + '次\n'
                except:
                    timeStr = ''
                    drawTimes = 1
                newResult = DrawFromDeck(allDeck[target], allDeck, deep+1, drawTimes)
                result += f'抽取{target} {timeStr}{newResult}\n'
            else: # 不应该发生的情况
                return f'该段信息存在错误: 关键词错误 {c} raw:{selectedItem["raw"]}'

        if selectedItem['end']:
            result += '\n抽取终止'
            break
    return result.strip()

def GenerateName(nameInfoDict, target, times):
    if not nameInfoDict:
        return '姓名资料库加载失败...'
    if not target:
        return f'当前可选的姓名有:{list(nameInfoDict["meta"].keys())}'
    if not target in nameInfoDict['meta'].keys():
        targetList = target.split('/')
        possTarget = PairSubstringList(targetList, nameInfoDict['meta'].keys())
        if len(possTarget) == 0:
            return f'无法找到与{target}相关的姓名库~'
        elif len(possTarget) > 1:
            return f'找到多个相关的姓名库: {possTarget}'
        else:
            target = possTarget[0]

    # 正式开始生成
    result = f'随机{target}姓名:'
    for i in range(times):
        detailInfo = RandomSelectList(nameInfoDict['meta'][target])[0] # 示例: ['达马拉人', 0, 2]
        chinesePart = ''
        englishPart = ''
        for i in range(1, len(detailInfo)):
            tempInfo = RandomSelectList(nameInfoDict['info'][detailInfo[0]][detailInfo[i]])[0]
            englishPart += tempInfo[0] + '·'
            chinesePart += tempInfo[1] + '·'
        result += f'\n{chinesePart[:-1]} ({englishPart[:-1]})'
    return result
        

def CreateNewUserInfo(userDict, personId):
    userDict[personId] = copy.deepcopy(userInfoTemp)

def CreateNewGroupInfo(groupDict, groupId):
    groupDict[groupId] = copy.deepcopy(groupInfoTemp)

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

        userDict[userId] = copy.deepcopy(userInfoCur)

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

        for curK in groupInfoCur.keys():
            if not curK in groupInfoTemp.keys():
                deletedList.append((groupId, curK))

        for k in groupInfoTemp.keys():
            if not k in groupInfoCur.keys():
                groupInfoCur[k] = groupInfoTemp[k]

        groupDict[groupId] = copy.deepcopy(groupInfoCur)

    for pair in deletedList:
        del groupDict[pair[0]][pair[1]]

    for groupId in deletedGroupList:
        del groupDict[groupId]

def UpdateDailyInfoDict(dailyDict):
    try:
        assert (GetCurrentDateRaw() - Str2Datetime(dailyDict['date'])) < datetime.timedelta(days=1)
        for k in dailyDict.keys():
            assert k in dailyInfoTemp.keys()
    except:
        dailyDict = copy.deepcopy(dailyInfoTemp)
        dailyDict['date'] = GetCurrentDateStr()
    for k in dailyInfoTemp.keys():
        if not k in dailyDict.keys():
            dailyDict[k] = copy.deepcopy(dailyInfoTemp[k])
    return dailyDict

def DetectSpam(currentDate, lastDateStr, accuNum, weight = 1) -> (bool, str, int):
    lastDate = Str2Datetime(lastDateStr)
    if currentDate - lastDate > MESSAGE_LIMIT_TIME:
        return False, Datetime2Str(currentDate), 0
    else:
        if accuNum + weight < MESSAGE_LIMIT_NUM:
            return False, lastDateStr, accuNum+weight
        else:
            return True, lastDateStr, accuNum+weight