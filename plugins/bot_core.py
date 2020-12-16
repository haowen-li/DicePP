import collections
import copy

from typing import Any, Dict, Sequence, List

from tool_dice import RollDiceCommand, SplitDiceCommand, SplitNumberCommand, isDiceCommand
import tool_pc as tp
import tool_common as tc
import tool_battle as tb
import data_template as dt
from utils import *
from utils import UpdateJsonAsync
from custom_config import *
from info_help import *
from info_game import *
from info_chat import *


async def ParseInput(inputStr):
    # 接受用户的输入, 输出一个Command类实例, 包含指令类型与对应参数
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
    commandType = ''
    commandStrOri = ''
    # 从commandKeywordList中依次匹配命令
    for i in range(len(commandKeywordList)):
        commandKeyword = commandKeywordList[i]
        splitIndex = commandStr.find(commandKeyword)
        if splitIndex == 0:
            commandType = commandStr[:len(commandKeyword)]  # 类型
            commandStrOri = commandStr[len(commandKeyword):]
            commandStr = commandStrOri.strip()  # 参数
            findCommand = True
            break
    # 无法直接找到匹配的关键字则尝试使用正则表达式判定
    if not findCommand:
        for i in range(len(commandKeywordReList)):
            result = re.match(commandKeywordReList[i], commandStr)
            if result:
                index = result.span(0)[1]
                commandType = commandStr[:index].strip()  # 类型
                commandStrOri = commandStr[index:]
                commandStr = commandStrOri.strip()  # 参数
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
        return Command(CommandType.Roll, [diceCommand, reason, isHide, isShort])
    # 更改昵称命令
    elif commandType == 'nn':
        nickName = commandStr
        return Command(CommandType.NickName, [nickName])
    # 今日人品命令
    elif commandType == 'jrrp':
        return Command(CommandType.JRRP, [])
        # 先攻列表命令
    elif commandType == 'init':
        # commandStr 可能为 '', 'clr' 
        return Command(CommandType.INIT, [commandStr])
    elif commandType == 'ri':
        # 参数包含两部分, 骰子表达式(加值)与名称, 名称为可选项
        diceCommand, name = SplitDiceCommand(commandStrOri)
        return Command(CommandType.RI, [diceCommand, name])
    elif commandType == 'bot':
        if commandStr.find('on') != -1:
            return Command(CommandType.BOT, ['on'])
        elif commandStr.find('off') != -1:
            return Command(CommandType.BOT, ['off'])
        else:
            return Command(CommandType.BOT, ['show'])
    elif commandType == '群管理':
        if commandStr.find('启用功能') != -1:
            index = commandStr.find('启用功能')
            return Command(CommandType.GROUP, ['启用功能', commandStr[index + 4:].strip()])
        elif commandStr.find('禁用功能') != -1:
            index = commandStr.find('禁用功能')
            return Command(CommandType.GROUP, ['禁用功能', commandStr[index + 4:].strip()])
        elif commandStr.find('查看禁用功能') != -1:
            return Command(CommandType.GROUP, ['查看禁用功能'])
        elif commandStr.find('信息') != -1:
            return Command(CommandType.GROUP, ['信息'])
        else:
            return Command(CommandType.GROUP, ['帮助'])
    elif commandType == 'dnd':
        number, reason = SplitNumberCommand(commandStr)
        return Command(CommandType.DND, [number, reason])
    elif commandType == 'help':
        subType = commandStr.replace(' ', '')
        return Command(CommandType.HELP, [subType])
    elif commandType == 'send':
        return Command(CommandType.SEND, [commandStr])
    elif commandType == '查询':
        target = commandStr.replace(' ', '')
        return Command(CommandType.QUERY, [target])
    elif commandType == '索引':
        return Command(CommandType.INDEX, [commandStr])
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
    elif commandType == 'debug':
        return Command(CommandType.MASTER, ['debug', commandStr])
    elif commandType == '好感度':
        return Command(CommandType.CREDIT, [])
    elif 'hp' in commandType:
        commandStr = commandType[:commandType.find('hp')] + commandStr
        subType = None
        targetStr = None
        hpCommand = None
        commandStr = commandStr.strip()
        if len(commandStr) == 0:
            return Command(CommandType.HP, ['查看'])
        if commandStr == 'clr':
            return Command(CommandType.HP, ['清除'])
        # 是否显式指定了指令类型
        for i in range(len(commandStr)):
            if commandStr[i] in ['+', '-', '=']:
                subType = commandStr[i]
                targetStr = commandStr[:i].strip()
                hpCommand = commandStr[i + 1:].strip()
                break
        # 不指定指令类型则默认为'='
        if not subType:
            for i in range(len(commandStr)):
                if commandStr[i] in (['d'] + [str(n) for n in range(0, 10)]):
                    subType = '='
                    targetStr = commandStr[:i].strip()
                    hpCommand = commandStr[i:].strip()
                    break
        if not subType:
            return None
        splitIndex = hpCommand.rfind('/')
        if splitIndex != -1:
            hpStr = hpCommand[:splitIndex]
            maxhpStr = hpCommand[splitIndex + 1:]
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
            try:
                level = int(commandType[0])
            except ValueError:
                try:
                    level = ChineseNumberToInt(commandType[0])
                except ValueError:
                    return None
            return Command(CommandType.SpellSlot, ['更改', level, commandStr])
        elif commandType == '法术位' or commandType == '查看法术位':
            return Command(CommandType.SpellSlot, ['查看', commandStr])
    elif '环' in commandType:
        try:
            level = int(commandType[0])
            return Command(CommandType.SpellSlot, ['更改', level, commandStr])
        except ValueError:
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
        self.memberInfoDict = ReadJson(LOCAL_MEMBERINFO_PATH)
        self.masterInfoDict = ReadJson(LOCAL_MASTERINFO_PATH)

        UpdateAllGroupInfo(self)
        UpdateAllUserInfo(self)
        UpdateAllMemberInfo(self)
        UpdateMasterInfo(self)
        self.dailyInfoDict = UpdateDailyInfoDict(self.dailyInfoDict)

        print(f'个人资料库加载成功!')
        # 尝试加载查询资料库
        try:
            filesPath = os.listdir(LOCAL_QUERYINFO_DIR_PATH)  # 读取所有文件名
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
            filesPath = os.listdir(LOCAL_DECKINFO_DIR_PATH)  # 读取所有文件名
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
                    for relay in self.deckDict[deck]['relay']:
                        if relay not in self.deckDict.keys():
                            invalidDeck.append([deck, f'依赖的牌堆{relay}不存在'])
                            hasInvalid = True
                if hasInvalid:
                    for invalid in invalidDeck:
                        del self.deckDict[invalid[0]]
                        print(f'移除无效牌堆:{invalid[0]}, 原因是{invalid[1]}')
                    hasInvalid = False
                    hasCheck = False  # 需要重新检查依赖

            assert len(self.deckDict) > 0
            print(f'牌库加载成功! 共{len(self.deckDict)}个牌堆')
        except Exception as e:
            print(f'牌库加载失败! {e}')
            self.deckDict = None

        # 尝试加载菜谱资料库
        try:
            filesPath = os.listdir(LOCAL_MENUINFO_DIR_PATH)  # 读取所有文件名
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
                    assert len(dishName) < 50, '名称过长'
                    assert len(dishInfo['描述']) < 400, '描述过长'
                    assert -20 <= dishInfo['美味'] <= 40, '美味数值不正确'
                    assert -20 <= dishInfo['难度'] <= 40, '难度数值不正确'
                    assert len(dishInfo['价格']) < 50
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
                    print(f'菜谱{dishName}无效 {e}')
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
                if PLATFORM_NAME == 'DOCKER' or os.path.exists(absPath):  # 如果是Docker环境则无法直接检查有效性
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
            filesPath = os.listdir(LOCAL_EMOTINFO_DIR_PATH)
            for fp in filesPath:
                try:
                    name, suffix = fp.split('.')
                    assert suffix in ['jpg', 'png', 'gif']
                    absPath = os.path.join(LOCAL_EMOTIMG_DIR_PATH, fp)
                    if PLATFORM_NAME == 'DOCKER' or os.path.exists(absPath):  # 如果是Docker环境则无法直接检查有效性
                        self.emotionDict[name] = absPath
                except:
                    pass
            assert len(self.emotionDict) != 0
            print(f'表情包加载成功! 共{len(self.emotionDict)}个条目, 分别是{self.emotionDict.keys()}')
        except Exception as e:
            print(f'表情包加载失败!', e)
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
            print(
                f'题库加载成功! 共{len(self.questionDict)}个条目,'
                f' 分别是{[(k, len(self.questionDict[k])) for k in self.questionDict.keys()]}')
        except Exception as e:
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
        await UpdateJsonAsync(self.memberInfoDict, LOCAL_MEMBERINFO_PATH)
        await UpdateJsonAsync(self.masterInfoDict, LOCAL_MASTERINFO_PATH)

    async def UpdateGroupInfo(self, groupInfoDictUpdate):
        result = []
        invalidGroupId = []
        validGroupNum = 0
        newGroupNum = 0
        try:
            for gId in groupInfoDictUpdate.keys():
                if gId not in self.groupInfoDict.keys():
                    CreateNewGroupInfo(self.groupInfoDict, gId)
                    newGroupNum += 1

            for gId in self.groupInfoDict.keys():
                if not gId in groupInfoDictUpdate.keys():
                    invalidGroupId.append(gId)
                elif groupInfoDictUpdate[gId]:
                    validGroupNum += 1
                    self.groupInfoDict[gId]['name'] = groupInfoDictUpdate[gId]
            resultStr = f'检测到{validGroupNum}个有效群信息, 新增{newGroupNum}个群信息, {len(invalidGroupId)}个群没有找到群信息'
            result += [CommandResult(CoolqCommandType.MESSAGE, resultStr, personIdList=MASTER)]
            # if len(invalidGroupId) != 0:
            #     for gId in invalidGroupId:
            #         del self.groupInfoDict[gId]
            #     result += [CommandResult(CoolqCommandType.MESSAGE,
            #     f'已删除不存在群: {invalidGroupId}', personIdList = MASTER)]
        except Exception as e:
            result += [CommandResult(CoolqCommandType.MESSAGE, f'更新群信息时出现错误: {e}', personIdList=MASTER)]
        # # 清除无用信息
        # DeleteInvalidInfo(self.nickNameDict, self.groupInfoDict.keys())
        # DeleteInvalidInfo(self.initInfoDict, self.groupInfoDict.keys())
        # DeleteInvalidInfo(self.pcStateDict, self.groupInfoDict.keys())
        # DeleteInvalidInfo(self.teamInfoDict, self.groupInfoDict.keys())
        return result

    async def DailyUpdate(self, saveData=True):
        result = []
        errorList = []
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
                    liveUserNum += 1  # 统计用户
                if userInfoCur['dailyCredit'] >= DAILY_CREDIT_LIMIT:
                    activeUserNum += 1  # 统计活跃用户
                if userInfoCur['credit'] < 0:
                    userInfoCur['credit'] = min(0, userInfoCur['credit'] + 10)
                userInfoCur['dailyCredit'] = 0
                userInfoCur['commandDaily'] = 0
                userInfoCur['messageDaily'] = 0
                userInfoCur['dndCommandDaily'] = 0
                # 处理过期的IA交互信息
                for i in range(len(userInfoCur['IACommand']) - 1, -1, -1):
                    IAInfo = userInfoCur['IACommand'][i]
                    if Str2Datetime(IAInfo['date']) < GetCurrentDateRaw():
                        userInfoCur['IACommand'].pop(i)
                # 清除过久没有使用的用户 (不清除拉黑用户)
                lastTime = GetCurrentDateRaw() - Str2Datetime(userInfoCur['activeDate'])
                if lastTime >= datetime.timedelta(days=10) and userInfoCur['credit'] >= 0:
                    userInfoCur['credit'] -= 10
                    if userInfoCur['credit'] < 0:
                        invalidUser.append(pId)
            except Exception as e:
                errorList.append(f'\n处理用户{pId}时的异常:{e}')

        for pId in invalidUser:
            del self.userInfoDict[pId]

        warningGroup = []
        dismissGroup = []
        for gId in self.groupInfoDict.keys():
            try:
                groupInfoCur = self.groupInfoDict[gId]
                lastTime = GetCurrentDateRaw() - Str2Datetime(groupInfoCur['activeDate'])
                if lastTime >= datetime.timedelta(days=7):
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
                errorList.append(f'\n处理群{gId}时的异常:{e}')

        if warningGroup:
            result += [CommandResult(CoolqCommandType.MESSAGE, LEAVE_WARNING_STR, groupIdList=warningGroup)]
        if dismissGroup:
            result += [CommandResult(CoolqCommandType.DISMISS, LEAVE_NOTICE_STR, groupIdList=dismissGroup)]
            for gId in dismissGroup:
                del self.groupInfoDict[gId]

        # 更新日志信息
        try:
            self.dailyInfoDict = UpdateDailyInfoDict(self.dailyInfoDict)
        except Exception as e:
            errorList.append(f'\n更新日志时的异常:{e}')

        # 清除无用信息
        DeleteInvalidInfo(self.nickNameDict, self.groupInfoDict.keys())
        DeleteInvalidInfo(self.initInfoDict, self.groupInfoDict.keys())
        DeleteInvalidInfo(self.pcStateDict, self.groupInfoDict.keys())
        DeleteInvalidInfo(self.teamInfoDict, self.groupInfoDict.keys())
        DeleteInvalidInfo(self.memberInfoDict, self.groupInfoDict.keys())

        # 清除无效的群成员信息
        for gId in self.memberInfoDict.keys():
            try:
                memberInfoCur = self.memberInfoDict[gId]
                invalidMember = []
                for pId in memberInfoCur.keys():
                    if pId not in self.userInfoDict.keys():
                        invalidMember.append(pId)
                        continue
                    lastTime = GetCurrentDateRaw() - Str2Datetime(memberInfoCur[pId]['activeDate'])
                    if lastTime >= datetime.timedelta(days=30):  # 30天没有发言则彻底删除记录
                        invalidMember.append(pId)
                        continue
                    memberInfoCur[pId]['days'] += 1
                for pId in invalidMember:
                    del memberInfoCur[pId]
            except Exception as e:
                errorList.append(f'\n处理群成员{gId}时的异常:{e}')

        result += [CommandResult(CoolqCommandType.MESSAGE,
                                 f'成功更新今日数据 警告:{warningGroup} 退群:{dismissGroup}\n昨日发言用户:{liveUserNum} 活跃用户:{activeUserNum}',
                                 MASTER)]
        if errorList:
            result += [CommandResult(CoolqCommandType.MESSAGE, '异常信息:' + str(errorList[:10]), MASTER)]
        if saveData:
            await self.UpdateLocalData()
        return result

    async def ProcessMessage(self, inputStr, userId, personName, groupId=None, onlyToMe=False) -> List[CommandResult]:
        # 检查个人信息是否存在
        try:
            assert userId in self.userInfoDict.keys()
        except AssertionError:
            CreateNewUserInfo(self.userInfoDict, userId)
        userInfoCur = self.userInfoDict[userId]

        if groupId:  # 当是群聊信息时, 检查群聊信息是否存在
            try:
                assert groupId in self.groupInfoDict.keys()
            except AssertionError:
                CreateNewGroupInfo(self.groupInfoDict, groupId)
            groupInfoCur = self.groupInfoDict[groupId]
        else:
            groupInfoCur = None

        # 统计信息次数
        userInfoCur['messageAccu'] += 1
        userInfoCur['messageDaily'] += 1
        if groupId:
            groupInfoCur['messageAccu'] += 1
            groupInfoCur['messageDaily'] += 1

        # 更新群成员信息
        if groupId:
            try:
                assert groupId in self.memberInfoDict.keys()
            except AssertionError:
                CreateNewGroupMemberInfo(self.memberInfoDict, groupId)
            try:
                assert userId in self.memberInfoDict[groupId].keys()
            except AssertionError:
                CreateNewMemberInfo(self.memberInfoDict[groupId], userId)
            groupMemberInfo = self.memberInfoDict[groupId][userId]
            groupMemberInfo['activeDate'] = GetCurrentDateStr()
            groupMemberInfo['messageDaily'] += 1
            groupMemberInfo['messageAccu'] += 1

        # 黑名单检测
        if userInfoCur['credit'] < 0:
            return None
        if userInfoCur['warning'] >= 2 or userInfoCur['ban'] >= 3:
            return None
        # 检查激活状态
        if groupId:
            try:
                assert groupInfoCur['active']  # 已有记录且是激活状态并继续执行命令
            except (KeyError, AssertionError):
                if not groupInfoCur['active'] and not onlyToMe and inputStr.find(
                        'bot') == -1:  # 已有记录且是非激活状态, 且不是单独指令, 则不执行命令
                    return None

        # 检测彩蛋
        if groupId and userInfoCur['credit'] >= CHAT_CREDIT_LV0:
            diffTime = Str2Datetime(groupInfoCur['chatDate']) - GetCurrentDateRaw()
            resultList = None
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
                                resultList += [
                                    CommandResult(CoolqCommandType.MESSAGE, IAInfo['warning'], personIdList=[userId],
                                                  groupIdList=[groupId])]
                            else:
                                resultList += [
                                    CommandResult(CoolqCommandType.MESSAGE, IAInfo['warning'], personIdList=[userId])]
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
                if isSpam and userId not in MASTER:
                    userInfoCur['credit'] -= 100
                    userWarning = userInfoCur['warning']
                    if userWarning == 0:
                        resultList = [CommandResult(CoolqCommandType.MESSAGE, f'检测到{personName} {userId}的刷屏行为, 黄牌警告!')]
                    elif userWarning == 1:
                        resultList = [CommandResult(CoolqCommandType.MESSAGE, f'检测到{personName} {userId}的刷屏行为, 不理你了!')]
                        userInfoCur['ban'] += 1
                    userInfoCur['warning'] += 1
            except Exception as e:
                print(f'DetectSpam:{e}')
            return resultList

        # 检测命令(以.开头)
        command = await ParseInput(inputStr)
        if command is None:
            return None

        # 检查该指令是否被该群禁用
        if groupId:
            if str(int(command.cType)) in groupInfoCur['BanFunc'].keys():
                return [CommandResult(CoolqCommandType.MESSAGE, FUNC_BAN_NOTICE)]

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

        # 更新并尝试读取昵称
        self.userInfoDict[userId]['name'] = personName
        nickName = self.GetNickName(groupId, userId)

        try:
            resultList, commandWeight = await self.__ProcessInput(command, userId, nickName, userInfoCur, groupId,
                                                                  groupInfoCur, onlyToMe)
        except MasterError as e:
            if self.masterInfoDict['debug']:
                raise e
            resultList = [
                CommandResult(CoolqCommandType.MESSAGE, f'引起错误的输入:{inputStr}\n' + str(e), personIdList=MASTER)]
            commandWeight = 0
        except UserError as e:
            resultList = [CommandResult(CoolqCommandType.MESSAGE, str(e))]
            commandWeight = 3
        # 最后处理
        if len(resultList) == 0:
            return None

        # 刷屏检测
        try:
            isSpam, dateStr, accuNum = DetectSpam(GetCurrentDateRaw(),
                                                  userInfoCur['activeDate'], userInfoCur['spamAccu'], commandWeight)
            userInfoCur['activeDate'] = dateStr
            userInfoCur['spamAccu'] = accuNum
            if isSpam and userId not in MASTER:
                userInfoCur['credit'] -= 100
                userWarning = userInfoCur['warning']
                if userWarning == 0:
                    resultList = [CommandResult(CoolqCommandType.MESSAGE, f'检测到{nickName} {userId}的刷屏行为, 黄牌警告!')]
                elif userWarning == 1:
                    resultList = [CommandResult(CoolqCommandType.MESSAGE, f'检测到{nickName} {userId}的刷屏行为, 不理你了!')]
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
            result = re.match(keyRe, inputStr, flags=re.I)
            if result:
                possChatList.append(CHAT_COMMAND_COMMON[keyRe])
        if len(possChatList) != 0:
            possChatList = RandomSelectList(possChatList)[0]
            possChatList = [info[1] for info in possChatList if
                            credit >= info[0] and ((len(info)) != 3 or credit <= info[2])]
            if possChatList == 0:
                return None
            result = RandomSelectList(possChatList)[0]
            result = InsertEmotion(result, self.emotionDict)
            return [CommandResult(CoolqCommandType.MESSAGE, result)]

        for keyRe in CHAT_COMMAND_FUNCTION.keys():
            result = re.match(keyRe, inputStr, flags=re.I)
            if result:
                possChatList.append(CHAT_COMMAND_FUNCTION[keyRe])
        if len(possChatList) != 0:
            targetFun = RandomSelectList(possChatList)[0]
            result = targetFun(inputStr, credit)
            if result:
                return [CommandResult(CoolqCommandType.MESSAGE, result)]
        return None

    # 接受输入字符串，返回输出字符串
    async def __ProcessInput(self, command, userId, nickName, userInfoCur, groupId, groupInfoCur, onlyToMe) -> tuple:
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
            if isHide and groupId == 'Private':
                raise UserError(GROUP_COMMAND_ONLY_STR)
            if diceCommand == '':
                diceCommand = 'd'
            if len(reason) != 0:
                reason = ROLL_REASON_STR.format(reason=reason)
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
                finalResult = ROLL_FEED_STR.format(reason=reason, nickName=nickName, resultStr=resultStr)
                try:
                    if resultStr[:3] == 'D20' or resultStr[:4] == '1D20':
                        if rollResult.rawResultList[0][0] == 20:
                            finalResult += N20_FEED_STR
                        elif rollResult.rawResultList[0][0] == 1:
                            finalResult += N01_FEED_STR
                    elif resultStr.find('次D20') != -1 or resultStr.find('次1D20') != -1:
                        succTimes = 0
                        failTimes = 0
                        for resList in rollResult.rawResultList:
                            if resList[0] == 20:
                                succTimes += 1
                            elif resList[0] == 1:
                                failTimes += 1
                        if succTimes != 0:
                            finalResult += '\n' + N20_FEED_MULT_STR.format(succTimes=succTimes)
                        if failTimes != 0:
                            finalResult += '\n' + N01_FEED_MULT_STR.format(failTimes=failTimes)
                except:
                    pass

                if isHide:
                    finalResult = HROLL_RES_STR.format(finalResult=finalResult)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult, personIdList=[userId]),
                                          CommandResult(CoolqCommandType.MESSAGE,
                                                        HROLL_FEED_STR.format(nickName=nickName))]
                else:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult)]

        elif cType == CommandType.BOT:
            commandWeight = 3
            subType = command.cArg[0]
            if subType != 'show' and groupId == 'Private':
                raise UserError(GROUP_COMMAND_ONLY_STR)
            if subType == 'show':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, SHOW_STR)]
            elif onlyToMe:
                if subType == 'on':
                    result = tc.BotSwitch(self, groupId, True)
                else:
                    result = tc.BotSwitch(self, groupId, False)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.GROUP:
            commandWeight = 1
            subType = command.cArg[0]
            if groupId == 'Private': commandResultList += [
                CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            if subType == '帮助':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, HELP_COMMAND_GROUP_STR)]
            elif subType == '信息':
                result = tc.GetGroupSummary(self, groupId)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
            elif subType == '查看禁用功能':
                result = tc.GetBannedGroupFunc(self, groupId)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
            else:
                funcName = command.cArg[1]
                if subType == '启用功能':
                    result = tc.GroupFuncSwitch(self, groupId, funcName, True)
                elif subType == '禁用功能':
                    result = tc.GroupFuncSwitch(self, groupId, funcName, False)
                else:
                    result = ''
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.DISMISS:
            if not onlyToMe:
                raise UserError('')  # '不指定我的话, 这个指令是无效的哦'
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, DISMISS_FEED_STR),
                                  CommandResult(CoolqCommandType.DISMISS, groupIdList=[groupId])]

        elif cType == CommandType.NickName:
            newNickName = command.cArg[0]
            if len(newNickName) <= 20:
                result = self.UpdateNickName(groupId, userId, newNickName)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
            else:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, NICKNAME_LEN_LIMIT_STR)]

        elif cType == CommandType.HELP:
            subType = str(command.cArg[0])
            helpInfo = tc.GetHelpInfo(subType)
            if helpInfo:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, helpInfo)]

        elif cType == CommandType.INIT:
            self.dailyInfoDict['initCommand'] += 1
            commandWeight = 4
            subType = command.cArg[0]
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            else:
                if not subType:
                    result = tb.GetInitSummary(self, groupId)
                elif subType == 'clr':
                    result = tb.ClearInit(self, groupId)
                elif subType[:3] == 'del':
                    nameList = subType[3:].split('/')
                    result = ''
                    for name in nameList:
                        if not result:
                            result = tb.RemoveElemFromInit(self, groupId, name.strip())
                        else:
                            result += '\n' + tb.RemoveElemFromInit(self, groupId, name.strip())
                else:
                    result = ''
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.RI:
            self.dailyInfoDict['initCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
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
                        if name[i] in ['+', '-'] and name[i + 1:] and isDiceCommand(name[i + 1:]):
                            initAdjSub += name[i:]
                            name = name[:i]
                            break
                    result = tb.AddElemToInit(self, groupId, userId, name, initAdjSub, isPC)
                    if not finalResult:
                        finalResult = result
                    else:
                        finalResult += f'\n{result}'
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult)]

        elif cType == CommandType.HP:
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            else:
                self.dailyInfoDict['hpCommand'] += 1
                subType = command.cArg[0]
                if subType == '记录':
                    # Args: [targetStr, subType , hpStr, maxhpStr]
                    result = tp.UpdateHP(self, groupId, userId, *command.cArg[1:], nickName)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '查看':
                    result = tp.ShowHP(self, groupId, userId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'{nickName}{result}')]
                elif subType == '清除':
                    tp.ClearHP(self, groupId, userId)
                    commandResultList += [
                        CommandResult(CoolqCommandType.MESSAGE, HP_CLEAR_STR.format(nickName=nickName))]

        elif cType == CommandType.PC:
            self.dailyInfoDict['pcCommand'] += 1
            commandWeight = 3
            subType = command.cArg[0]
            infoStr = command.cArg[1]
            if groupId == 'Private' and subType != '模板':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            else:
                if subType == '记录':
                    result = tp.SetPlayerInfo(self, groupId, userId, infoStr)
                elif subType == '查看':
                    result = tp.GetPlayerInfo(self, groupId, userId, nickName)
                elif subType == '完整':
                    result = tp.GetPlayerInfoFull(self, groupId, userId, nickName)
                elif subType == '清除':
                    tp.ClearPlayerInfo(self, groupId, userId)
                    result = PC_CLEAR_STR.format(nickName=nickName)
                elif subType == '模板':
                    result = PC_SHEET_TEMPLATE

                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.CHECK:
            self.dailyInfoDict['checkCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            else:
                itemArgs = command.cArg[0].split('#')
                if len(itemArgs) == 1:
                    item = itemArgs[0]
                    times = 1
                else:
                    try:
                        times = int(itemArgs[0])
                        assert 1 <= times <= 10
                    except (ValueError, AssertionError):
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, CHECK_TIME_LIMIT_STR)]
                        times = None
                    item = itemArgs[1]

                if times:
                    diceCommand = command.cArg[1]
                    reason = command.cArg[2]
                    result = tp.PlayerCheck(self, groupId, userId, item, times, diceCommand, nickName)
                    if reason:
                        result = f'由于{reason}, {result}'
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.TeamCheck:
            self.dailyInfoDict['checkCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            else:
                try:
                    teamName = self.teamInfoDict[groupId]['name']
                    membersList = self.teamInfoDict[groupId]['members']
                    assert len(membersList) >= 1
                    valid = True
                except AssertionError:
                    raise UserError(TEAM_NEED_STR)

                item = command.cArg[0]
                diceCommand = command.cArg[1]
                reason = command.cArg[2]
                times = 1

                finalResult = f'{teamName}进行队伍{item}检定'
                if reason:
                    finalResult = f'由于{reason}, {finalResult}'
                errorInfo = None
                for memberId in membersList:
                    nickName = self.GetNickName(groupId, memberId)
                    result = tp.PlayerCheck(self, groupId, memberId, item, times, diceCommand, nickName)
                    finalResult += f'\n{result}'

                if errorInfo:
                    finalResult = errorInfo
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult)]

        elif cType == CommandType.SpellSlot:
            self.dailyInfoDict['slotCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            else:
                # Args: [subType, *args]
                subType = command.cArg[0]
                if subType == '记录':
                    result = tp.SetSpellSlot(self, groupId, userId, command.cArg[1])
                elif subType == '查看':
                    result = nickName + tp.ShowSpellSlot(self, groupId, userId)
                elif subType == '更改':
                    level = command.cArg[1]
                    try:
                        assert command.cArg[2][0] in ['+', '-']
                        adjVal = int(command.cArg[2])
                        assert -10 < adjVal < 10
                    except (AssertionError, ValueError):
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE,
                                                            SPELL_SLOT_ADJ_INVALID_STR.format(val=command.cArg[2]))]
                    result = nickName + tp.ModifySpellSlot(self, groupId, userId, level, adjVal)
                elif subType == '清除':
                    result = tp.ClearSpellSlot(self, groupId, userId)

                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.MONEY:
            self.dailyInfoDict['moneyCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            else:
                subType = command.cArg[0]
                if subType == '记录':
                    result = tp.SetMoney(self, groupId, userId, command.cArg[1])
                elif subType == '清除':
                    result = tp.ClearMoney(self, groupId, userId)
                elif subType == '更改':
                    result = nickName + tp.ModifyMoney(self, groupId, userId, command.cArg[1])
                elif subType == '查看':
                    result = nickName + '当前的财富:' + tp.ShowMoney(self, groupId, userId)
                else:
                    result = ''
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.TeamMoney:
            self.dailyInfoDict['moneyCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            else:
                try:
                    teamName = self.teamInfoDict[groupId]['name']
                    membersList = self.teamInfoDict[groupId]['members']
                    assert len(membersList) >= 1
                except (KeyError, AssertionError):
                    raise UserError(TEAM_NEED_STR)

                modifier = command.cArg[0]
                finalResult = f'{teamName}{modifier}:'
                for memberId in membersList:
                    nickName = self.GetNickName(groupId, memberId)
                    result = nickName + tp.ModifyMoney(self, groupId, memberId, modifier)
                    finalResult += f'\n{result}'
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, finalResult)]

        elif cType == CommandType.NOTE:
            self.dailyInfoDict['noteCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
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
                    result = tc.SetNote(self, groupId, index, content)
                elif subType == '清除':
                    index = command.cArg[1]
                    result = tc.ClearNote(self, groupId, index)
                elif subType == '查看':
                    index = command.cArg[1]
                    result = tc.ShowNote(self, groupId, index)
                else:
                    result = ''
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.TEAM:
            self.dailyInfoDict['teamCommand'] += 1
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            else:
                subType = command.cArg[0]
                if subType == '加入':
                    result = tp.JoinTeam(self, groupId, userId, command.cArg[1])
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '清除':
                    result = tp.ClearTeam(self, groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '查看':
                    result = tp.ShowTeam(self, groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '点名':
                    result = tp.CallTeam(self, groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == '完整':
                    result = tp.ShowTeamFull(self, groupId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result, personIdList=[userId]),
                                          CommandResult(CoolqCommandType.MESSAGE, TEAM_INFO_FEED_STR)]

        elif cType == CommandType.REST:
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            else:
                subType = command.cArg[0]
                if subType == '长休':
                    result = tp.LongRest(self, groupId, userId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, nickName + result)]

        elif cType == CommandType.SEND:
            commandWeight = 4
            if len(command.cArg[0]) < 10 or len(command.cArg[0]) > 100:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, SEND_LEN_LIMIT_STR)]
            else:
                if groupId != 'Private':
                    message = f'来自群{groupId} 用户{userId}的信息: {command.cArg[0]}'
                else:
                    message = f'来自用户{userId}的信息: {command.cArg[0]}'
                feedback = SEND_FEED_STR
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, message, personIdList=MASTER),
                                      CommandResult(CoolqCommandType.MESSAGE, feedback)]

        elif cType == CommandType.Question:
            commandWeight = 4
            if not command.cArg[0]:
                commandResultList += [
                    CommandResult(CoolqCommandType.MESSAGE, EXAM_LIST_STR.format(val=list(self.questionDict.keys())))]
            else:
                possKey = PairSubstring(command.cArg[0].strip(), self.questionDict.keys())
                if len(possKey) == 0:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, EXAM_MISS_STR)]
                elif len(possKey) > 1:
                    commandResultList += [
                        CommandResult(CoolqCommandType.MESSAGE, EXAM_MULT_STR.format(possKey=possKey))]
                else:
                    result = tc.StartExam(self, possKey[0], groupId, userId)
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.WELCOME:
            if groupId == 'Private':
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, GROUP_COMMAND_ONLY_STR)]
            else:
                info = command.cArg[0].strip()
                groupInfoCur['welcome'] = info
                if info:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, WELCOME_FEED_STR + '\n' + info)]
                else:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, WELCOME_CLEAR_STR)]

        elif cType == CommandType.NAME:
            temp = command.cArg[0].split('#')
            times = 1
            target = None
            try:
                assert 1 <= len(temp) <= 2
                if len(temp) == 1:
                    target = temp[0].strip()
                else:
                    times = int(temp[0])
                    target = temp[1].strip()
            except (AssertionError, ValueError):
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, NAME_FORMAT_STR)]
            if target is not None:
                if times > 10 or times <= 0:
                    result = NAME_LIMIT_STR
                else:
                    result = tc.GenerateName(self.nameInfoDict, target, times)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.JRRP:
            commandWeight = 2
            date = GetCurrentDateRaw()
            value = tc.GetJRRP(userId, date)
            if not userInfoCur['seenJRRP']:
                userInfoCur['seenJRRP'] = True
                self.dailyInfoDict['jrrpCommand'] += 1
                answer = JRRP_FEED_STR.format(nickName=nickName, value=value)
                if value >= 80:
                    answer += JRRP_GOOD_STR
                elif value <= 20:
                    gift = GIFT_LIST[np.random.randint(0, len(GIFT_LIST))]
                    answer += JRRP_BAD_STR.format(gift=gift)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, answer)]
            else:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, JRRP_REPEAT_STR.format(value=value))]

        elif cType == CommandType.DND:
            commandWeight = 3
            try:
                times = int(command.cArg[0])
                assert 0 < times <= 10
            except AssertionError:
                times = 1
            except ValueError:
                times = 1
            reason = command.cArg[1]
            result = tc.DNDBuild(times)
            result = DND_FEED_STR.format(nickName=nickName, reason=reason, result=result)
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.QUERY:
            self.dailyInfoDict['queryCommand'] += 1
            commandWeight = 3
            targetStr = str(command.cArg[0])
            queryResult = tc.QueryInfo(self, targetStr, userId, groupId)
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, queryResult)]

        elif cType == CommandType.INDEX:
            self.dailyInfoDict['queryCommand'] += 1
            commandWeight = 3
            targetStr = str(command.cArg[0])
            queryResult = tc.IndexInfo(self, targetStr, userId, groupId)
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
            drawResult = tc.DrawInfo(self, targetStr, timesStr)
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, drawResult)]

        elif cType == CommandType.COOK:
            self.dailyInfoDict['cookCommand'] += 1
            commandWeight = 4
            cookAdj = command.cArg[0]
            keywordList = command.cArg[1]
            cookResult = tc.CookCheck(self, cookAdj, keywordList)
            cookResult = COOK_FEED_STR.format(nickName=nickName, cookResult=cookResult)
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, cookResult)]

        elif cType == CommandType.ORDER:
            self.dailyInfoDict['cookCommand'] += 1
            commandWeight = 4
            number = command.cArg[0]
            keywordList = command.cArg[1]
            orderResult = tc.OrderDish(self, number, keywordList)
            orderResult = ORDER_FEED_STR.format(nickName=nickName, orderResult=orderResult)
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, orderResult)]

        elif cType == CommandType.TodayMenu:
            if not userInfoCur['seenJRCD']:
                userInfoCur['seenJRCD'] = True
                self.dailyInfoDict['cookCommand'] += 1
                commandWeight = 4
                date = GetCurrentDateRaw()
                result = tc.GetTodayMenu(self, userId, date)
                result = f'{nickName}的{result}'
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result, personIdList=[userId])]
            else:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, MENU_LIMIT_STR)]

        elif cType == CommandType.TodayJoke:
            flag = ''
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
                date = GetCurrentDateRaw() + command.cArg[0] * datetime.timedelta(days=1)
                result = tc.GetTodayJoke(self, userId, date)
                result = JOKE_FEED_STR.format(nickName=nickName, flag=flag, result=result)
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
            else:
                if command.cArg[0] == -1:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, JOKE_LIMIT_LAST_STR)]
                elif command.cArg[0] == 0:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, JOKE_LIMIT_TODAY_STR)]
                elif command.cArg[0] == 1:
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, JOKE_LIMIT_NEXT_STR)]

        elif cType == CommandType.CREDIT:
            if userInfoCur['seenCredit']:
                result = CREDIT_REPEAT_FEED
            else:
                credit = userInfoCur['credit']
                level = 0
                for i in CREDIT_LEVEL_FEED.keys():
                    if level < i <= credit:
                        level = i
                result = RandomSelectList(CREDIT_LEVEL_FEED[level])[0]
                result = result.format(name=nickName)
                result = InsertEmotion(result, self.emotionDict)
                userInfoCur['seenCredit'] = True
            commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]

        elif cType == CommandType.MASTER:
            if userId not in MASTER:
                commandResultList += [CommandResult(CoolqCommandType.MESSAGE, MASTER_LIMIT_STR)]
            else:
                subType = command.cArg[0]
                if subType == 'savedata':
                    try:
                        await self.UpdateLocalData()
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, SAVE_FEED_STR)]
                    except Exception as e:
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, f'保存资料时遇到错误:\n{e}')]
                elif subType == 'credit':
                    try:
                        commandArgs = command.cArg[1].split(':')
                        targetId = commandArgs[0].strip()
                        if len(commandArgs) > 1:  # 修改
                            value = int(commandArgs[1])
                            self.userInfoDict[targetId]['credit'] += value
                            commandResultList += [CommandResult(CoolqCommandType.MESSAGE,
                                                                f'{targetId}的好感度{int2str(value)},'
                                                                f' 现在是{self.userInfoDict[targetId]["credit"]}'),
                                                  CommandResult(CoolqCommandType.MESSAGE,
                                                                f'对你的好感度{int2str(value)},'
                                                                f' 现在是{self.userInfoDict[targetId]["credit"]}',
                                                                personIdList=[targetId])]
                        else:  # 查看
                            commandResultList += [CommandResult(CoolqCommandType.MESSAGE,
                                                                f'{targetId}的好感度是'
                                                                f'{self.userInfoDict[targetId]["credit"]}')]
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
                    result += f'成功:{self.dailyInfoDict["querySucc"]}' \
                              f' 失败:{self.dailyInfoDict["queryFail"]} 多结果:{self.dailyInfoDict["queryMult"]}\n'
                    result += f'抽卡指令:{self.dailyInfoDict["drawCommand"]}\n角色卡指令:{self.dailyInfoDict["pcCommand"]}\n'
                    result += f'金钱指令:{self.dailyInfoDict["moneyCommand"]}\n生命值指令:{self.dailyInfoDict["hpCommand"]}\n'
                    result += f'检定指令:{self.dailyInfoDict["checkCommand"]}\n法术位指令:{self.dailyInfoDict["slotCommand"]}\n'
                    result += f'烹饪指令:{self.dailyInfoDict["cookCommand"]}\n'
                    result += f'笔记指令:{self.dailyInfoDict["noteCommand"]}\n'
                    result += f'交互指令:{self.dailyInfoDict["IACommand"]}'
                    commandResultList += [CommandResult(CoolqCommandType.MESSAGE, result)]
                elif subType == 'debug':
                    flag = command.cArg[1].lower()
                    if flag == 'true' or flag == '1' or flag == 'on':
                        self.masterInfoDict['debug'] = True
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '开启debug模式(错误信息将会直接在命令行中显示')]
                    else:
                        self.masterInfoDict['debug'] = False
                        commandResultList += [CommandResult(CoolqCommandType.MESSAGE, '关闭debug模式(错误信息将会发送给Master')]

        return commandResultList, commandWeight

    async def ValidateGroupInvite(self, groupId, inviterId) -> bool:
        try:
            assert self.userInfoDict[inviterId]['credit'] >= 0
            CreateNewGroupInfo(self.groupInfoDict, groupId)
            self.groupInfoDict[groupId]['inviter'] = inviterId
            return True
        except (AssertionError, MasterError, KeyError):
            return False

    def GetBotData(self, botDataT: BotDataT, args: Sequence[Any] = (), isRef=False, autoCreate=False) -> Dict:
        # 从外部获取信息, isRef决定给出的是引用还是复制
        # 在获取不到信息且autoCreate=False时会抛出一个MasterError异常
        # 若获取不到信息且autoCreate=True, 会自动调用CreateBotData并返回新建的信息
        # 正常情况下, USER, GROUP, GROUP_MEMBER是必然存在的
        output = None
        try:
            if botDataT == BotDataT.USER:
                output = self.userInfoDict[args[0]]
            elif botDataT == BotDataT.GROUP:
                output = self.groupInfoDict[args[0]]
            elif botDataT == BotDataT.GROUP_MEMBER:
                if len(args) == 1:
                    output = self.memberInfoDict[args[0]]
                elif len(args) == 2:
                    output = self.memberInfoDict[args[0]][args[1]]
            elif botDataT == BotDataT.INIT:
                output = self.initInfoDict[args[0]]
            elif botDataT == BotDataT.PC:
                if len(args) == 1:
                    output = self.pcStateDict[args[0]]
                elif len(args) == 2:
                    output = self.pcStateDict[args[0]][args[1]]
            elif botDataT == BotDataT.TEAM:
                output = self.teamInfoDict[args[0]]
            elif botDataT == BotDataT.QUES:
                output = self.questionDict
            elif botDataT == BotDataT.QUERY:
                output = self.queryInfoDict
            elif botDataT == BotDataT.QUERY_SYN:
                output = self.querySynDict
            elif botDataT == BotDataT.DECK:
                output = self.deckDict
            elif botDataT == BotDataT.DISH:
                output = self.menuDict
            elif botDataT == BotDataT.JOKE:
                output = self.jokeDict
            else:
                raise MasterError(f'尝试获取信息时给定的类型{botDataT}不在可用范围之内')
        except MasterError as e:
            raise e
        except KeyError as e:
            if autoCreate:
                try:
                    self.CreateBotData(botDataT, args)
                    output = self.GetBotData(botDataT, args, isRef)
                    return output
                except Exception as e:
                    errorInfo = f'自动创建{BotDataT2Str(botDataT)}信息失败, 参数为{args}'
                    raise MasterError(errorInfo, type(e), rawError=e)
            else:
                errorInfo = f'获取{BotDataT2Str(botDataT)}信息失败, 参数为{args}'
                raise MasterError(errorInfo, type(e), rawError=e)

        except Exception as e:
            errorInfo = f'获取{BotDataT2Str(botDataT)}信息失败, 参数为{args}'
            raise MasterError(errorInfo, type(e), rawError=e)

        if output is None:
            errorInfo = f'获取{BotDataT2Str(botDataT)}信息失败, 参数为{args}, 输出为None'
            raise MasterError(errorInfo)

        if isRef:
            return output
        else:
            return copy.deepcopy(output)

    def DelBotData(self, botDataT: BotDataT, args: Sequence[Any]):
        # 删除给定的信息, 失败会抛出一个MasterError异常
        try:
            if botDataT == BotDataT.USER:
                del self.userInfoDict[args[0]]
            elif botDataT == BotDataT.GROUP:
                del self.groupInfoDict[args[0]]
            elif botDataT == BotDataT.GROUP_MEMBER:
                if len(args) == 1:
                    del self.memberInfoDict[args[0]]
                elif len(args) == 2:
                    del self.memberInfoDict[args[0]][args[1]]
            elif botDataT == BotDataT.INIT:
                del self.initInfoDict[args[0]]
            elif botDataT == BotDataT.PC:
                if len(args) == 1:
                    del self.pcStateDict[args[0]]
                elif len(args) == 2:
                    del self.pcStateDict[args[0]][args[1]]
            elif botDataT == BotDataT.TEAM:
                del self.teamInfoDict[args[0]]
            else:
                raise MasterError(f'尝试删除信息时给定的类型{botDataT}不在可用范围之内')
        except MasterError as e:
            raise e
        except Exception as e:
            errorInfo = f'获取{BotDataT2Str(botDataT)}信息失败, 参数为{args}'
            raise MasterError(errorInfo, type(e), rawError=e)

    def CreateBotData(self, botDataT: BotDataT, args: Sequence[Any]):
        try:
            if botDataT == BotDataT.USER:
                self.userInfoDict[args[0]] = copy.deepcopy(dt.userInfoTemp)
            elif botDataT == BotDataT.GROUP:
                self.groupInfoDict[args[0]] = copy.deepcopy(dt.groupInfoTemp)
            elif botDataT == BotDataT.GROUP_MEMBER:
                if len(args) == 1:
                    self.memberInfoDict[args[0]] = copy.deepcopy(dt.groupMemberDictTemp)
                elif len(args) == 2:
                    if args[0] not in self.memberInfoDict.keys():
                        self.memberInfoDict[args[0]] = copy.deepcopy(dt.groupMemberDictTemp)
                    self.memberInfoDict[args[0]][args[1]] = copy.deepcopy(dt.memberInfoTemp)
                else:
                    raise MasterError(f'创建{BotDataT2Str(botDataT)}信息的参数{args}不合法')
            elif botDataT == BotDataT.INIT:
                self.initInfoDict[args[0]] = copy.deepcopy(dt.initDictTemp)
            elif botDataT == BotDataT.PC:
                if len(args) == 1:
                    self.pcStateDict[args[0]] = copy.deepcopy(dt.groupPcDictTemp)
                elif len(args) == 2:
                    if args[0] not in self.pcStateDict.keys():
                        self.pcStateDict[args[0]] = copy.deepcopy(dt.groupPcDictTemp)
                    self.pcStateDict[args[0]][args[1]] = copy.deepcopy(dt.pcInfoBasicTemp)
                else:
                    raise MasterError(f'创建{BotDataT2Str(botDataT)}信息的参数{args}不合法')
            elif botDataT == BotDataT.TEAM:
                self.teamInfoDict[args[0]] = copy.deepcopy(dt.teamInfoTemp)
            else:
                raise MasterError(f'尝试删除信息时给定的类型{botDataT}不在可用范围之内')
        except MasterError as e:
            raise e
        except Exception as e:
            errorInfo = f'创建{BotDataT2Str(botDataT)}信息失败, 参数为{args}'
            raise MasterError(errorInfo, type(e), rawError=e)

    def GetNickName(self, groupId: str, userId: str) -> str:
        try:
            nickName = self.nickNameDict[groupId][userId]
        except KeyError:
            try:
                nickName = self.nickNameDict['Private'][userId]
            except KeyError:
                try:
                    nickName = self.userInfoDict[userId]['name']
                except Exception as e:
                    raise MasterError(f'获取昵称失败, 群号为{groupId}, 姓名为{userId}', type(e))
        except Exception as e:
            raise MasterError(f'获取昵称失败, 群号为{groupId}, 姓名为{userId}', type(e))
        return nickName

    def UpdateNickName(self, groupId: str, userId: str, nickName: str) -> str:
        try:
            assert type(self.nickNameDict[groupId]) == dict
        except (KeyError, AssertionError):
            self.nickNameDict[groupId] = {}

        if nickName:  # 如果指定了昵称, 则更新昵称
            imposterList = []
            for strCur in NAME2TITLE.keys():
                if nickName.find(strCur) != -1:
                    imposterList.append(strCur)
            if imposterList:
                return f'{imposterList[0]}是{NAME2TITLE[imposterList[0]]}哦~请换个名字吧!'
            self.nickNameDict[groupId][userId] = nickName
            # 尝试修改先攻列表
            try:
                initList = self.initInfoDict[groupId]['initList']
                # 如果已有先攻列表有同名角色, 修改所有权
                if nickName in initList.keys():
                    # 先移除可能的原本角色
                    previousName = None
                    for itemName in initList.keys():
                        if initList[itemName]['id'] == userId and initList[itemName]['isPC']:
                            previousName = itemName
                            break
                    if previousName:
                        del initList[previousName]
                    # 再修改所有权
                    initList[nickName]['id'] = userId
                    initList[nickName]['isPC'] = True
                else:
                    # 在先攻列表中搜索该pc控制的角色
                    previousName = None
                    for itemName in initList.keys():
                        if initList[itemName]['id'] == userId and initList[itemName]['isPC']:
                            previousName = itemName
                            break
                    # 如果找到, 就新建一份并且删除原有的记录
                    if previousName:
                        initList[nickName] = initList[previousName]
                        del initList[previousName]
                self.initInfoDict[groupId]['initList'] = initList
            except KeyError:
                pass

            return NN_FEED_STR.format(nickName=nickName)
        else:  # 否则移除原有的昵称
            try:
                del self.nickNameDict[groupId][userId]
            except KeyError:
                pass
            return NN_RESET_STR

    def RegisterIACommand(self, userId, groupId, funcName, argsList, IAType=-1, expireTime=IA_EXPIRE_TIME,
                          expireWarning='', isRepeat=False):
        # 查找已有的同类交互指令并删除
        for i in range(len(self.userInfoDict[userId]['IACommand']) - 1, -1, -1):
            if self.userInfoDict[userId]['IACommand'][i]['groupId'] == groupId and \
                    self.userInfoDict[userId]['IACommand'][i]['IAType'] == IAType:
                self.userInfoDict[userId]['IACommand'].pop(i)
                break

        if len(self.userInfoDict[userId]['IACommand']) >= IA_LIMIT_NUM:
            self.userInfoDict[userId]['IACommand'].pop(0)

        info = dict()
        info['name'] = funcName
        info['date'] = Datetime2Str(GetCurrentDateRaw() + expireTime)
        info['personId'] = userId
        info['groupId'] = groupId
        info['args'] = argsList
        info['IAType'] = IAType
        info['warning'] = expireWarning
        info['isRepeat'] = isRepeat
        info['isValid'] = True
        self.userInfoDict[userId]['IACommand'].append(info)

    def IA_QueryInfoWithIndex(self, IAInfo, index) -> str:
        targetStr = IAInfo['args'][0]
        try:
            index = int(index)
            assert 0 < index <= QUERY_SHOW_LIMIT
        except (ValueError, AssertionError):
            return ''
        keywordList = [k for k in targetStr.split('/') if k]
        possResult = PairSubstringList(keywordList, self.queryInfoDict.keys())
        try:
            assert index <= len(possResult)
            return self.queryInfoDict[possResult[index - 1]]
        except AssertionError:
            return ''

    def IA_IndexInfoWithIndex(self, IAInfo, index) -> str:
        targetStr = IAInfo['args'][0]
        try:
            index = int(index)
            assert 0 < index <= QUERY_SHOW_LIMIT
        except (ValueError, AssertionError):
            return ''
        keywordList = [k for k in targetStr.split('/') if k]
        possResult = []
        # 开始索引
        for item in self.queryInfoDict:
            valid = True
            itemInfo = item.lower() + self.queryInfoDict[item].lower()
            for k in keywordList:
                if k not in itemInfo:
                    valid = False
                    break
            if valid:
                possResult.append(item)
        try:
            assert index <= len(possResult)
            return self.queryInfoDict[possResult[index - 1]]
        except AssertionError:
            return ''

    def IA_AnswerQuestion(self, IAInfo, answer) -> str:
        userId = IAInfo['personId']
        groupId = IAInfo['groupId']
        examKey, questionIndexList, examState = IAInfo['args']
        questionInfo = self.questionDict[examKey][questionIndexList[examState[0]]]
        answer = answer.strip().upper()
        if answer == 'Q':
            return f'那么考试就到这里咯~ 你总共答对了{examState[1]}道题, 答错了{examState[2]}道题'
        groundTruth = questionInfo[1]
        quesExp = questionInfo[2]
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
            result += EXAM_TRUE_STR
            examState[1] += 1
        else:
            result += EXAM_FALSE_STR.format(answer=groundTruth)
            examState[2] += 1
        if quesExp:
            result += f'解析: {quesExp}\n\n'

        examState[0] += 1
        if examState[0] < len(questionIndexList):
            self.RegisterIACommand(userId, groupId, 'IA_AnswerQuestion', [examKey, questionIndexList, examState], 1,
                                   datetime.timedelta(seconds=120), EXAM_EXPIRE_STR)
            result += f'\n下一道题来咯!\n第{examState[0] + 1}题:'
            result += self.questionDict[examKey][questionIndexList[examState[0]]][0]
        else:
            result += (f'\n考试结束咯, 你答对了{len(questionIndexList)}道题中的{examState[1]}道'
                       f', 正确率为{100 * examState[1] / len(questionIndexList)}%~')
        return result


