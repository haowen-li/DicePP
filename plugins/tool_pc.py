import math
import copy

from tool_dice import *
import tool_battle as tb
from info_game import *
from utils import *


def GetBasicPCState(bot, groupId: str, userId: str, isRef: bool = False, autoCreate: bool = False):
    pcState = bot.GetBotData(BotDataT.PC, (groupId, userId), isRef=isRef, autoCreate=autoCreate)
    return pcState


def SetPlayerInfo(bot, groupId: str, userId: str, infoStr: str) -> str:
    pcState = GetBasicPCState(bot, groupId, userId, isRef=True, autoCreate=True)

    # linesep = os.linesep
    linesep = '\n'
    infoStr = infoStr.strip()
    infoLength = len(infoStr)
    numberStrList = [str(n) for n in range(10)] + [' ']
    pcAbilityList = list(PC_ABILITY_DICT.keys())
    # 处理六大基本属性和熟练加值
    for ability in pcAbilityList + ['熟练加值']:
        index = infoStr.find(ability)
        if index == -1:
            return f'无法找到关键词"{ability}", 请查看.角色卡模板'
        # 找到属性值字符串
        index += len(ability) + 1
        lastIndex = index
        for i in range(index, infoLength):
            if infoStr[i] in numberStrList:
                lastIndex = i + 1
            else:
                break
        abilityVal = infoStr[index:lastIndex].strip()
        try:
            abilityVal = int(abilityVal)
            assert 0 <= abilityVal <= 99
            pcState[ability] = abilityVal
            pcState['额外' + ability] = ''
        except (ValueError, AssertionError):
            return f'关键词"{ability}"对应的属性值"{abilityVal}"无效, 请查看.角色卡模板'

    # 计算基础属性调整值
    for ability in pcAbilityList:
        pcState[ability + '调整值'] = math.floor((pcState[ability] - 10) / 2)
    pcState['无调整值'] = 0

    # 初始化技能加值,豁免加值,攻击加值与额外加值
    checkKeywordList = list(PC_CHECK_DICT_SHORT.keys())
    profAbleKeywordList = list(PC_SKILL_DICT.keys()) + list(PC_SAVING_DICT.keys())
    for key in checkKeywordList:
        pcState[key] = pcState[PC_CHECK_DICT_SHORT[key]]
        pcState['额外' + key] = ''

    # 给技能, 豁免, 攻击加上熟练加值
    index = infoStr.find('熟练项:')
    lastIndex = infoStr[index:].find(linesep)
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
        if profItem in PC_SKILL_SYNONYM_DICT.keys():
            profItem = PC_SKILL_SYNONYM_DICT[profItem]

        if profItem in profAbleKeywordList:
            pcState[profItem] += pcState['熟练加值']
            pcState['熟练项'].append(profItem)
        else:
            return f'{profItem}不是有效的熟练关键词, 请查看.角色卡模板'
    # 默认给所有攻击加上熟练加值
    for attack in PC_ATTACK_DICT.keys():
        pcState[attack] += pcState['熟练加值']

    pcState['额外加值'] = []

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

            if checkItem in PC_SKILL_SYNONYM_DICT.keys():
                checkItem = PC_SKILL_SYNONYM_DICT[checkItem]

            if checkItem in checkKeywordList:
                pcState['额外' + checkItem] += addStr
            elif checkItem == '豁免':  # 如: 豁免+2
                for saving in PC_SAVING_DICT.keys():
                    pcState['额外' + saving] += addStr
            elif checkItem == '检定':  # 如: 豁免+2
                for ability in PC_ABILITY_DICT.keys():
                    pcState['额外' + ability] += addStr
                for skill in PC_SKILL_DICT.keys():
                    pcState['额外' + skill] += addStr
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
            if len(hpList) == 1:
                pcState['maxhp'] = int(hpList[0])
            else:
                pcState['maxhp'] = int(hpList[1])
        except ValueError:
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
            bot.UpdateNickName(groupId, userId, nickName)

    if '最大法术位' in infoStr:
        index = infoStr.find('最大法术位:') + 6
        lastIndex = infoStr[index:].find(linesep)
        if lastIndex == -1:
            lastIndex = infoLength
        else:
            lastIndex += index
        command = infoStr[index:lastIndex].strip()
        if command:
            SetSpellSlot(bot, groupId, userId, command)

    if '金钱:' in infoStr:
        index = infoStr.find('金钱:') + 3
        lastIndex = infoStr[index:].find(linesep)
        if lastIndex == -1:
            lastIndex = infoLength
        else:
            lastIndex += index
        command = infoStr[index:lastIndex].strip()
        if command:
            SetMoney(bot, groupId, userId, command)
    return '记录角色卡成功, 查看角色卡请输入.角色卡 或.角色卡 完整\n更多相关功能请查询.help检定, .helphp, .help法术位'


