import numpy as np
import datetime

from .utils import *

# 将一个字符串分割为一个骰子列表, 然后输出最终结果 [异常值， 结果字符串， 结果数值]
@TypeAssert(str)
def RollDiceCommond(diceCommand) -> (int, str, int):
    diceCommand = diceCommand.upper()
    diceCommand = diceCommand.replace(' ', '')
    
    if len(diceCommand) == 0:
        return -1, '命令表达式为空!', None
    
    diceList = []

    # 处理关于 # 的部分
    repeatTime = 1
    hashIndex = diceCommand.find('#')
    if hashIndex != -1:
        # 如果找到一个
        try:
            repeatTime = int(diceCommand[:hashIndex])
            assert repeatTime >= 1
            assert repeatTime <= 10
        except:
            return -1, f'{diceCommand[:hashIndex]}必须是大于等于1, 小于等于10的整数', None
        try:
            diceCommand = diceCommand[hashIndex+1:]
        except:
            return -1, f'#后的内容必须为有效的骰子表达式', None

    splitKeys = ['+', '-']
    
    splitIndex = 0
    # 利用分隔符将不同投骰部分分隔开
    for i in range(1, len(diceCommand)):
        if diceCommand[i] in splitKeys:
            if splitIndex == i-1 and splitIndex != 0:
                return -1, f'连续遇到两个符号:{diceCommand}', None
            dice = diceCommand[splitIndex:i]
            diceList.append(dice)
            splitIndex = i
    diceList.append(diceCommand[splitIndex:])
    
    # ---------- 暂时这样处理默认骰
    length = 0 # 用于记录在diceCommand的哪个部分插入默认骰
    defaultDiceType = '20'
    for i in range(len(diceList)):
        length += len(diceList[i])
        if diceList[i][-1] == 'D': 
            diceList[i] += defaultDiceType
            diceCommand = diceCommand[:length] + defaultDiceType + diceCommand[length:]
        elif len(diceList[i])>=3 and (diceList[i][-3:] == 'D优势' or diceList[i][-3:] == 'D劣势'):
            diceList[i] = diceList[i][:-2] + defaultDiceType + diceList[i][-2:]
            diceCommand = diceCommand[:length-2] + defaultDiceType + diceCommand[length-2:]

    if repeatTime == 1:
        # 如果不重复直接返回结果
        error, answer, totalValue = RollDiceList(diceList)
        if error != 0:
            return -1, answer, None
        output = f'{diceCommand}={answer}'
    else:
        # 重复多次则在结果中加入第x次的标注
        output = f'{repeatTime}次{diceCommand}=' + '{\n'
        for i in range(repeatTime):
            error, answer, totalValue = RollDiceList(diceList)
            if error != 0:
                return -1, answer, None
            output += f'{answer}'
            if i != repeatTime-1:
                output += '\n'

        output += ' }'
        totalValue = None

    return 0, output, totalValue

# 接受一个骰子列表, 返回结果字符串和总值
@TypeAssert(list)
def RollDiceList(diceList)->(int, str, int):
    # 生成随机种子
    np.random.seed(np.random.seed(datetime.datetime.now().microsecond+np.random.randint(10000)))
    finalAnswer = ''
    totalValue = 0
    answerList = []

    # diceList示例 ['+D20','-1', '+1D4', 'D']
    for dice in diceList:
        error, answer, value = RollDice(dice)
        if error != 0:
            return -1, f'执行{dice}时遇到了问题:{answer}', None
        answerList.append(answer)
        totalValue += value
    length = len(answerList)

    finalAnswer += answerList[0]
    for i in range(1,length):
        if answerList[i][0] != '-':
            finalAnswer += '+'
        finalAnswer += answerList[i]

    # 如果结果个数多于一个, 显示总和
    if len(answerList) > 1 or answerList[0].find('(') != -1:
        finalAnswer += f'={totalValue}'
    return 0, finalAnswer, totalValue

