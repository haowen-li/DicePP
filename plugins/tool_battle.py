from info_help import *
from utils import *
from info_chat import *
from tool_dice import *
import data_template as dt

def GetInitSummary(bot, groupId: str) -> str:
    try: #查找已存在的先攻信息
        initInfo = bot.GetBotData(BotDataT.INIT, (groupId, ))
    except MasterError as e: #如未找到, 返回错误信息
        if e.errorType is KeyError:
            raise UserError(INIT_MISS_STR)
        else:
            raise e
    
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

def ClearInit(bot, groupId: str) -> str:
    # 清空先攻信息
    try:
        bot.DelBotData(BotDataT.INIT, (groupId,))
    except MasterError as e:
        if e.errorType is KeyError:
            return INIT_CLEAR_FAIL_STR
        else:
            raise e
    return INIT_CLEAR_STR

def RemoveElemFromInit(bot, groupId: str, name: str) -> str:
    # 将一个对象从先攻列表中删除
    try: #查找已存在的先攻信息
        initInfo = bot.GetBotData(BotDataT.INIT, (groupId, ), isRef = True)
    except MasterError as e: #如未找到, 返回错误信息
        if e.errorType is KeyError:
            raise UserError(INIT_MISS_STR)
        else:
            raise e

    # 如果没有在先攻列表中找到指定的名字, 尝试搜索名字
    if not name in initInfo['initList'].keys():
        possName = []
        for k in initInfo['initList'].keys():
            if k.find(name) != -1:
                possName.append(k)
        if len(possName) == 0:
            raise UserError(INIT_REMOVE_FAIL_STR.format(name = name))
        if len(possName) > 1:
            raise UserError(INIT_REMOVE_MULT_STR.format(val = [ n for n in possName]))
        name = possName[0]

    del initInfo['initList'][name]
    return INIT_REMOVE_STR.format(name = name)

def AddElemToInit(bot, groupId: str, userId: str, name: str, initAdj: str, isPC: bool) -> str:
    #查找已存在的先攻信息
    initInfo = bot.GetBotData(BotDataT.INIT, (groupId, ), isRef = True, autoCreate = True)

    if initAdj.find('抗性') != -1 or initAdj.find('易伤') != -1:
        raise UserError('抗性与易伤关键字不能出现在此处!')
        
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
                    initInfo['initList'][nameMulti] = dt.initInfoTemp
                    initInfo['initList'][nameMulti].update({'id':userId, 'init':initResult, 'hp':hp, 'maxhp':maxhp, 'alive':True, 'isPC':isPC})
                result = f'{nameListStr.strip()}先攻:{resultStr}'
                flag = False
            except Exception as e:
                flag = False
                raise UserError(f'关于{name}的先攻指令不正确:{e}')
    if flag:
        initInfo['initList'][name] = dt.initInfoTemp
        initInfo['initList'][name].update({'id':userId, 'init':initResult, 'hp':hp, 'maxhp':maxhp, 'alive':True, 'isPC':isPC})
        result = f'{name}先攻:{resultStr}'
    try:
        if GetCurrentDateRaw() - Str2Datetime(initInfo['date']) > datetime.timedelta(hours=1):
            result += '\n' + INIT_WARN_STR
        initInfo['date'] = GetCurrentDateStr()
    except:
        pass
    return result