from info_help import *
from info_chat import *
from custom_config import *
from tool_dice import *
import tool_dice as td


def BotSwitch(bot, groupId: str, activeState: bool) -> str:
    groupInfo = bot.GetBotData(BotDataT.GROUP, (groupId,), isRef=True)
    groupInfo['active'] = activeState
    if activeState:
        return BOT_ON_STR
    else:
        return BOT_OFF_STR


def GetGroupSummary(bot, groupId: str) -> str:
    def GetGroupUselessRate(groupInfoCur):
        prevRate = (10 * groupInfoCur['dndCommandAccu'] + 2 * groupInfoCur['commandAccu']) / groupInfoCur['messageAccu']
        prevRate = 1 - min(prevRate, 1)
        curRate = (10 * groupInfoCur['dndCommandDaily'] + 2 * groupInfoCur['commandDaily']) / groupInfoCur[
            'messageDaily']
        curRate = 1 - min(curRate, 1)
        gamma = (min(groupInfoCur['days'], 30) / 30) * 0.5  # 历史数据的权重, 群存在时间越久权重越高
        finalRate = gamma * prevRate + (1 - gamma) * curRate
        finalRate = int(100 * finalRate)
        return finalRate

    groupInfo = bot.GetBotData(BotDataT.GROUP, (groupId,))
    memberInfo = bot.GetBotData(BotDataT.GROUP_MEMBER, (groupId,))
    result = ''
    result += f'群名称: {groupInfo["name"]}\n'
    result += f'活跃群成员数量 {len(memberInfo)}\n'
    result += f'好感度排名:\n'
    memberList = []
    for userId in memberInfo.keys():
        try:
            userInfo = bot.GetBotData(BotDataT.USER, (userId,))
            lastTime = GetCurrentDateRaw() - Str2Datetime(memberInfo[userId]['activeDate'])
            assert lastTime <= datetime.timedelta(days=7)
        except (MasterError, AssertionError):
            continue
        memberList.append((bot.GetNickName(groupId, userId), userId, userInfo['credit']))
    memberList = sorted(memberList, key=lambda x: x[2], reverse=True)[:10]
    for i in range(len(memberList)):
        result += f'{i + 1}. {memberList[i][0]} {memberList[i][1]}\n'
    result += f'潮湿程度: {GetGroupUselessRate(groupInfo)}%'
    return result


def GroupFuncSwitch(bot, groupId: str, funcName: str, activeState: bool) -> str:
    if funcName not in Str2CommandTypeDict.keys():
        return '所选的功能不在可选范围内呢, 请输入.help群管理查看'
    commandTypeDict = Str2CommandTypeDict[funcName]
    groupInfo = bot.GetBotData(BotDataT.GROUP, (groupId,), isRef=True)
    if activeState:
        for c in commandTypeDict:
            try:
                del groupInfo['BanFunc'][int(c)]
            except KeyError:
                pass
        return FUNC_ON_STR.format(funcName=funcName)
    else:
        for c in commandTypeDict:
            groupInfo['BanFunc'][int(c)] = ''
        return FUNC_OFF_STR.format(funcName=funcName)


def GetBannedGroupFunc(bot, groupId: str) -> str:
    BanFuncList = []
    groupInfo = bot.GetBotData(BotDataT.GROUP, (groupId,))
    bannedGroupCommand = groupInfo['BanFunc']
    for funcStr in Str2CommandTypeDict.keys():
        commandTypeDict = Str2CommandTypeDict[funcStr]
        flag = False
        for cType in commandTypeDict:
            if int(cType) in bannedGroupCommand:
                flag = True
                continue
        if flag:
            BanFuncList.append(funcStr)
    if BanFuncList:
        resultStr = '目前没有被禁用的功能哦~'
    else:
        resultStr = f'目前被禁用的功能是{BanFuncList}~'

    return resultStr


def GetHelpInfo(subType: str) -> str:
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
    elif subType == '群管理':
        return HELP_COMMAND_GROUP_STR
    else:
        return ''


def SetNote(bot, groupId: str, index: str, content: str) -> str:
    groupInfo = bot.GetBotData(BotDataT.GROUP, (groupId,), isRef=True)
    noteInfo = groupInfo['note']
    if content[0] == '+':
        try:
            newContent = noteInfo[index] + '。' + content[1:]
        except KeyError:
            newContent = content[1:]
        content = newContent
    if not index:
        index = '临时记录'
    if len(noteInfo) > 20:
        raise UserError(NOTE_NUM_LIMIT_STR)
    if len(content) > 300:
        raise UserError(NOTE_LEN_LIMIT_STR)
    totalWords = 0
    for k in noteInfo.keys():
        totalWords += len(noteInfo[k])
    if totalWords + len(content) > 2000:
        raise UserError(NOTE_TOTAL_LIMIT_STR)
    noteInfo[index] = content
    return NOTE_FEED_STR.format(index=index)


