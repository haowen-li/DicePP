import re

GIFT_LIST = ['秘制蜜汁小鱼干', '吹起来很好听的小螺号', '特别美味的大青蟹',
 '珍贵的水晶球(听说吞下去可以转运)', '椰蛋树牌椰汁', '椰羊牌椰奶',
  '最新的海底八卦杂志', '皇宫大殿的WiFi密码', '回火的木棒', '俺寻思之力',
  '咸鱼味果冻', '阿罗德斯之镜', '甜甜花酿鸡', '琉璃袋', '溪木镇的鸡']

COOK_FAIL_STR_LIST = ['略加思索', '灵机一动', '毫不犹豫', '啊!就是这个', '不如这样']

CHAT_CREDIT_LV0 = 100
CHAT_CREDIT_LV1 = 300
CHAT_CREDIT_LV2 = 500
CHAT_CREDIT_LV3 = 1000
CHAT_CREDIT_LV4 = 1500
CHAT_CREDIT_LV5 = 2000

CREDIT_LEVEL_FEED = {0:['呐，{name}你问这个是想做什么呀？',
                        '现在对{name}还不是很熟悉呢~',
                        '我们才认识没多久，问这个不是很好吧~',
                        '对{name}还没什么印象呢。。。'],
                     CHAT_CREDIT_LV0:['认识{name}有一些日子了，但是还需要更多时间来了解你哦~',
                          '{name}？应该不是坏人吧？'],
                     CHAT_CREDIT_LV1:['{name}么？也可以算得上是朋友吧~',
                          '{name}大概是伊丽莎白的朋友吧~',
                          '{name}想和伊丽莎白做朋友吗？还要多努力哦~'],
                     CHAT_CREDIT_LV2:['{name}当然是我的朋友啦~',
                          '伊丽莎白觉得{name}作为一个人类来说还不错啦~',
                          '{name}, 我们是认识的喔, 但是不要再说我是奈亚拉托提普变的啦~'],
                     CHAT_CREDIT_LV3:['{name}是伊丽莎白的好朋友哦~',
                          '伊丽莎白觉得{name}是个好人!$点赞$',
                          '嗯? {name}, 干嘛问这个, 生命中再无聊的时光, 也都是 限 量 版 哟~',
                          '{name}, 不是每一个故事都要有"之后" #轻轻合上故事集'],
                     CHAT_CREDIT_LV4:['诶？好感吗？不要问这个啦~{name}，这是我刚做好的棒棒糖，要来一根吗？',
                          '今天{name}要和伊丽莎白一起比赛游泳吗? 我不会输的哦~',
                          '{name}, 想和伊丽莎白去海边走走吗?',
                          '{name}是伊丽莎白可以信赖的人哦~',
                          '{name}, 待会退潮的时候和伊丽莎白一起向群青公主祈祷吧!$祈祷$',
                     ],
                     CHAT_CREDIT_LV5:['{name}, 当我们回首往事, 我们可能不会记得当时说了些什么, 或许不会记得任何细节, 但我们都会记得, 我在那里和你们一起 ———— 而这才是最重要的。',
                                      '{name}, 能与你相遇, 真是太好了']
                    }

NAME2TITLE = {'梨子':'伊丽莎白最喜欢的水果',
              '群青公主':'群青公主 Ultramarine Princess是伊丽莎白信仰的神明哦~ 祂的真名是阿弗洛狄忒 Aphrodite, 祂是深海之主，厄运之神，美丽与欲望的化身，梦境与幻象的主宰.',
              '阿弗洛狄忒':'阿弗洛狄忒 Aphrodite被我们人鱼一族尊称为群青公主 Ultramarine Princess, 祂的神职是海洋 Ocean; 灾厄 Adversity; 繁殖 Breed; 梦境 Dream; 幻象 Illusion.',
              '群青公主阿弗洛狄忒': '群青公主 Ultramarine Princess 阿弗洛狄忒 Aphrodite 是深海之主，厄运之神，美丽与欲望的化身，梦境与幻象的主宰. 阿弗洛狄忒的教会分成数个教派，不同教派的理念相差很大，主要包括由我们人鱼领导的克制派与邪恶鱼人和海怪组成的放纵派。',
              '伊丽莎白':'一条小人鱼',

              '小安':'伊丽莎白派往人类的牧者',
              'printf（）':'一个为了让你们可以开怀大笑而尽了一份力的男人。',
              '困囿四囝':'幽默地精的保护者',
              '邪恶勇者':'黑暗料理之王',
              '牧龙人':'精精牧龙人',
              '冰棒':'一个动不动就说一些没有什么用的骚话的笑话翻译工具人',
              '小花':'对所有怪物和魔法物品了如指掌的花族王子',
              '花作噫':'正在学习5E的苦力作者'
              }

