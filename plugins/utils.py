import json
import datetime
import os
import numpy as np
from collections import namedtuple
from enum import Enum, unique

from .type_assert import TypeAssert

# 注意! 有重复字符的长指令必须放在短指令前面, 否则会被覆盖!
commandKeywordList = ['ri', 'r', 'nn', 'jrrp', 'init', 'bot', 'dnd', 'help', 'send']
commandKeywordList += ['查询', 'dismiss', 'draw', '烹饪', '点菜', '今日菜单', '好感度']
commandKeywordList += ['记录角色卡', '角色卡模板', '角色卡模版','查看角色卡', '完整角色卡', '清除角色卡', '角色卡']
commandKeywordList += ['加入队伍', '队伍信息', '完整队伍信息', '清除队伍', '记录金钱', '清除金钱', '查看金钱', '金钱']
commandKeywordList += ['savedata', 'credit', 'notice']
commandKeywordReList = ['.*检定', '.*豁免', '.*法术位', '.*hp', '^[1-9]环']

@unique
class CommandType(Enum):
    MASTER = 999
    Roll = 0
    NickName = 1
    JRRP = 2
    INIT = 3
    RI = 4
    SETHP = 5
    SHOWHP = 6
    CLRHP = 7
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


@unique
class CoolqCommandType(Enum):
    DISMISS = 0
    MESSAGE = 1


pcAbilityDict = {'力量':'力量调整值', '敏捷':'敏捷调整值', '体质':'体质调整值',
                '智力':'智力调整值', '感知':'感知调整值', '魅力':'魅力调整值'}
pcSavingDict = {'力量豁免':'力量调整值', '敏捷豁免':'敏捷调整值', '体质豁免':'体质调整值',
                '智力豁免':'智力调整值', '感知豁免':'感知调整值', '魅力豁免':'魅力调整值', '死亡豁免':'无调整值'}
pcSkillDict = {'运动':'力量调整值', '体操':'敏捷调整值', '巧手':'敏捷调整值', '隐匿':'敏捷调整值', '先攻':'敏捷调整值',
               '奥秘':'智力调整值', '历史':'智力调整值', '调查':'智力调整值', '自然':'智力调整值', '宗教':'智力调整值',
               '驯兽':'感知调整值', '洞悉':'感知调整值', '医药':'感知调整值', '察觉':'感知调整值', '求生':'感知调整值',
               '欺瞒':'魅力调整值', '威吓':'魅力调整值', '表演':'魅力调整值', '游说':'魅力调整值'}

pcSkillSynonymDict = {'特技':'体操', '潜行':'隐匿', '隐蔽':'隐匿', '躲藏':'隐匿', '驯养':'驯兽', '驯服':'驯兽', '医疗':'医药',
                       '医术':'医药', '观察':'察觉', '生存':'求生', '欺骗':'欺瞒', '哄骗':'欺瞒', '唬骗':'欺瞒', '威胁':'威吓',
                       '妙手':'巧手', '说服':'游说'}
pcCheckDictShort = {**pcSavingDict, **pcSkillDict}
pcCheckDictLong = {**pcAbilityDict, **pcCheckDictShort}

pcSheetTemplate = '姓名:约翰\nhp:30/50\n力量:16 敏捷:13 体质:16 智力:10 感知:14 魅力:8\n熟练加值:3  熟练项:力量豁免/体质豁免/运动/威吓/察觉/洞悉\n额外加值:豁免+1/检定+1/先攻+2/说服+1d4\n最大法术位:4/3/3/1\n金钱:50gp 30sp'

    
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
    
def GetCurrentDateStr():
    china_tz = datetime.timezone(datetime.timedelta(hours=8), '北京时间')
    current_date = datetime.datetime.now(china_tz)
    return current_date.strftime('%Y_%m_%d_%H_%M_%S')

def GetCurrentDateRaw():
    china_tz = datetime.timezone(datetime.timedelta(hours=8), '北京时间')
    current_date = datetime.datetime.now(china_tz)
    return current_date

def Str2Datetime(inputStr):
    return datetime.datetime.strptime(inputStr, '%Y_%m_%d_%H_%M_%S')

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