def ClearNote(bot, groupId: str, index: str) -> str:
    groupInfo = bot.GetBotData(BotDataT.GROUP, (groupId,), isRef=True)
    noteInfo = groupInfo['note']

    if not index:
        index = '临时记录'
    if index == '所有笔记':
        groupInfo['note'] = {}
        return NOTE_CLEAR_ALL_STR
    else:
        if index not in noteInfo.keys():
            resList = PairSubstring(index, noteInfo.keys())
            if len(resList) == 1:
                index = resList[0]
            elif len(resList) > 1:
                return NOTE_MULT_INDEX_STR.format(resList=resList)
            else:
                return NOTE_MISS_STR
        del noteInfo[index]
        return NOTE_CLEAR_STR.format(index=index)


def ShowNote(bot, groupId: str, index: str) -> str:
    groupInfo = bot.GetBotData(BotDataT.GROUP, (groupId,), isRef=False)
    noteInfo = groupInfo['note']

    if not index:
        result = '所有笔记:\n'
        for k in noteInfo.keys():
            result += f'{k}:{noteInfo[k]}\n'
        result = result[:-1]
    else:
        if index not in noteInfo.keys():
            resList = PairSubstring(index, noteInfo.keys())
            if len(resList) == 1:
                index = resList[0]
            elif len(resList) > 1:
                return NOTE_MULT_INDEX_STR.format(resList=resList)
            else:
                return NOTE_MISS_STR
        result = f'{index}:{noteInfo[index]}\n'
    return result


def StartExam(bot, examKey: str, groupId: str, userId: str, questionNum: int = 10) -> str:
    questionDict = bot.GetBotData(BotDataT.QUES, isRef=False, autoCreate=False)
    if examKey not in questionDict.keys():
        raise UserError(EXAM_MISS_STR.format(key=examKey))

    size = len(questionDict[examKey])
    questionNum = min(size, questionNum)
    questionIndexList = np.random.permutation(size)[:questionNum].tolist()
    examState = [0, 0, 0]  # 当前序号, 正确, 错误数量
    bot.RegisterIACommand(userId, groupId, 'IA_AnswerQuestion', [examKey, questionIndexList, examState], 1,
                          datetime.timedelta(seconds=120), EXAM_EXPIRE_STR)
    result = f'{examKey}考试开始啦, 下面是从{size}道题中为你随机选择的{questionNum}道题~\n'
    result += '判断题输入T/F 或 Y/N回答, 选择题请输入序号。答案是大小写都可以\n每道题只有2分钟的有效时间, 错过了就请重新开始吧~\n'
    result += '输入Q即可中止考试\n'
    result += f'听好咯, 第一道题目是:\n{questionDict[examKey][questionIndexList[0]][0]}'
    return result


def GenerateName(nameInfoDict: dict, target: str, times: int):
    if not nameInfoDict:
        return INFO_MISS_STR.format(val='姓名')
    if not target:
        return f'当前可选的姓名有:{list(nameInfoDict["meta"].keys())}'
    if target not in nameInfoDict['meta'].keys():
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
    for _ in range(times):
        detailInfo = RandomSelectList(nameInfoDict['meta'][target])[0]  # 示例: ['达马拉人', 0, 2]
        chinesePart = ''
        englishPart = ''
        for i in range(1, len(detailInfo)):
            tempInfo = RandomSelectList(nameInfoDict['info'][detailInfo[0]][detailInfo[i]])[0]
            englishPart += tempInfo[0] + '·'
            chinesePart += tempInfo[1] + '·'
        result += f'\n{chinesePart[:-1]} ({englishPart[:-1]})'
    return result


def GetJRRP(userId, date) -> int:
    seed = 0
    temp = 1
    seed += date.year + date.month * 13 + date.day * 6
    for c in userId:
        seed += ord(c) * temp
        temp += 3
        if temp > 10:
            temp = -4
    seed = int(seed)
    np.random.seed(seed)
    value = np.random.randint(0, 101)
    return value