CHAT_COMMAND_COMMON = {'the shadow.*':[(CHAT_CREDIT_LV0, 'The shadow! (激动地)'),
                                (CHAT_CREDIT_LV1, 'The shadow? (疑惑地)'),
                                (CHAT_CREDIT_LV1, 'The shadow. (坚定地)'),
                                (CHAT_CREDIT_LV2, 'The shadow! (惊恐地)'),
                                (CHAT_CREDIT_LV2, 'The shadow... (平静地)'),
                                (CHAT_CREDIT_LV2, 'The shadow? (无奈地)'),
                                (CHAT_CREDIT_LV3, '$没有思考$I\'m the SHADOW! (嚣张地)')],
                '^伊丽莎白$':[ (CHAT_CREDIT_LV0, '$没有思考$哦, 好的好的, 再见'),
                            (CHAT_CREDIT_LV0, '$没有思考$我推荐我自己!'),
                            (CHAT_CREDIT_LV1, '$看书$伊丽莎白在这里哦~'),
                            (CHAT_CREDIT_LV1, '$没有思考$有什么可以帮到你吗?'),
                            (CHAT_CREDIT_LV3, '$祈祷$愿群青公主护佑着你'),
                            (CHAT_CREDIT_LV3, '$看书$今天也是要好好学习规则的一天呢~')],
                '.*伊丽莎白保佑.*':[(CHAT_CREDIT_LV0, '$看书$#伊丽莎白意味深长地看着你'),
                                   (CHAT_CREDIT_LV0, '$抛全1骰子$没问题~', CHAT_CREDIT_LV3),
                                   (CHAT_CREDIT_LV0, '$抛全1骰子$你的想法我已经知道了哦~'),
                                   (CHAT_CREDIT_LV1, '$祈祷$厄运只是群青公主对我们的考验, 勇敢向前吧!', CHAT_CREDIT_LV2),
                                   (CHAT_CREDIT_LV1, '$祈祷$好运和厄运都只是暂时的, 请不要把它们放在心上', CHAT_CREDIT_LV2),
                                   (CHAT_CREDIT_LV1, '没人能帮忙。你必须独自面对Gazebo'),
                                   (CHAT_CREDIT_LV3, '$祈祷$愿群青公主护佑着你'),
                                   (CHAT_CREDIT_LV4, '$点赞$加油~'),
                                   (CHAT_CREDIT_LV4, '$双重点赞$加油加油~'),
                                   (CHAT_CREDIT_LV5, '$抛全1骰子$隐藏着黑暗力量的骰子啊~在我面前显示你真正的力量吧，跟你许下约定的伊丽莎白命令你...')],
                '有团吗.?':[(CHAT_CREDIT_LV0, '让我们换一个话题'),
                           (CHAT_CREDIT_LV1, '祝您长寿~'),
                           (CHAT_CREDIT_LV1, '升级到凡戴尔的失落矿坑\n需求: DM (你没有)\n花费: 全家桶'),
                           (CHAT_CREDIT_LV1, '我们在与哈劳斯国王、拉盖娅女皇、雅米拉女士、酒馆侍女和海寇跑团。'),
                           (CHAT_CREDIT_LV2, '伊丽莎白表彰了你的热情, 但是她决定将下一个团的名额留给梨子。她会出0第纳尔作为你的补偿。'),
                           (CHAT_CREDIT_LV2, '三个哥布林, 一头黑熊, 两个强盗, 一个狗头人, 一只蚊蝠, 一头野狼...掷先攻吧!'),
                           (CHAT_CREDIT_LV5, '等伊丽莎白给你开团吧~')],
                '伊丽莎白带团.*':[(CHAT_CREDIT_LV1, '$疑惑翻书$唔~规则太难啦!'),
                                 (CHAT_CREDIT_LV2, '$看卷轴$唔...'),
                                 (CHAT_CREDIT_LV3, '$没有思考$等伊丽莎白再看多一会书吧...'),
                                 (CHAT_CREDIT_LV4, '$完全搞懂了$玩家手册我完全搞懂了, 找时间带团吧~'),
                                 (CHAT_CREDIT_LV4, '$没有思考$你们走进房间, 房间里全是公主和小马...'),
                                 (CHAT_CREDIT_LV4, '$看书$高大的留着长长白胡须的老人, 戴着歪向一边的尖顶帽子, 穿着污损的灰色长袍, 身边有七只金丝雀...'),],
                '赞.?':[(CHAT_CREDIT_LV2, '$点赞$'),(CHAT_CREDIT_LV3, '$双重点赞$')]
                }

def GetPersonTitle(inputStr, credit):
    name = inputStr[:inputStr.find('是')]
    if name in NAME2TITLE.keys():
        return NAME2TITLE[name]
    else:
        return None

CHAT_COMMAND_FUNCTION = {'.+是谁.?':GetPersonTitle, '.+是什么.?':GetPersonTitle}

def InsertEmotion(inputStr, emotionDict):
    def replaceByEmotion(matched):
            inputStr = matched.group()[1:-1]
            try:
                inputStr = f'[CQ:image,file=file:///{emotionDict[inputStr]}]'
            except:
                inputStr = f'#{inputStr}'
            return inputStr
    if emotionDict:
        return re.sub('\$.+?\$', replaceByEmotion, inputStr)
    else:
        return inputStr