def GetPlayerInfo(bot, groupId: str, userId: str, name: str) -> str:
    try:
        pcState = GetBasicPCState(bot, groupId, userId, isRef=False, autoCreate=False)
        assert pcState['熟练加值']
    except (MasterError, KeyError, AssertionError):
        return f'{name}还没有记录角色卡呢~'

    result = f'姓名:{name}\n'
    if pcState['hp'] != 0 and pcState['maxhp'] != 0:
        result += f'hp:{pcState["hp"]}/{pcState["maxhp"]}\n'

    for ability in PC_ABILITY_DICT.keys():
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
    except KeyError:
        pass

    try:
        moneyList = pcState['金钱']
        result += f'\n金钱:{moneyList[0]}gp'
        if moneyList[1] != 0:
            result += f' {moneyList[1]}sp'
        if moneyList[2] != 0:
            result += f' {moneyList[2]}sp'
    except KeyError:
        pass

    return result


def GetPlayerInfoShort(bot, groupId: str, userId: str, name: str) -> str:
    try:
        pcState = GetBasicPCState(bot, groupId, userId, isRef=False, autoCreate=False)
        assert pcState['熟练加值']
    except (MasterError, KeyError, AssertionError):
        return f'{name}还没有记录角色卡呢~'

    result = name
    try:
        hp = pcState['hp']
        result += f' hp:{hp}'
    except KeyError:
        pass
    try:
        maxhp = pcState['maxhp']
        result += f'/{maxhp}'
    except KeyError:
        pass
    try:
        moneyList = pcState['金钱']
        result += f' 金钱:{moneyList[0]}gp'
        if moneyList[1] != 0:
            result += f' {moneyList[1]}sp'
        if moneyList[2] != 0:
            result += f' {moneyList[2]}cp'
    except KeyError:
        pass
    try:
        currentSlotList = pcState['当前法术位']
        maxSlotList = pcState['最大法术位']
        highestSlot = -1
        for i in range(9):
            if currentSlotList[i] != 0 or maxSlotList[i] != 0:
                highestSlot = i + 1
        assert highestSlot != -1
        result += ' 法术位:'
        for i in range(highestSlot):
            result += f'{currentSlotList[i]}({maxSlotList[i]})/'
        result = result[:-1]
    except (KeyError, AssertionError):
        pass
    return result


def GetPlayerInfoFull(bot, groupId: str, userId: str, name: str) -> str:
    try:
        pcState = GetBasicPCState(bot, groupId, userId, isRef=False, autoCreate=False)
        assert pcState['熟练加值']
    except (MasterError, KeyError, AssertionError):
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
    except KeyError:
        pass
    result += f'熟练加值:{pcState["熟练加值"]}\n'

    for ability in PC_ABILITY_DICT.keys():
        result += f'{ability}:{pcState[ability]} 调整值:{pcState[ability + "调整值"]} '
        result += f'检定:{pcState[ability + "调整值"]}{pcState["额外" + ability]} '
        result += f'豁免:{pcState[ability + "豁免"]}{pcState["额外" + ability + "豁免"]}\n'
    result += f'技能:\n'
    current = '力量调整值'
    for skill in PC_SKILL_DICT.keys():
        if current != PC_SKILL_DICT[skill]:
            result += '\n'
            current = PC_SKILL_DICT[skill]
        result += f'{skill}:{pcState[skill]}{pcState["额外" + skill]}  '
    result = result[:-2]

    try:
        currentSlotList = pcState['当前法术位']
        maxSlotList = pcState['最大法术位']
        highestSlot = -1
        for i in range(9):
            if currentSlotList[i] != 0 or maxSlotList[i] != 0:
                highestSlot = i + 1
        assert highestSlot != -1
        result += '\n法术位:'
        for i in range(highestSlot):
            result += f'{currentSlotList[i]}({maxSlotList[i]})/'
        result = result[:-1]
    except (KeyError, AssertionError, IndexError):
        pass

    return result


