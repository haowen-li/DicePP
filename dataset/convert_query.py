import numpy as np
import os
import argparse
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, dest = 'file', help='file name, must be txt format')

    fileName = parser.parse_args().file
    
    queryDict = {}
    title = ''
    content = ''
    with open(fileName, 'r', encoding="utf-8-sig") as f:
        data = f.readline().strip()
        while data:
            data = data.strip()
            if not data:
                if title:
                    if len(title) > 20:
                        print("Title too long?"+title+"##"+content)
                    elif len(content) < 5:
                        print("Content too small?"+title+"##"+content)
                    content = content.replace('【换行】', '\n')
                    queryDict[title] = content[:-1]
                title = ''
                content = ''
            else:
                if not title:
                    title = data
                else:
                    content += data.strip() + '\n'
            data = f.readline()
    content = content.replace('【换行】', '\n')
    queryDict[title] = content[:-1]



    targetPath = f'./{fileName[:-4]}_query.json'
    with open(targetPath,"w", encoding='utf-8') as f:
        json.dump(queryDict,f,ensure_ascii=False)
    print(f'成功将{fileName}转化为json文件, 输出至{targetPath}, 请将其移动至plugins/custom_data/query_info/目录下')