def DNDBuild(times: int) -> str:
    result = ''
    for i in range(times):
        error, resultStr, rollResult = td.RollDiceCommand(f'6#4d6k3')
        result += f'力量:{rollResult.rawResultList[0][0]}  敏捷:{rollResult.rawResultList[1][0]}' \
                  f'  体质:{rollResult.rawResultList[2][0]}  智力:{rollResult.rawResultList[3][0]}'
        result += f'  感知:{rollResult.rawResultList[4][0]}  魅力:{rollResult.rawResultList[5][0]}'
        result += f'  共计:{sum(rollResult.totalValueList)}'
        if i != (times - 1) and times != 1:
            result += '\n'
    return result


def QueryInfo(bot, targetStr: str, userId: str, groupId: str) -> str:
    try:
        queryInfoDict = bot.GetBotData(BotDataT.QUERY)
    except MasterError:
        raise UserError(INFO_MISS_STR.format(val='查询'))

    if not targetStr:
        return QUERY_NOTICE_STR.format(num=len(queryInfoDict))

    if targetStr in queryInfoDict.keys():
        return queryInfoDict[targetStr]

    # 尝试替换同义词
    try:
        querySynDict = bot.GetBotData(BotDataT.QUERY_SYN)
        if targetStr in querySynDict.keys():
            targetStr = querySynDict[targetStr]
            if targetStr in queryInfoDict.keys():
                return queryInfoDict[targetStr]
    except Exception as e:
        raise MasterError('同义词词典出现问题', type(e), e)

    # 无法直接找到结果, 尝试搜索
    keywordList = [k for k in targetStr.split('/') if k]
    if len(keywordList) > 5:
        return QUERY_KEY_LIMIT_STR
    possResult = PairSubstringList(keywordList, queryInfoDict.keys())

    if len(possResult) > 1:
        result = ''
        for i in range(min(len(possResult), QUERY_SHOW_LIMIT)):
            result += f'{i + 1}.{possResult[i]} '
        if len(possResult) <= QUERY_SHOW_LIMIT:
            result = QUERY_MULT_SHORT_STR.format(info=result[:-1])
        else:
            result = QUERY_MULT_LONG_STR.format(info=result[:-1], num=len(possResult))
        bot.RegisterIACommand(userId, groupId, 'IA_QueryInfoWithIndex', [targetStr], 0, isRepeat=True)
        return result
    elif len(possResult) == 1:
        result = str(queryInfoDict[possResult[0]])
        result = QUERY_FEED_COMP_STR.format(key=possResult[0], result=result)
        return result
    else:
        return QUERY_MISS_STR


def IndexInfo(bot, targetStr: str, userId: str, groupId: str) -> str:
    try:
        queryInfoDict = bot.GetBotData(BotDataT.QUERY)
    except MasterError:
        raise UserError(INFO_MISS_STR.format(val='查询'))

    if not targetStr:
        return QUERY_NOTICE_STR.format(num=len(queryInfoDict))

    possResult = []
    keywordList = [k for k in targetStr.split('/') if k]
    if len(keywordList) > 5:
        return QUERY_KEY_LIMIT_STR

    # 开始索引
    for item in queryInfoDict:
        valid = True
        itemInfo = item.lower() + queryInfoDict[item].lower()
        for k in keywordList:
            if k not in itemInfo:
                valid = False
                break
        if valid:
            possResult.append(item)
    if len(possResult) == 0:
        return INDEX_MISS_STR.format(keywordList=keywordList)
    elif len(possResult) == 1:
        return QUERY_FEED_COMP_STR.format(key=possResult[0], result=queryInfoDict[possResult[0]])
    else:
        result = ''
        for i in range(min(len(possResult), QUERY_SHOW_LIMIT)):
            result += f'{i + 1}.{possResult[i]} '
        if len(possResult) <= QUERY_SHOW_LIMIT:
            result = QUERY_MULT_SHORT_STR.format(info=result[:-1])
        else:
            result = QUERY_MULT_LONG_STR.format(info=result[:-1], num=len(possResult))
        bot.RegisterIACommand(userId, groupId, 'IA_IndexInfoWithIndex', [targetStr], 0, isRepeat=True)
        return result