def PlayerCheck(bot, groupId: str, userId: str, item: str, times: int, diceCommand: str, nickName: str) -> str:
    try:
        pcState = GetBasicPCState(bot, groupId, userId, isRef=False, autoCreate=False)
        assert pcState['熟练加值']
    except (MasterError, KeyError, AssertionError):
        raise UserError('请先记录角色卡~')

    if times <= 0 or times >= 10:
        raise UserError('次数不合法!')

    if diceCommand.find('抗性') != -1 or diceCommand.find('易伤') != -1:
        raise UserError('抗性与易伤关键字不能出现在此处!')

    if item in PC_SKILL_SYNONYM_DICT.keys():
        item = PC_SKILL_SYNONYM_DICT[item]

    if item not in PC_CHECK_DICT_SHORT.keys():
        if item in PC_ABILITY_DICT.keys():
            itemKeyword = item + '调整值'
        else:
            raise UserError(f'关键字{item}无效~')
    else:
        itemKeyword = item

    # diceCommand 必须为调整值
    if not diceCommand or diceCommand[0] in ['+', '-'] or diceCommand[:2] in ['优势', '劣势']:  # 通过符号判断
        if pcState[itemKeyword] != 0:
            completeCommand = 'd20' + diceCommand + int2str(pcState[itemKeyword]) + pcState['额外' + item]
        else:
            completeCommand = 'd20' + diceCommand + pcState['额外' + item]
        if times != 1:
            completeCommand = f'{times}#{completeCommand}'
        error, resultStr, rollResult = RollDiceCommand(completeCommand)
        if error != 0:
            raise UserError(resultStr)
        checkResult = rollResult.totalValueList[0]
    else:
        raise UserError(f'输入的指令有点问题呢~')

    result = ''
    if '豁免' not in item:  # 说明是属性检定
        result += f'{nickName}在{item}检定中掷出了{resultStr}'
    else:
        result += f'{nickName}在{item}中掷出了{resultStr}'
    if times == 1:
        if rollResult.rawResultList[0][0] == 20:
            result += ' 大成功!'
        elif rollResult.rawResultList[0][0] == 1:
            result += ' 大失败!'
    else:
        succTimes = 0
        failTimes = 0
        for t in range(times):
            if rollResult.rawResultList[t][0] == 20:
                succTimes += 1
            elif rollResult.rawResultList[t][0] == 1:
                failTimes += 1
        if succTimes != 0:
            result += f' {succTimes}次大成功!'
        if failTimes != 0:
            result += f' {failTimes}次大失败!'

    if item == '先攻':
        tb.AddElemToInit(bot, groupId, userId, nickName, '0' + int2str(checkResult), isPC=True)
        result += f'\n已将{nickName}加入先攻列表'
    return result


def ClearPlayerInfo(bot, groupId: str, userId: str) -> None:
    try:
        bot.DelBotData(BotDataT.PC, (groupId, userId))
    except MasterError as e:
        if e.errorType is not KeyError:
            raise e


