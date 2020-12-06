import json
import datetime
import numpy as np
from enum import Enum, IntEnum, unique

# 注意! 有重复字符的长指令必须放在短指令前面, 否则会被覆盖!
commandKeywordList = ['ri', 'r', 'nn', 'jrrp', 'init', 'bot', 'dnd', 'help', 'send', 'welcome', 'name']
commandKeywordList += ['查询', '索引', 'dismiss', 'draw', '烹饪', '点菜', '今日菜单', '好感度', '今日笑话', '昨日笑话', '明日笑话']
commandKeywordList += ['记录角色卡', '角色卡模板', '角色卡模版', '查看角色卡', '完整角色卡', '清除角色卡', '角色卡']
commandKeywordList += ['加入队伍', '队伍信息', '完整队伍信息', '清除队伍', '队伍点名']
commandKeywordList += ['记录金钱', '清除金钱', '查看金钱', '队伍金钱', '金钱', '长休']
commandKeywordList += ['记录笔记', '查看笔记', '清除笔记', '笔记', '答题']
commandKeywordList += ['群管理']
commandKeywordList += ['savedata', 'credit', 'notice', 'dp', 'debug']
commandKeywordReList = ['^([1-9]#)?..检定', '^([1-9]#)?..豁免', '^([1-9]#)?..攻击', '.*法术位', '.*hp', '^[1-9]环']
commandKeywordReList += ['^队伍..检定']


@unique
class CommandType(IntEnum):
    MASTER = 999
    Roll = 0
    NickName = 1
    JRRP = 2
    INIT = 3
    RI = 4
    HP = 5
    WELCOME = 6
    NAME = 7
    BOT = 8
    DND = 9
    HELP = 10
    QUERY = 11
    DISMISS = 12
    DRAW = 13
    COOK = 14
    ORDER = 15
    TodayMenu = 16
    PC = 17
    CHECK = 18
    SEND = 19
    SpellSlot = 20
    TEAM = 21
    MONEY = 22
    CREDIT = 23
    TodayJoke = 24
    REST = 25
    NOTE = 26
    TeamCheck = 27
    TeamMoney = 28
    INDEX = 29
    Question = 30
    GROUP = 31


Str2CommandTypeDict = {'查询': {CommandType.QUERY, CommandType.INDEX},
                       '先攻': {CommandType.INIT, CommandType.RI},
                       '今日笑话': {CommandType.TodayJoke},
                       '今日人品': {CommandType.JRRP},
                       '掷骰': {CommandType.Roll},
                       '抽卡': {CommandType.DRAW},
                       '烹饪': {CommandType.COOK, CommandType.ORDER, CommandType.TodayMenu}}

dndCommandDict = {CommandType.Roll, CommandType.INIT, CommandType.RI, CommandType.HP, CommandType.QUERY,
                  CommandType.INDEX, CommandType.PC,
                  CommandType.CHECK, CommandType.SpellSlot, CommandType.TEAM, CommandType.MONEY, CommandType.REST,
                  CommandType.TeamCheck, CommandType.TeamMoney}


@unique
class CoolqCommandType(Enum):
    DISMISS = 0
    MESSAGE = 1


@unique
class BotDataT(Enum):
    USER = 0
    GROUP = 1
    GROUP_MEMBER = 2
    INIT = 3
    PC = 4
    TEAM = 5
    QUES = 6
    QUERY = 7
    QUERY_SYN = 8
    DECK = 9
    DISH = 10
    JOKE = 11


def BotDataT2Str(botDataT: BotDataT):
    if botDataT == BotDataT.USER:
        dataStr = '用户'
    elif botDataT == BotDataT.GROUP:
        dataStr = '群'
    elif botDataT == BotDataT.GROUP_MEMBER:
        dataStr = '群成员'
    elif botDataT == BotDataT.INIT:
        dataStr = '先攻'
    elif botDataT == BotDataT.PC:
        dataStr = '角色卡'
    elif botDataT == BotDataT.TEAM:
        dataStr = '队伍'
    elif botDataT == BotDataT.QUES:
        dataStr = '答题'
    elif botDataT == BotDataT.QUERY:
        dataStr = '查询'
    elif botDataT == BotDataT.QUERY_SYN:
        dataStr = '查询同义词'
    elif botDataT == BotDataT.DECK:
        dataStr = '牌库'
    elif botDataT == BotDataT.DISH:
        dataStr = '菜谱'
    elif botDataT == BotDataT.JOKE:
        dataStr = '笑话'
    else:
        dataStr = str(botDataT)
    return dataStr


china_tz = datetime.timezone(datetime.timedelta(hours=8), '北京时间')


class Command():
    # 命令类, 用来存放命令类型和参数
    def __init__(self, cType, cArg):
        #         assert isinstance(cType, CommandType), f'Type of {cType} is not {CommandType}'
        #         assert isinstance(cArg, list)
        self.cType = cType
        self.cArg = cArg

    def equal(self, otherCommand, info=True):
        if self.cType != otherCommand.cType:
            if info:
                print(f'{self.cType} != {otherCommand.cType}')
            return False
        if self.cArg != otherCommand.cArg:
            if info:
                print(f'{self.cArg} != {otherCommand.cArg}')
            return False
        return True


