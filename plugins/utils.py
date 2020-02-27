import json
import datetime
import os
from collections import namedtuple
from enum import Enum, unique

from .type_assert import TypeAssert

# 注意! 有重复字符的长指令必须放在短指令前面, 否则会被覆盖!
commandKeywordList = ['ri', 'r', 'nn', 'jrrp', 'init', 'sethp', 'bot', 'dnd', 'help', '查询']

@unique
class CommandType(Enum):
    Roll = 0
    NickName = 1
    JRRP = 2
    INIT = 3
    RI = 4
    SETHP = 5
    BOT = 6
    DND = 7
    HELP = 8
    QUERY = 9
    
# @TypeAssert(CommandType, list)
class Command():
    # 命令类, 用来存放命令类型和参数
    def __init__(self, cType, cArg, personId = None, groupId = None):
#         assert isinstance(cType, CommandType), f'Type of {cType} is not {CommandType}'
#         assert isinstance(cArg, list)
        self.cType = cType
        self.cArg = cArg
        self.personId = personId
        self.groupId = groupId
        
        if cType == CommandType.Roll:
            assert len(cArg) == 2, '投骰命令必须有两个参数!'
        
    def equal(self, otherCommand, info = True):
        if self.cType != otherCommand.cType:
            if info:
                print(f'{self.cType} != {otherCommand.cType}')
            return False
        if self.cArg != otherCommand.cArg:
            if info:
                print(f'{self.cArg} != {otherCommand.cArg}')
            return False
        if self.personId != otherCommand.personId:
            if info:
                print(f'{self.personId} != {otherCommand.personId}')
            return False
        if self.groupId != otherCommand.groupId:
            if info:
                print(f'{self.groupId} != {otherCommand.groupId}')
            return False
        return True
    
    def show(self):
        return (self.cType, self.cArg, self.personId, self.groupId)

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
#     newStr = inputStr
#     for i in range(len(inputStr)):
#         char = inputStr[i]
#         if char == '。':
#             newStr[i] = '.'
#         if char == '，':
#             newStr[i] = ','
#         if char == '＋':
#             newStr[i] = '+'
#         if char == '－':
#             newStr[i] = '-'
    return inputStr

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
    
def GetCurrentDate():
    china_tz = datetime.timezone(datetime.timedelta(hours=8), '北京时间')
    current_date = datetime.datetime.now(china_tz)
    return current_date.strftime('%Y_%m_%d_%H_%M_%S')

def GetCurrentDateRaw():
    china_tz = datetime.timezone(datetime.timedelta(hours=8), '北京时间')
    current_date = datetime.datetime.now(china_tz)
    return current_date