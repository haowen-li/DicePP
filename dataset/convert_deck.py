import numpy as np
import os
import argparse
import json
import re

def isDiceCommand(inputStr)->(bool):
    # 判断一个字符串是不是合法的投骰表达式
    singleKeywords = ['+', '-', 'k', 'd', '#'] + [str(i) for i in range(10)]
    doubleKeywords = ['优势', '劣势', '抗性', '易伤']
    inputStr = inputStr.replace(' ', '')
    splitIndex = 0
    hasContent = False
    while splitIndex < len(inputStr):
        if inputStr[splitIndex] in singleKeywords:
            if inputStr[splitIndex] == '#':
                hasContent == False
            else:
                hasContent = True
            splitIndex += 1
        else:
            try:
                assert inputStr[splitIndex:splitIndex+2] in doubleKeywords
                splitIndex += 2
            except:
                return False
    if hasContent:
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=str, dest = 'file', help='file name, must be txt format')

    fileName = parser.parse_args().file
    
    deckTitle = ''
    deckList = []
    deckRelayList = []
    deckDict = {}
    totalWeight = 0
    keyList = [['WEIGHT', re.compile('WEIGHT\(.*?\)')], ['ROLL', re.compile('ROLL\(.*?\)')],
               ['DRAW', re.compile('DRAW\(.*?\)')], ['END', re.compile('END\(\)')]]
    with open(fileName, 'r', encoding="utf-8-sig") as f:
        data = f.readline().strip()
        deckTitle = data
        data = f.readline().strip()
        if data[:3] == '依赖:':
            deckRelayList = data[3:].split('/')
            deckRelayList = [relay.strip() for relay in deckRelayList]
            data = f.readline().strip()
        while data:
            weight = 1
            end = False
            rawContent = data
            content = []
            for key in keyList:
                resultList = key[1].findall(data)
                if resultList:
                    if key[0] == 'WEIGHT':
                        assert len(resultList) == 1, 'WEIGHT指令只能出现一次'
                        weight = int(resultList[0][7:-1])
                        data = data.replace(resultList[0], '')
                        assert weight >= 1
                    elif key[0] == 'END':
                        assert len(resultList) == 1, 'END指令只能出现一次'
                        end = True
                        data = data.replace(resultList[0], '')
                    else:
                        for result in resultList:
                            index = data.find(result)
                            arg = data[index+len(key[0])+1:index+len(result)-1]
                            if index != 0:
                                if data[:index].split():
                                    content.append(['TEXT',data[:index].replace('\\n', '\n')])
                            if key[0] == 'DRAW':
                                targetDeck = arg.split('/')[0]
                                assert len(arg.split('/')) <= 2
                                assert targetDeck == deckTitle or targetDeck in deckRelayList, targetDeck
                            elif key[0] == 'ROLL':
                                assert isDiceCommand(arg)
                            content.append([key[0],arg])
                            data = data[index+len(result):]
            if data.split():
                content.append(['TEXT', data.replace('\\n', '\n')])
            assert content, rawContent
            totalWeight += weight
            deckList.append({'weight':weight, 'content':content, 'end':end, 'raw':rawContent})
            data = f.readline().strip()

    deckDict['title'] = deckTitle
    deckDict['relay'] = deckRelayList
    deckDict['totalWeight'] = totalWeight
    deckDict['list'] = deckList

    targetPath = f'./{fileName[:-4]}_deck.json'
    with open(targetPath,"w", encoding='utf-8') as f:
        json.dump(deckDict,f,ensure_ascii=False)
    print(f'成功将{fileName}转化为json文件, 输出至{targetPath}, 请将其移动至plugins/custom_data/deck_info/目录下')