def CreateNewUserInfo(userDict, userId):
    userDict[userId] = copy.deepcopy(dt.userInfoTemp)


def CreateNewGroupInfo(groupDict, groupId):
    groupDict[groupId] = copy.deepcopy(dt.groupInfoTemp)


def CreateNewGroupMemberInfo(memberDict, groupId):
    memberDict[groupId] = copy.deepcopy(dt.groupMemberDictTemp)


def CreateNewMemberInfo(groupMemberDict, userId):
    groupMemberDict[userId] = copy.deepcopy(dt.memberInfoTemp)


def UpdateInfoDictByTemplate(inputDict, tempDict):
    outputDict = copy.deepcopy(inputDict)

    for keyId in inputDict.keys():
        infoCur = outputDict[keyId]
        if type(infoCur) != dict:
            del outputDict[keyId]
            continue

        for curK in infoCur.keys():
            if curK not in tempDict.keys():
                del outputDict[keyId][curK]

        for tempK in tempDict.keys():
            if tempK not in infoCur.keys():
                outputDict[keyId][tempK] = tempDict[tempK]
    return outputDict


def UpdateDictByTemplate(inputDict, tempDict):
    outputDict = copy.deepcopy(inputDict)

    for curK in inputDict.keys():
        if curK not in tempDict.keys():
            del outputDict[curK]

    for tempK in tempDict.keys():
        if tempK not in inputDict.keys():
            outputDict[tempK] = tempDict[tempK]
    return outputDict