def UpdateHP(bot, groupId: str, userId: str, targetStr: str, subType: str, hpStr: str, maxhpStr: str,
             nickName: str) -> str:
    maxhp = None
    if subType != '=' and maxhpStr:
        raise UserError('增加或减少生命值的时候不能修改最大生命值哦')
    # 先尝试解读hpStr和maxhpStr
    error, resultStrHp, rollResult = RollDiceCommand(hpStr)
    if error:
        return error
    try:
        hp = rollResult.totalValueList[0]
    except Exception as e:
        print(e)
        raise UserError(f'无法解释生命值参数{hpStr}呢...')
    if hp < 0:
        raise UserError(f'hp数值{resultStrHp}为负数, 没有修改hp数值')

    if maxhpStr:
        try:
            maxhp = int(maxhpStr)
            assert maxhp > 0
        except (ValueError, AssertionError):
            raise UserError(f'无法解释最大生命值参数{maxhpStr}呢...')

    if not targetStr:  # 不指定目标说明要修改自己的生命值信息
        pcState = GetBasicPCState(bot, groupId, userId, isRef=True, autoCreate=True)

        result = ModifyHPInfo(pcState, subType, hp, maxhp, nickName, resultStrHp)
    else:
        targetList = targetStr.split('/')
        result = ''
        for targetStr in targetList:
            # 尝试对先攻列中的目标修改生命值信息
            try:  # 查找已存在的先攻信息
                initInfo = bot.GetBotData(BotDataT.INIT, (groupId,), isRef=True)
            except MasterError as e:  # 如未找到, 返回错误信息
                if e.errorType is KeyError:
                    return '只能指定在先攻列表中的其他角色, 请先建立先攻列表吧~'
                else:
                    raise e

            # 尝试搜索targetStr有关的信息
            if targetStr not in initInfo['initList'].keys():
                possName = []
                for k in initInfo['initList'].keys():
                    if k.find(targetStr) != -1:
                        possName.append(k)
                if len(possName) == 0:
                    return f'在先攻列表中找不到与"{targetStr}"相关的名字哦'
                elif len(possName) > 1:
                    return f'在先攻列表找到多个可能的名字: {[n for n in possName]}'
                else:
                    targetStr = possName[0]

            targetInfo = initInfo['initList'][targetStr]
            # 如果指定的目标是pc, 则直接修改pcStateDict然后返回
            if targetInfo['isPC']:
                targetId = targetInfo['id']
                pcState = GetBasicPCState(bot, groupId, targetId, isRef=False, autoCreate=True)

                resultCur = ModifyHPInfo(pcState, subType, hp, maxhp, targetStr, resultStrHp)
            # 否则修改先攻列表中的信息并保存
            else:
                resultCur = ModifyHPInfo(targetInfo, subType, hp, maxhp, targetStr, resultStrHp)
            if result == '':
                result = resultCur
            else:
                result += '\n' + resultCur

    return result


def CreateHP(bot, groupId: str, userId: str, hp: int = 0, maxhp: int = 0) -> None:
    # 查找已存在的角色卡信息
    pcState = bot.GetBotData(BotDataT.PC, (groupId, userId), isRef=True, autoCreate=True)
    pcState.update({'hp': hp, 'maxhp': maxhp, 'alive': True})


def ClearHP(bot, groupId: str, userId: str) -> None:
    try:
        pcState = bot.GetBotData(BotDataT.PC, (groupId, userId))
        pcState['hp'] = 0
        pcState['maxhp'] = 0
    except (MasterError, KeyError):
        pass


def ShowHP(bot, groupId: str, userId: str) -> str:
    try:
        pcState = bot.GetBotData(BotDataT.PC, (groupId, userId))
        hp = pcState['hp']
        maxhp = pcState['maxhp']
        assert hp != 0 or maxhp != 0
        result = f'当前生命值为{hp}'
        if maxhp != 0:
            result += f'/{maxhp}'
        return result
    except (MasterError, KeyError, AssertionError):
        return '还没有设置生命值呢~'


def SetSpellSlot(bot, groupId: str, userId: str, commandStr: str) -> str:
    # commandStr示例: 4/2/0/0/0/0
    maxSpellSlotList = [0] * 9
    sizeStrList = commandStr.split('/')
    isValid = False
    index = 0
    if len(sizeStrList) > 9:
        raise UserError('唔...法术环位好像最高只有九环呢...')
    for sizeStr in sizeStrList:
        try:
            size = int(sizeStr)
            maxSpellSlotList[index] = size
            assert 0 <= size < 100
            if size > 0:
                isValid = True
        except (ValueError, IndexError, AssertionError):
            raise UserError(f'{index + 1}环法术位大小{sizeStr}无效~')
        index += 1
    if not isValid:
        raise UserError('不会施法就请不要记录法术位咯~')

    pcState = GetBasicPCState(bot, groupId, userId, isRef=True, autoCreate=True)
    pcState['最大法术位'] = maxSpellSlotList
    pcState['当前法术位'] = maxSpellSlotList.copy()
    return '法术环位已经记录好了~'