def DrawInfo(bot, targetStr: str, timesStr: str = '1') -> str:
    try:
        deckDict = bot.GetBotData(BotDataT.DECK)
    except MasterError:
        raise UserError(INFO_MISS_STR.format(val='牌堆'))

    if not targetStr:
        return DRAW_NOTICE_STR.format(num=len(deckDict), val=list(deckDict.keys()))

    try:
        times = int(timesStr)
        assert times >= 1
        assert times <= 10
    except (ValueError, AssertionError):
        return DRAW_NUM_LIMIT_STR

    try:
        targetDeck = deckDict[targetStr]
        result = DrawFromDeck(targetDeck, deckDict, times=times)
        result = DRAW_FEED_STR.format(targetStr=targetStr, result=result)
        return result
    except (KeyError, MasterError):
        # 无法直接找到结果, 尝试搜索
        keywordList = [k for k in targetStr.split('/') if k]
        if len(keywordList) > 5:
            return QUERY_KEY_LIMIT_STR

        # 开始逐个搜索
        possResult = PairSubstringList(keywordList, deckDict.keys())

        if len(possResult) > 1:
            if len(possResult) <= 30:
                result = DRAW_MULT_SHORT_STR.format(info=possResult)
            else:
                result = DRAW_MULT_LONG_STR.format(info=possResult[:30], num=len(possResult))
            return result
        elif len(possResult) == 1:
            result = DrawFromDeck(deckDict[possResult[0]], deckDict, times=times)
            result = DRAW_FEED_STR.format(targetStr=possResult[0], result=result)
            return result
        else:
            return QUERY_MISS_STR


def DrawFromDeck(deck, allDeck, deep=1, times=1) -> str:
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
            result += f'\n第{t + 1}次:'
        randWeight = np.random.randint(deck['totalWeight']) + 1
        selectedItem = None
        for item in deck['list']:
            randWeight -= item['weight']
            if randWeight <= 0:
                selectedItem = item
                break
        if not selectedItem:
            return f'未知的错误发生了: 权重总值不正确'
        for c in selectedItem['content']:
            if c[0] == 'TEXT':
                result += c[1]
            elif c[0] == 'ROLL':
                error, resultStr, rollResult = RollDiceCommand(c[1])
                if error:  # 不应该发生的情况
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
                except (IndexError, AssertionError):
                    timeStr = ''
                    drawTimes = 1
                newResult = DrawFromDeck(allDeck[target], allDeck, deep + 1, drawTimes)
                result += f'抽取{target} {timeStr}{newResult}\n'
            else:  # 不应该发生的情况
                return f'该段信息存在错误: 关键词错误 {c} raw:{selectedItem["raw"]}'

        if selectedItem['end']:
            result += '\n抽取终止'
            break
    return result.strip()


def CookCheck(bot, cookAdj: str, keywordList: list) -> str:
    result = ''
    # cookAdj 有两种情况, 一是调整值, 二是固定值
    if not cookAdj or cookAdj[0] in ['+', '-'] or cookAdj[:2] in ['优势', '劣势']:  # 通过符号判断
        error, resultStr, rollResult = RollDiceCommand('d20' + cookAdj)
    else:
        error, resultStr, rollResult = RollDiceCommand(cookAdj)
    if error:
        raise UserError(resultStr)
    cookValue = rollResult.totalValueList[0]

    try:
        menuDict = bot.GetBotData(BotDataT.DISH)
    except MasterError:
        raise UserError(INFO_MISS_STR.format(val='菜谱'))

    if keywordList:
        if len(keywordList) > 5:
            raise UserError(f'至多指定5个关键词噢~')
        for key in keywordList:
            if key not in MENU_KEYWORD_LIST:
                raise UserError(f'{key}不是有效的关键词, 请查看.help烹饪')
        possDish, delKeyList = FindDishList(menuDict, keywordList)
        if len(possDish) == 0:
            raise UserError(f'想不到满足要求的食物呢...')
        if len(delKeyList) != 0:
            result += f'在无视了关键词{delKeyList}后, '
    else:
        possDish = list(menuDict.keys())

    SetNumpyRandomSeed()
    dishName = RandomSelectList(possDish)[0]
    result += f'于{len(possDish)}个备选中选择了{dishName}\n'
    dishInfo = menuDict[dishName]

    deliValue = 0
    result += f'在检定时掷出了{resultStr} '
    if cookValue >= dishInfo['难度']:
        if cookValue >= dishInfo['难度'] + 10:
            result += '完美!\n'
            deliValue += 10
        elif cookValue >= dishInfo['难度'] + 5:
            result += '非常成功\n'
            deliValue += 5
        else:
            result += '比较成功\n'
    else:
        if cookValue <= dishInfo['难度'] - 10:
            result += '大失败!\n'
            if keywordList:
                possDish, delKeyList = FindDishList(menuDict, ['黑暗'] + keywordList)
            else:
                possDish, delKeyList = FindDishList(menuDict, ['黑暗'])
            dishName = RandomSelectList(possDish)[0]
            dishInfo = menuDict[dishName]
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
    return result