def UpdateAllUserInfo(bot):
    bot.userInfoDict = UpdateInfoDictByTemplate(bot.userInfoDict, dt.userInfoTemp)


def UpdateAllGroupInfo(bot):
    bot.groupInfoDict = UpdateInfoDictByTemplate(bot.groupInfoDict, dt.groupInfoTemp)


def UpdateAllMemberInfo(bot):
    for groupId in bot.memberInfoDict.keys():
        bot.memberInfoDict[groupId] = UpdateInfoDictByTemplate(bot.memberInfoDict[groupId], dt.memberInfoTemp)


def UpdateMasterInfo(bot):
    bot.masterInfoDict = UpdateDictByTemplate(bot.masterInfoDict, dt.masterInfoTemp)


def UpdateDailyInfoDict(dailyDict):
    try:
        assert (GetCurrentDateRaw() - Str2Datetime(dailyDict['date'])) < datetime.timedelta(days=1)
        for k in dailyDict.keys():
            assert k in dt.dailyInfoTemp.keys()
    except (AssertionError, KeyError):
        dailyDict = copy.deepcopy(dt.dailyInfoTemp)
        dailyDict['date'] = GetCurrentDateStr()
    for k in dt.dailyInfoTemp.keys():
        if k not in dailyDict.keys():
            dailyDict[k] = copy.deepcopy(dt.dailyInfoTemp[k])
    return dailyDict


def DetectSpam(currentDate, lastDateStr, accuNum, weight=1) -> (bool, str, int):
    lastDate = Str2Datetime(lastDateStr)
    if currentDate - lastDate > MESSAGE_LIMIT_TIME:
        return False, Datetime2Str(currentDate), 0
    else:
        if accuNum + weight < MESSAGE_LIMIT_NUM:
            return False, lastDateStr, accuNum + weight
        else:
            return True, lastDateStr, accuNum + weight