def ClearSpellSlot(bot, groupId: str, userId: str) -> str:
    try:
        pcState = GetBasicPCState(bot, groupId, userId, isRef=True, autoCreate=False)
        del pcState['最大法术位']
        del pcState['当前法术位']
    except (MasterError, KeyError):
        pass
    return '已经将法术位信息忘记啦~'


def ShowSpellSlot(bot, groupId: str, userId: str) -> str:
    try:
        pcState = GetBasicPCState(bot, groupId, userId, isRef=False, autoCreate=False)
        maxSlotList = pcState['最大法术位']
        currentSlotList = pcState['当前法术位']
    except (MasterError, KeyError):
        raise UserError('还没有记录施法能力哦, 请先使用 .记录法术位 命令吧~')
    result = '当前法术位'
    index = 1
    for maxSize in maxSlotList:
        if maxSize != 0:
            result += f'\n{index}环法术位:{currentSlotList[index - 1]}/{maxSize}'
        index += 1
    return result


def ModifySpellSlot(bot, groupId: str, userId: str, level: int, adjVal: int) -> str:
    # level in [1, 9]
    # adjVal in [-9, 9]
    try:
        pcState = GetBasicPCState(bot, groupId, userId, isRef=True, autoCreate=False)
        currentSlotList = pcState['当前法术位']
    except (MasterError, KeyError):
        raise UserError('还没有记录施法能力哦, 请先使用 .记录法术位 命令吧~')
    preSlot = currentSlotList[level - 1]
    if preSlot + adjVal < 0:
        raise UserError('没有这么多法术位了...')
    currentSlotList[level - 1] += adjVal
    pcState['当前法术位'] = currentSlotList
    if adjVal < 0:
        return f'{level}环法术位减少了{-1 * adjVal}个 ({preSlot}->{preSlot + adjVal})'
    else:
        return f'{level}环法术位增加了{adjVal}个 ({preSlot}->{preSlot + adjVal})'


def SetMoney(bot, groupId: str, userId: str, commandStr: str) -> str:
    reason, moneyList = Str2MoneyList(commandStr)
    pcState = GetBasicPCState(bot, groupId, userId, isRef=True, autoCreate=True)
    pcState['金钱'] = moneyList
    return '牢牢记住你的财富咯~'


def ShowMoney(bot, groupId: str, userId: str) -> str:
    try:
        pcState = GetBasicPCState(bot, groupId, userId, isRef=False, autoCreate=False)
        moneyList = pcState['金钱']
    except (MasterError, KeyError):
        return '现在身无分文呢~ 请先使用 .记录金钱 命令吧~'
    result = f'{moneyList[0]}gp'
    if moneyList[1] != 0:
        result += f' {moneyList[1]}sp'
    if moneyList[2] != 0:
        result += f' {moneyList[2]}cp'
    return result


def ClearMoney(bot, groupId: str, userId: str) -> str:
    try:
        pcState = GetBasicPCState(bot, groupId, userId, isRef=True, autoCreate=False)
        del pcState['金钱']
    except (MasterError, KeyError) as e:
        if e.errorType is not KeyError:
            raise e
    except KeyError:
        pass
    except Exception as e:
        raise MasterError('清空金钱时出现错误', type(e), e)
    return '已经将你的财富忘记啦~'


