import re

GIFT_LIST = ['秘制蜜汁小鱼干', '吹起来很好听的小螺号', '特别美味的大青蟹',
 '珍贵的水晶球(听说吞下去可以转运)', '偷偷带出来的淬毒匕首', '父皇宝库里的幽蓝魔杖',
 '路上随便捡的一把生锈三叉戟', '超迷你皇冠(建国666周年纪念品)', '漂亮的鳞片(来源不明)',
 '椰蛋树牌椰汁', '最新的海底八卦杂志', '皇宫大殿的WiFi密码', '咸鱼味果冻', '母后偷偷在用的美白精华', '一瓶从六核之洋深处取来的海水',
 '阿罗德斯之镜']

COOK_FAIL_STR_LIST = ['略加思索', '灵机一动', '毫不犹豫', '啊!就是这个', '不如这样']

NAME2TITLE = {'梨子':'伊丽莎白最喜欢的水果~',
              '群青公主':'群青公主 Ultramarine Princess是伊丽莎白信仰的神明哦~ 祂的真名是阿弗洛狄忒 Aphrodite, 祂是深海之主，厄运之神，美丽与欲望的化身，梦境与幻象的主宰.',
              '阿弗洛狄忒':'阿弗洛狄忒 Aphrodite被我们人鱼一族尊称为群青公主 Ultramarine Princess, 祂的神职是海洋 Ocean; 灾厄 Adversity; 繁殖 Breed; 梦境 Dream; 幻象 Illusion.',
              '群青公主阿弗洛狄忒': '群青公主 Ultramarine Princess 阿弗洛狄忒 Aphrodite 是深海之主，厄运之神，美丽与欲望的化身，梦境与幻象的主宰. 阿弗洛狄忒的教会分成数个教派，不同教派的理念相差很大，主要包括由我们人鱼领导的克制派与鱼人和海怪组成的放纵派。',
              
              'printf()':'一个为了让你们可以开怀大笑而尽了一份力的男人。',
              '困囿四囝':'幽默地精的保护者',
              '邪恶':'黑暗料理之王',
              '牧龙人':'精精牧龙人'
              }

CHAT_CREDIT_LV0 = 50
CHAT_CREDIT_LV1 = 100
CHAT_CREDIT_LV2 = 200
CHAT_CREDIT_LV3 = 300
CHAT_CREDIT_LV4 = 500
CHAT_CREDIT_LV5 = 1000
CHAT_COMMAND_COMMON = {'the shadow.*':[(CHAT_CREDIT_LV0, 'The shadow! (激动地)'),
                                (CHAT_CREDIT_LV1, 'The shadow? (疑惑地)'),
                                (CHAT_CREDIT_LV1, 'The shadow. (坚定地)'),
                                (CHAT_CREDIT_LV2, 'The shadow! (惊恐地)'),
                                (CHAT_CREDIT_LV2, 'The shadow... (平静地)'),
                                (CHAT_CREDIT_LV2, 'The shadow? (无奈地)'),
                                (CHAT_CREDIT_LV3, 'I\'m the SHADOW! (嚣张地)')],
                '.*伊丽莎白保佑.*':[(CHAT_CREDIT_LV0, '向群青公主阿弗洛狄忒祈祷吧~$祈祷$'),
                                   (CHAT_CREDIT_LV0, '没问题~$抛全1骰子$'),
                                   (CHAT_CREDIT_LV0, '你的想法我已经知道了哦~$抛全1骰子$'),
                                   (CHAT_CREDIT_LV0, '$抛骰子$'),
                                   (CHAT_CREDIT_LV1, '厄运只是群青公主对我们的考验, 勇敢向前吧!$祈祷$'),
                                   (CHAT_CREDIT_LV1, '好运和厄运都只是暂时的, 请不要把它们放在心上$祈祷$'),
                                   (CHAT_CREDIT_LV3, '愿群青公主护佑着你~$祈祷$'),
                                   (CHAT_CREDIT_LV4, '加油~$点赞$'),
                                   (CHAT_CREDIT_LV4, '加油加油~$双重点赞$')],
                '有团吗.?':[(CHAT_CREDIT_LV0, '自己不开团就不会有团跑~ $抛骰子$'),
                           (CHAT_CREDIT_LV3, '等伊丽莎白给你开团吧~$看书$')],
                '伊丽莎白带团.*':[(CHAT_CREDIT_LV1, '唔~规则太难啦!$疑惑翻书$'),
                                 (CHAT_CREDIT_LV2, '唔...$看卷轴$'),
                                 (CHAT_CREDIT_LV3, '等伊丽莎白再看多一会书吧...$没有思考$'),
                                 (CHAT_CREDIT_LV4, '玩家手册我完全搞懂了, 找时间带团吧~$完全搞懂了$')],
                '赞.?':[(CHAT_CREDIT_LV2, '$点赞$'),(CHAT_CREDIT_LV3, '$双重点赞$')]
                }

def GetPersonTitle(inputStr):
    name = inputStr[:inputStr.find('是谁')]
    if name in NAME2TITLE.keys():
        return NAME2TITLE[name]
    else:
        return None

CHAT_COMMAND_FUNCTION = {'.+是谁.?':GetPersonTitle}

def InsertEmotion(inputStr, emotionDict):
    def replaceByEmotion(matched):
            inputStr = matched.group()[1:-1]
            try:
                inputStr = f'[CQ:image,file=file:///{emotionDict[inputStr]}]'
            except:
                inputStr = f'#{inputStr}'
            return inputStr

    return re.sub('\$.+?\$', replaceByEmotion, inputStr)