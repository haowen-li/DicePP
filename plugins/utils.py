import json
import datetime
import os
import numpy as np
from collections import namedtuple
from enum import Enum, unique

from .type_assert import TypeAssert

# 注意! 有重复字符的长指令必须放在短指令前面, 否则会被覆盖!
commandKeywordList = ['ri', 'r', 'nn', 'jrrp', 'init', 'bot', 'dnd', 'help', 'send', 'welcome']
commandKeywordList += ['查询', '索引', 'dismiss', 'draw', '烹饪', '点菜', '今日菜单', '好感度', '今日笑话']
commandKeywordList += ['记录角色卡', '角色卡模板', '角色卡模版','查看角色卡', '完整角色卡', '清除角色卡', '角色卡']
commandKeywordList += ['加入队伍', '队伍信息', '完整队伍信息', '清除队伍', '记录金钱', '清除金钱', '查看金钱', '队伍金钱', '金钱' ,'长休']
commandKeywordList += ['记录笔记', '查看笔记', '清除笔记', '笔记']
commandKeywordList += ['savedata', 'credit', 'notice', 'dailyprofile']
commandKeywordReList = ['^([1-9]#)?..检定', '^([1-9]#)?..豁免', '^([1-9]#)?..攻击', '.*法术位', '.*hp', '^[1-9]环']
commandKeywordReList += ['^队伍..检定']

@unique
class CommandType(Enum):
    MASTER = 999
    Roll = 0
    NickName = 1
    JRRP = 2
    INIT = 3
    RI = 4
    HP = 5
    WELCOME = 6
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

dndCommandDict = {CommandType.Roll, CommandType.INIT, CommandType.RI, CommandType.HP, CommandType.QUERY, CommandType.INDEX, CommandType.PC, 
                 CommandType.CHECK, CommandType.SpellSlot, CommandType.TEAM, CommandType.MONEY, CommandType.REST,
                 CommandType.TeamCheck,  CommandType.TeamMoney}


@unique
class CoolqCommandType(Enum):
    DISMISS = 0
    MESSAGE = 1

china_tz = datetime.timezone(datetime.timedelta(hours=8), '北京时间')
    
class Command():
    # 命令类, 用来存放命令类型和参数
    def __init__(self, cType, cArg):
#         assert isinstance(cType, CommandType), f'Type of {cType} is not {CommandType}'
#         assert isinstance(cArg, list)
        self.cType = cType
        self.cArg = cArg
        
    def equal(self, otherCommand, info = True):
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
    @TypeAssert(coolqCommand = CoolqCommandType, resultStr = str, personIdList = list, groupIdList = list)
    def __init__(self, coolqCommand, resultStr = None, personIdList = None, groupIdList = None):
        self.coolqCommand = coolqCommand
        self.resultStr = resultStr
        self.personIdList = personIdList
        self.groupIdList = groupIdList


class TypeValueError(Exception):
    # 自定义的错误类型, 可以通过方法增加错误信息
    def __init__(self, arg):
        self.args = arg
        
    def attachInfoAfter(arg):
        self.args += arg
        
    def attachInfoBefore(arg):
        self.args = arg+self.args
        
def ChineseToEnglishSymbol(inputStr):
    # 将中文字符串转为英文
    if type(inputStr) != str:
        raise TypeValueError(f'ChineseToEnglishSymbol: Input {inputStr} must be str type')
#     if len(inputStr) != 1:
#         raise TypeValueError(f'ChineseToEnglishSymbol: length of Input {inputStr} must be 1')   
    inputStr = inputStr.replace('。', '.')
    inputStr = inputStr.replace('，', ',')
    inputStr = inputStr.replace('＋', '+')
    inputStr = inputStr.replace('－', '-')
    inputStr = inputStr.replace('＃', '#')
    inputStr = inputStr.replace('：', ':')
    return inputStr

# 将中文数字转为int类型
def ChineseNumberToInt(inputChar):
    if inputChar == '零': return 0
    elif inputChar == '一': return 1
    elif inputChar == '二': return 2
    elif inputChar == '三': return 3
    elif inputChar == '四': return 4
    elif inputChar == '五': return 5
    elif inputChar == '六': return 6
    elif inputChar == '七': return 7
    elif inputChar == '八': return 8
    elif inputChar == '九': return 9
    raise TypeValueError(f'ChineseNumberToInt: Input {inputStr} is invalid')

def int2str(value, with_symbol = True):
    assert type(value) == int
    if with_symbol and value >= 0:
        return '+' + str(value)
    else:
        return str(value)
    
def UpdateJson(jsonFile, path):
    with open(path,"w", encoding='utf-8') as f:
        json.dump(jsonFile,f,ensure_ascii=False)

def ReadJson(path):
    with open(path,"r", encoding='utf-8') as f:
        js = f.read()
        jsonFile = json.loads(js)
        return jsonFile

async def UpdateJsonAsync(jsonFile, path):
    with open(path,"w", encoding='utf-8') as f:
        json.dump(jsonFile,f,ensure_ascii=False)
    
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

@TypeAssert(inputList = list)
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

@TypeAssert(substring = str)
def PairSubstring(substring, strList)->list:
    possibleResult = []
    for strCur in strList:
        if strCur.find(substring) != -1:
            possibleResult.append(strCur)
    return possibleResult