def ModifyMoney(bot, groupId: str, userId: str, commandStr: str) -> str:
    try:
        pcState = GetBasicPCState(bot, groupId, userId, isRef=True, autoCreate=False)
        moneyList = copy.deepcopy(pcState['金钱'])
    except (MasterError, KeyError):
        raise UserError('现在身无分文呢~ 请先使用 .记录金钱 命令吧~')
    reason, adjList = Str2MoneyList(commandStr)
    totalVal = moneyList[0] * 100 + moneyList[1] * 10 + moneyList[0]
    adjVal = adjList[0] * 100 + adjList[1] * 10 + adjList[0]
    if totalVal + adjVal < 0:
        raise UserError('余额不足, 请及时充值~')
    # 当前的铜币不足以支付要求的铜币, 则用银币或金币换取
    if moneyList[2] + adjList[2] < 0:
        # 加上银币
        if adjList[2] + moneyList[2] + moneyList[1] * 10 < 0:
            # 依然不够则加上金币
            gpNum = math.ceil((adjList[2] + moneyList[2] + moneyList[1] * 10) / -100)
            moneyList[2] = adjList[2] + moneyList[2] + moneyList[1] * 10 + gpNum * 100
            moneyList[1] = 0
            moneyList[0] -= gpNum
        else:
            # 换取部分银币
            spNum = math.ceil((adjList[2] + moneyList[2]) / -10)
            moneyList[2] = adjList[2] + moneyList[2] + spNum * 10
            moneyList[1] -= spNum
    else:
        moneyList[2] = adjList[2] + moneyList[2]

    # 当前的银币不足以支付要求的银币, 则用铜币或金币换取
    if moneyList[1] + adjList[1] < 0:
        # 加上铜币如果仍然不够
        if adjList[1] + moneyList[1] + moneyList[2] // 10 < 0:
            # 再加上金币
            gpNum = math.ceil((adjList[1] + moneyList[1] + moneyList[2] // 10) / -10)
            moneyList[1] = adjList[1] + moneyList[1] + moneyList[2] // 10 + gpNum * 10
            moneyList[2] -= (moneyList[2] // 10) * 10
            moneyList[0] -= gpNum
        else:
            # 换取部分铜币支付
            cpNum = (adjList[1] + moneyList[1]) * -10
            moneyList[1] = 0
            moneyList[2] -= cpNum
    else:
        moneyList[1] = adjList[1] + moneyList[1]

    # 当前的金币不足以支付要求的金币, 则用银币或铜币换取
    if moneyList[0] + adjList[0] < 0:
        # 加上银币
        if adjList[0] + moneyList[0] + moneyList[1] // 10 < 0:
            # 依然不够则加上铜币支付
            cpNum = (adjList[0] + moneyList[0] + moneyList[1] // 10) * -100
            moneyList[0] = 0
            moneyList[1] -= (moneyList[1] // 10) * 10
            moneyList[2] -= cpNum
        else:
            spNum = (adjList[0] + moneyList[0]) * -10
            moneyList[0] = 0
            moneyList[1] -= spNum
    else:
        moneyList[0] = adjList[0] + moneyList[0]
    preMoneyStr = ShowMoney(bot, groupId, userId)
    pcState['金钱'] = moneyList
    curMoneyStr = ShowMoney(bot, groupId, userId)
    return f'的金钱{commandStr} ({preMoneyStr}->{curMoneyStr})'


def JoinTeam(bot, groupId: str, userId: str, name: str) -> str:
    try:
        pcState = GetBasicPCState(bot, groupId, userId, isRef=False, autoCreate=False)
        assert pcState['熟练加值']
    except (MasterError, KeyError):
        raise UserError('必须先记录角色卡才能加入队伍~')

    teamInfo = bot.GetBotData(BotDataT.TEAM, (groupId,), isRef=True, autoCreate=True)
    if name:
        teamInfo['name'] = name
    if userId not in teamInfo['members']:
        teamInfo['members'].append(userId)
    else:
        return f'你已经加入{name}啦~'
    return f'成功加入{name}, 当前共{len(teamInfo["members"])}人。 查看队伍信息请输入 .队伍信息 或 .完整队伍信息'


def ClearTeam(bot, groupId: str) -> str:
    try:
        bot.DelBotData(BotDataT.TEAM, (groupId,))
        return '队伍信息已经删除啦'
    except MasterError:  # 如未找到, 返回错误信息
        return '无法删除不存在的队伍哦'


def ShowTeam(bot, groupId: str) -> str:
    try:
        teamInfo = bot.GetBotData(BotDataT.TEAM, (groupId,), isRef=False, autoCreate=False)
    except MasterError:
        raise UserError('还没有创建队伍哦~')
    name = teamInfo['name']
    result = f'{name}:'
    for uId in teamInfo['members']:
        nickName = bot.GetNickName(groupId, uId)
        result += f'\n{GetPlayerInfoShort(bot, groupId, uId, nickName)}'

    return result


def CallTeam(bot, groupId: str) -> str:
    try:
        teamInfo = bot.GetBotData(BotDataT.TEAM, (groupId,), isRef=False, autoCreate=False)
    except MasterError:
        return '还没有创建队伍哦~'
    result = f'{teamInfo["name"]}的成员快来呀~\n'
    for pId in teamInfo['members']:
        result += f'[CQ:at,qq={pId}] '
    return result[:-1]


def ShowTeamFull(bot, groupId: str) -> str:
    try:
        teamInfo = bot.GetBotData(BotDataT.TEAM, (groupId,), isRef=False, autoCreate=False)
    except MasterError:
        return '还没有创建队伍哦~'
    result = f'{teamInfo["name"]}的完整信息:'

    for uId in teamInfo['members']:
        nickName = bot.GetNickName(groupId, uId)
        result += f'\n----------\n{GetPlayerInfoFull(bot, groupId, uId, nickName)}'
    return result


def LongRest(bot, groupId: str, userId: str) -> str:
    isValidSlot = False
    isValidHp = False
    try:
        pcState = bot.GetBotData(BotDataT.PC, (groupId, userId), isRef=True, autoCreate=False)
    except MasterError:
        raise UserError('请先录入角色卡!')
    try:
        maxSlotList = pcState['最大法术位']
        currentSlotList = pcState['当前法术位']
        isValidSlot = True
    except KeyError:
        maxSlotList, currentSlotList = None, None
        pass
    try:
        hp = pcState['hp']
        maxhp = pcState['maxhp']
        assert maxhp != 0
        isValidHp = True
    except (KeyError, AssertionError):
        hp, maxhp = None, None
        pass
    if not isValidSlot and not isValidHp:
        raise UserError('至少要设置最大生命值和最大法术位中的一项!')
    result = ''
    if isValidHp:
        result = f'\n生命值: {hp}->{maxhp}'
        pcState['hp'] = maxhp
    if isValidSlot:
        result += '\n法术环位:\n'
        for i in range(9):
            if maxSlotList[i] != currentSlotList[i]:
                result += f'{currentSlotList[i]}->{maxSlotList[i]}/'
            else:
                result += f'{maxSlotList[i]}/'
        result = result[:-1]
        pcState['当前法术位'] = maxSlotList.copy()
    return result


def ModifyHPInfo(stateDict, subType, hp, maxhp, name, resultStrHp) -> str:
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

    return result


def Str2MoneyList(commandStr) -> (str, list):
    moneyList = [0, 0, 0]
    gpIndex = commandStr.find('gp')
    spIndex = commandStr.find('sp')
    cpIndex = commandStr.find('cp')
    if gpIndex == -1 and spIndex == -1 and cpIndex == -1:
        try:
            moneyList[0] = int(commandStr)
            return '', moneyList
        except ValueError:
            raise UserError('找不到有效的关键字["gp", "sp", "cp"]')
    if gpIndex != -1:
        try:
            value = int(commandStr[0:gpIndex])
            moneyList[0] = value
            assert -100000000 <= value <= 100000000
            gpIndex += 2
        except (ValueError, AssertionError):
            raise UserError(f'{commandStr[:gpIndex]}不是有效的数额')
    if spIndex != -1:
        startIndex = max(gpIndex, 0)
        try:
            value = int(commandStr[startIndex:spIndex])
            moneyList[1] = value
            assert -100000000 <= value <= 100000000
            spIndex += 2
        except (ValueError, AssertionError):
            raise UserError(f'{commandStr[startIndex:spIndex]}不是有效的数额')
    if cpIndex != -1:
        startIndex = max([0, gpIndex, spIndex])
        try:
            value = int(commandStr[startIndex:cpIndex])
            moneyList[2] = value
            assert -100000000 <= value <= 100000000
        except (ValueError, AssertionError):
            raise UserError(f'{commandStr[startIndex:cpIndex]}不是有效的数额')
    return '', moneyList