def OrderDish(bot, numberStr: str, keywordList: list) -> str:
    result = ''
    number = 1
    if numberStr:
        error, resultStr, rollResult = RollDiceCommand(numberStr)
        if error:
            raise UserError(resultStr)
        number = rollResult.totalValueList[0]
        if number < 1:
            raise UserError(ORDER_LIMIT_MIN_STR)
        if number > 5:
            raise UserError(ORDER_LIMIT_MAX_STR)
    try:
        menuDict = bot.GetBotData(BotDataT.DISH)
    except MasterError:
        raise UserError(INFO_MISS_STR.format(val='菜谱'))

    if keywordList:
        if len(keywordList) > 5:
            raise UserError(f'至多指定5个关键词噢~')
        for key in keywordList:
            if key not in MENU_KEYWORD_LIST:
                raise UserError(ORDER_INVALID_STR.format(key=key))
        possDish, delKeyList = FindDishList(menuDict, keywordList)
        if len(possDish) == 0:
            raise UserError(ORDER_FAIL_ALL_STR)
        if len(delKeyList) != 0:
            result += ORDER_FAIL_PART_STR.format(delKeyList=delKeyList)
    else:
        possDish = list(menuDict.keys())

    SetNumpyRandomSeed()
    dishNameList = RandomSelectList(possDish, number)
    result += ORDER_FEED_P2_STR.format(num1=len(possDish), num2=len(dishNameList))
    for dishName in dishNameList:
        dishInfo = menuDict[dishName]
        result += f'{dishName} {dishInfo["价格"]}\n{dishInfo["描述"]}\n'
    return result[:-1]


def FindDishList(menuDict, keywordList) -> (list, list):
    possDish = []
    delKeyList = []
    while len(keywordList) > 0:
        for dishName in menuDict.keys():
            isValid = True
            for key in keywordList:
                if key not in menuDict[dishName]['关键词']:
                    isValid = False
                    break
            if isValid:
                possDish.append(dishName)
        if len(possDish) == 0:  # 如果没有找到一个合适的菜肴, 尝试删掉最后一个关键词
            delKeyList.append(keywordList.pop())
        else:
            break  # 停止寻找
    return possDish, delKeyList


def GetTodayMenu(bot, personId, date) -> str:
    seed = 0
    temp = 1
    seed += date.year + date.month * 13 + date.day * 6
    for c in personId:
        seed += ord(c) * temp
        temp += 3
        if temp > 10:
            temp = -4
    seed = int(seed)
    np.random.seed(seed)

    try:
        menuDict = bot.GetBotData(BotDataT.DISH)
    except MasterError:
        raise UserError(INFO_MISS_STR.format(val='菜谱'))

    result = ''
    todayCuisine = RandomSelectList(MENU_CUISINE_LIST)[0]
    todayStyle = RandomSelectList(MENU_STYLE_LIST)[0]
    result += f'今日菜单主题是{todayCuisine}与{todayStyle}噢~\n'
    usedDishList = []
    for typeStr in MENU_TYPE_LIST:
        possDish, delKeyList = FindDishList(menuDict, [typeStr, todayCuisine, todayStyle])
        if len(possDish) != 0 and len(delKeyList) <= 1:
            dishName = RandomSelectList(possDish, 1)[0]
            if dishName in usedDishList:
                continue
            usedDishList.append(dishName)
            dishInfo = menuDict[dishName]
            result += f'{typeStr}:{dishName} {dishInfo["价格"]}\n{dishInfo["描述"]}\n'

    return result[:-1]


def GetTodayJoke(bot, personId, date) -> str:
    seed = 0
    temp = 1
    seed += date.year + date.month * 13 + date.day * 6
    for c in personId:
        seed += ord(c) * temp
        temp += 3
        if temp > 10:
            temp = -4
    seed = int(seed)
    np.random.seed(seed)

    try:
        jokeDict = bot.GetBotData(BotDataT.JOKE)
    except MasterError:
        raise UserError(INFO_MISS_STR.format(val='笑话'))

    wordSize = len(jokeDict['word'])
    imgSize = len(jokeDict['img'])
    index = np.random.randint(wordSize + imgSize)
    if index < wordSize or not IS_COOLQ_PRO:
        jokeCur = RandomSelectList(jokeDict['word'], 1)[0]
    else:
        index = index - wordSize
        fileName = jokeDict['img'][index]
        absPath = os.path.join(LOCAL_JOKEIMG_DIR_PATH, fileName)
        jokeCur = f'[CQ:image,file=file:///{absPath}]'
    return jokeCur