@TypeAssert(str)
def RollDice(diceStr)->(int, str, int):
    # 接受单个骰子命令， 如'2D6'，'+d4', '5'
    # 返回[异常值， 结果字符串， 结果值]
    # 注意, 返回的第二个参数开头必然不会以'+'开头
    scale = 1
    diceNum = 1
    diceType = None
    result = None
    
    splitIndex = diceStr.find('D')
    
    # 如果没有找到D, 尝试把整个表达式变为数字, 失败则报错
    if splitIndex == -1:
        try:
            result = int(diceStr)
        except:
            errorInfo = diceStr+'不是有效的表达式'
            print(errorInfo)
            return -1, errorInfo, None
        return 0, str(result), result
    
    strFormer = diceStr[:splitIndex] # D之前的部分
    strLater = diceStr[splitIndex+1:] # D之后的部分
    
    # 前面部分
    # 如果不是以D开头
    if splitIndex != 0:
        if strFormer[0] == '+': #如果开头是+则
            scale = 1
            strFormer = strFormer[1:]
        elif strFormer[0] == '-':
            scale = -1
            strFormer = strFormer[1:]
        # 如果前面部分除去符号后不是空白，尝试识别骰子数量
        if len(strFormer) > 0:
            try:
                diceNum = int(strFormer)
                assert diceNum >= 1 and diceNum <= 100
            except:
                return -1, '骰子数量需为1至100的整数', None
    
    # 后半部分
    # 先检查有无优势或劣势或K
    advIndex = strLater.find('优势')
    disadvIndex = strLater.find('劣势')
    keepIndex = strLater.find('K')

    if (advIndex != -1 or disadvIndex != -1) and keepIndex != -1:
        return -1, '优势或劣势不能与K(取最高值)并存', None

    if advIndex != -1 and disadvIndex != -1:
        return -1, '不能同时存在优势和劣势', None
    elif advIndex != -1 and diceNum == 1: # 优势
        strLater = strLater[:advIndex]
        diceNum = 2
    elif disadvIndex != -1 and diceNum == 1: # 劣势
        strLater = strLater[:disadvIndex]
        diceNum = 2
    elif (advIndex != -1 or disadvIndex != -1) and diceNum != 1:
        return -1, '优势和劣势骰数量只能为1', None

    if keepIndex != -1:
        try:
            keepMaxNum = int (strLater[keepIndex+1:])
            assert keepMaxNum <= diceNum
        except:
            return -1, '保留骰子数目必须小于等于总骰子数目', None
        strLater = strLater[:keepIndex]

    # 查看骰子面数
    # if strLater == '' :
    #     # 如果没有给出数值, 则默认使用20面骰
    #     diceType = 20
    try:
        diceType = int(strLater)
        assert diceType <= 1000 and diceType >=1
    except:
        return -1, strLater+'无效, 骰子面数需为1至1000之间的整数', None
    
    # 获取随机结果
    result = []
    for i in range(diceNum):
        result.append(scale*np.random.randint(1, diceType+1))

    # 生成返回字符串, 保证第一个数字不会是+, 但可以是-
    if diceNum == 1: # 只投一次就直接返回结果
        return 0, str(result[0]), result[0]
    else:
        if advIndex != -1: # 优势
            final = max(result[0], result[1])
            return 0, f'Max{result[0], result[1]}', final
        elif disadvIndex != -1: # 劣势
            final = min(result[0], result[1])
            return 0, f'Min{result[0], result[1]}', final
        elif keepIndex != -1: # 保留的情况
            if len(result) < 20: # 总骰子数小于20个
                final = 0
                answer = ''
                for r in result:
                    answer += int2str(r)
                if answer[0] =='+':
                    answer = answer[1:]
                result = sorted(result, reverse = True)[:keepMaxNum]
                keepAnswer = ''
                for r in result:
                    final += r
                    keepAnswer += int2str(r)
                if keepAnswer[0] =='+':
                    keepAnswer = keepAnswer[1:]
                if keepMaxNum == 1:
                    answer = f'Max({answer})={keepAnswer}'
                else:
                    answer = f'Max{keepMaxNum}({answer})={keepAnswer}'
                return 0, f'{answer}', final
            else:
                final = 0
                result = sorted(result, reverse = True)[:keepMaxNum]
                for r in result:
                    final += r
                return 0, f'{final}', final
        # 普通投骰
        elif len(result) < 20: # 少于20个骰子则返回所有结果
            final = 0
            answer = ''
            for r in result:
                final += r
                answer += int2str(r)
            if answer[0] =='+':
                answer = answer[1:]
            return 0, f'({answer})', final
        else: # 多于20个骰子则只返回总和
            final = 0
            for r in result:
                final += r
            return 0, f'{final}', final
        
        
@TypeAssert(str)
def SplitDiceCommand(inputStr)->(str, str):
    # 将投掷表达式与后面的无关部分分开
    # 如SplitDiceCommand('d20优势+5攻击地精')将返回('d20优势+5', '攻击地精')
    singleKeywords = ['+', '-', 'k', 'd', '#', ' ', '\n'] + [str(i) for i in range(10)]
    doubleKeywords = ['优势', '劣势']
    inputStr = inputStr.replace(' ', '')
    splitIndex = 0 # splitIndex以及之后的内容都是无关内容
    while splitIndex < len(inputStr):
        if inputStr[splitIndex] in singleKeywords:
            splitIndex += 1
        else:
            try:
                assert inputStr[splitIndex:splitIndex+2] in doubleKeywords
                splitIndex += 2
            except:
                break
                
    return inputStr[:splitIndex], inputStr[splitIndex:]