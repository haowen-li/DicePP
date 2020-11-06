import numpy as np
import os
import argparse
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, dest = 'file', help='file name, must be txt format')

    fileName = parser.parse_args().file
    
    cookDict = {}
    curName = ''
    with open(fileName, 'r', encoding="utf-8-sig") as f:
        data = f.readline().strip()
        while data:
            data = data.split(':')
            if data[0] == '名称':
                cookDict[data[1]] = {}
                curName = data[1]
            if data[0] == '美味' or data[0] == '难度':
                data[1] = int(data[1])
            if data[0] == '菜系' or data[0] == '种类' or data[0] == '风格':
                data[1] = data[1].split('/')
            cookDict[curName][data[0]] = data[1]
            data = f.readline().strip()
            if data == '':
                data = f.readline().strip()
                cookDict[curName]['关键词'] = cookDict[curName]['菜系'] + cookDict[curName]['种类'] + cookDict[curName]['风格']



    targetPath = f'./{fileName[:-4]}_menu.json'
    with open(targetPath,"w", encoding='utf-8') as f:
        json.dump(cookDict,f,ensure_ascii=False)
    print(f'成功将{fileName}转化为json文件, 输出至{targetPath}, 请将其移动至plugins/custom_data/menu_info/目录下')