class CommandResult():
    def __init__(self, coolqCommand, resultStr=None, personIdList=None, groupIdList=None):
        self.coolqCommand = coolqCommand
        self.resultStr = resultStr
        self.personIdList = personIdList
        self.groupIdList = groupIdList


# class TypeValueError(Exception):
#     # 自定义的错误类型, 可以通过方法增加错误信息
#     def __init__(self, arg):
#         self.args = arg
#
#     def attachInfoAfter(self, arg):
#         self.args += arg
#
#     def attachInfoBefore(self, arg):
#         self.args = arg + self.args


class MasterError(Exception):
    # 会向管理员汇报的异常, 包括期待被其他函数处理的异常(如果没有处理, 最后会向管理员汇报)
    def __init__(self, info: str, errorType: type = None, rawError: Exception = None):
        self.info = info
        self.errorType = errorType
        self.rawError = rawError

    def __str__(self):
        errorTypeStr = '未设定类型'
        rawErrorStr = '未知'
        if self.errorType:
            errorTypeStr = self.errorType.__name__
        if self.rawError:
            rawErrorStr = str(self.rawError)

        return f'错误类型:{errorTypeStr}\n信息:{self.info}\n源信息:\n{rawErrorStr}'


class UserError(Exception):
    # 会直接向用户汇报的异常
    def __init__(self, info: str):
        self.info = info

    def __str__(self):
        return self.info


# 一些通用函数
def ChineseToEnglishSymbol(inputStr):
    # 将中文字符串转为英文
    if type(inputStr) != str:
        raise ValueError(f'ChineseToEnglishSymbol: Input {inputStr} must be str type')
    inputStr = inputStr.replace('。', '.')
    inputStr = inputStr.replace('，', ',')
    inputStr = inputStr.replace('＋', '+')
    inputStr = inputStr.replace('➕', '+')
    inputStr = inputStr.replace('－', '-')
    inputStr = inputStr.replace('➖', '-')
    inputStr = inputStr.replace('＝', '=')
    inputStr = inputStr.replace('＃', '#')
    inputStr = inputStr.replace('：', ':')
    return inputStr


# 将中文数字转为int类型
def ChineseNumberToInt(inputChar):
    if inputChar == '零':
        return 0
    elif inputChar == '一':
        return 1
    elif inputChar == '二':
        return 2
    elif inputChar == '三':
        return 3
    elif inputChar == '四':
        return 4
    elif inputChar == '五':
        return 5
    elif inputChar == '六':
        return 6
    elif inputChar == '七':
        return 7
    elif inputChar == '八':
        return 8
    elif inputChar == '九':
        return 9
    raise ValueError(f'ChineseNumberToInt: Input {inputChar} is invalid')


def int2str(value, with_symbol=True):
    assert type(value) == int
    if with_symbol and value >= 0:
        return '+' + str(value)
    else:
        return str(value)


def UpdateJson(jsonFile, path):
    with open(path, "w", encoding='utf-8') as f:
        json.dump(jsonFile, f, ensure_ascii=False)


def ReadJson(path):
    with open(path, "r", encoding='utf-8') as f:
        js = f.read()
        jsonFile = json.loads(js)
        return jsonFile


async def UpdateJsonAsync(jsonFile, path):
    with open(path, "w", encoding='utf-8') as f:
        json.dump(jsonFile, f, ensure_ascii=False)


def GetCurrentDateStr():
    current_date = datetime.datetime.now(china_tz)
    return current_date.strftime('%Y_%m_%d_%H_%M_%S')


def GetCurrentDateRaw():
    current_date = datetime.datetime.now(china_tz)
    return current_date


def Str2Datetime(inputStr):
    result = datetime.datetime.strptime(inputStr, '%Y_%m_%d_%H_%M_%S')
    result = result.replace(tzinfo=china_tz)
    return result


def Datetime2Str(inputDatetime):
    return inputDatetime.strftime('%Y_%m_%d_%H_%M_%S')


def SetNumpyRandomSeed():
    np.random.seed(np.random.randint(10000))


def RandomSelectList(inputList, num=1):
    assert num >= 1
    length = len(inputList)
    if num == 1:
        return [inputList[np.random.randint(length)]]
    else:
        result = []
        if length <= num:
            for i in np.random.permutation(length):
                result.append(inputList[i])
        else:
            for i in np.random.permutation(length)[:num]:
                result.append(inputList[i])
        return result


def PairSubstring(substring, strList) -> list:
    # 子串匹配
    possibleResult = []
    for strCur in strList:
        if strCur.find(substring) != -1:
            possibleResult.append(strCur)
    return possibleResult


def PairSubstringList(substringList, strList) -> list:
    # 多子串匹配
    possResult = []
    for strCur in strList:
        isPoss = True
        for keyword in substringList:
            if strCur.find(keyword) == -1:
                isPoss = False
                break
        if isPoss:
            possResult.append(strCur)
    return possResult


def DeleteInvalidInfo(targetDict, sourceKeys):
    # 只保留键在sourceKeys中的targetDict条目
    invalidGroupId = []
    for gId in targetDict.keys():
        if not gId in sourceKeys:
            invalidGroupId.append(gId)
    for gId in invalidGroupId:
        del targetDict[gId]
