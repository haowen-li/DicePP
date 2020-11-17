import re

def GetPersonTitle(inputStr, credit):
    name = inputStr[:inputStr.find('是')]
    if name in NAME2TITLE.keys():
        return NAME2TITLE[name]
    else:
        return None

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

CHAT_CREDIT_LV0 = 100
CHAT_CREDIT_LV1 = 300
CHAT_CREDIT_LV2 = 500
CHAT_CREDIT_LV3 = 1000
CHAT_CREDIT_LV4 = 1500
CHAT_CREDIT_LV5 = 2000

CREDIT_REPEAT_FEED = '哎~今天已经问过了呀~'
CREDIT_LEVEL_FEED = {0:['呐，{name}你问这个是想做什么呀？',
                        '现在对{name}还不是很熟悉呢~',
                        '我们才认识没多久，问这个不是很好吧~',
                        '对{name}还没什么印象呢...',
                        '{name}是...谁啊？似乎没有什么印象呢'],
                     CHAT_CREDIT_LV0:['认识{name}有一些日子了，但是还需要更多时间来了解你哦~',
                          '{name}？应该不是坏人吧？',
                          '{name}么？也可以算得上是朋友吧~',
                          '{name}大概是伊丽莎白的朋友吧~',
                          '{name}想和伊丽莎白做朋友吗？还要多努力哦~',
                          '{name}嘛？确实是认识呢...不要烦我...还有人要查询规则呢...'],
                     CHAT_CREDIT_LV1:['{name}当然是我的朋友啦~',
                          '伊丽莎白觉得{name}作为一个人类来说还不错啦~',
                          '{name}, 我们是认识的喔, 但是不要再说我是奈亚拉托提普变的啦~',
                          '要是拿{name}跟梨子比较的话，大概...1:100？',
                          '想要得到伊丽莎白的青睐，{name}先去把规则书抄10遍吧，无论是三宝书还是扩展都要抄哦~'],
                     CHAT_CREDIT_LV2:['{name}是伊丽莎白的好朋友哦~',
                          '伊丽莎白觉得{name}是个好人!$点赞$',
                          '好啦好啦...别问啦, 会给你大成功的',
                          '请不要让伊丽莎白频繁地查询迷情媚药好嘛？虽然跟{name}关系还不错，但是这种事情依然是不被允许的！'
                          ],
                     CHAT_CREDIT_LV3:['嗯? {name}, 干嘛问这个, 生命中再无聊的时光, 也都是 限 量 版 哟~',
                          '{name}, 不是每一个故事都要有"之后" #轻轻合上故事集',
                          '掷骰子好累QAQ, 伊丽莎白不想再努力了, {name}来代劳吧。',
                          '诶？好感？好感...对{name}的好感才不会有的啦!',
                          '{name}已经被伊丽莎白强化了！快上！',
                          'DM, 我证明, {name}在我这里确实roll了6个18!',
                          '{name}是伊丽莎白可以信赖的人哦~',
                     ],
                     CHAT_CREDIT_LV4:['诶？{name}为什么要问这个问题？哦对了, 这是我刚做好的棒棒糖, 要来一根嘛？',
                          '今天{name}要和伊丽莎白一起比赛游泳吗? 我不会输的哦~',
                          '{name}, 想和伊丽莎白去海边走走吗?',
                          '等会退潮的时候...{name}要和我一起向群青公主祈祷吗？',
                          '不许叫我傻白！就算是{name}也不行！爱称...真的嘛...那我勉强接受吧',
                          '不要问我为什么{name}的角色卡里少了钱！因为被我拿去拿去买冰镇梨子汁了！',
                          '当前网络波动绝对不是伊丽莎白的错！都是因为企鹅把属于{name}的骰子叼走了！',
                          '哎~今天已经问过了呀....什么？绝对没有？伊丽莎白不可能记错的，绝对是{name}错了！',
                          '过来帮伊丽莎白整理资料吧，作为奖励，今天就多给{name}扔几个大成功吧~',
                          '想听伊丽莎白唱歌嘛？现在....别跑啊{name}！不会让你过豁免的！',
                          '什么？{name}要去冒险了？等我准备一下骰子 #把全是20的骰子拿出来'
                     ],
                     CHAT_CREDIT_LV5:['{name}, 当我们回首往事, 我们可能不会记得当时说了些什么, 或许不会记得任何细节, 但我们都会记得, 我在那里和你们一起 ———— 而这才是最重要的。',
                                      '{name}, 能与你相遇, 真是太好了',
                                      '{name}跟伊丽莎白在一起的时光，伊丽莎白会永远记住的。',
                                      '伊丽莎白会永远记得你，所以{name}也会永远记得我的对嘛？',
                                      '{name}叫爱称也要适可而止啊！以后大家都叫我傻白怎么办？',
                                      '想摸我的头？唉, 既然是{name}的话...但是只有一次哦!',
                                      '伊丽莎白要小睡一会儿...所以{name}....能给我讲个睡前故事嘛？',
                                      '我正在记录{name}冒险的故事哦，怎么样？写的还不错吧~']
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
              '冰棒':'工具人',
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
                '^伊丽莎白.?$':[ (CHAT_CREDIT_LV0, '$没有思考$哦, 好的好的, 再见'),
                            (CHAT_CREDIT_LV0, '$没有思考$我推荐我自己!'),
                            (CHAT_CREDIT_LV0, '早安, 跑团人!'),
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

GIFT_LIST = ['秘制蜜汁小鱼干', '吹起来很好听的小螺号', '特别美味的大青蟹',
 '珍贵的水晶球(听说吞下去可以转运)', '椰蛋树牌椰汁', '椰羊牌椰奶',
  '最新的海底八卦杂志', '皇宫大殿的WiFi密码', '回火的木棒', '俺寻思之力',
  '咸鱼味果冻', '阿罗德斯之镜', '甜甜花酿鸡', '琉璃袋', '溪木镇的鸡']

COOK_FAIL_STR_LIST = ['略加思索', '灵机一动', '毫不犹豫', '啊!就是这个', '不如这样']

CHAT_COMMAND_FUNCTION = {'.+是谁.?':GetPersonTitle, '.+是什么.?':GetPersonTitle}

BOT_ON_STR = '伊丽莎白来啦~'
BOT_OFF_STR = '那我就不说话咯~ #潜入水中 (咕嘟咕嘟)'

ROLL_FEED_STR = '{reason}{nickName}掷出了{resultStr}' # 普通的掷骰指令
ROLL_REASON_STR = '由于{reason},' # reason部分的格式
N20_FEED_STR = ', 大成功!' # 单次掷骰大成功提示
N01_FEED_STR = ', 大失败!' # 单次掷骰大失败提示
N20_FEED_MULT_STR = '{succTimes}次大成功!' # 多次掷骰大成功提示
N01_FEED_MULT_STR = '{failTimes}次大失败!' # 多次掷骰大失败提示

HROLL_FEED_STR = '{nickName}进行了一次暗骰' # 使用暗骰指令后在群里发送的提示
HROLL_RES_STR = '暗骰结果:{finalResult}' # 使用暗骰指令后私聊发送的提示

JRRP_FEED_STR = '{nickName}今天走运的概率是{value}%' # JRRP指令回复
JRRP_GOOD_STR = ', 今天运气不错哦~' # 好运提示
JRRP_BAD_STR = ', 今天跑团的时候小心点... 给你{gift}作为防身道具吧~' # 厄运提示
JRRP_REPEAT_STR = '不是已经问过了嘛~ 你走运的概率是{value}%, 记好了哦!'

NN_FEED_STR = '要称呼你为{nickName}吗? 没问题!' # nn指令回复
NN_RESET_STR = '要用本来的名字称呼你吗? 了解!'

INIT_MISS_STR = '还没有做好先攻列表哦'
INIT_CLEAR_STR = '先攻列表已经删除啦'
INIT_CLEAR_FAIL_STR = '无法删除不存在的先攻列表哦'
INIT_REMOVE_STR = '已经将{name}从先攻列表中删除'
INIT_REMOVE_FAIL_STR = '在先攻列表中找不到与"{name}"相关的名字哦'
INIT_REMOVE_MULT_STR = '在先攻列表找到多个可能的名字: {val}'
INIT_WARN_STR = '先攻列表上一次更新是一小时以前, 请注意~'

DISMISS_FEED_STR = '再见咯~' # 使用dismiss指令退群后发送
NICKNAME_LEN_LIMIT_STR = '你的名字是什么呀...记不住啦~' # 昵称超过20个字符后发送的提示
GROUP_COMMAND_ONLY_STR = '只有在群聊中才能使用该功能哦' # 在私聊中使用群聊功能时发送的提示
HP_CLEAR_STR = '已经忘记了{nickName}的生命值...' # 删除生命值后的提示
PC_CLEAR_STR = '成功删除了{nickName}的角色卡~' # 删除角色卡后的提示
CHECK_TIME_LIMIT_STR = '重复的次数必须在1~9之间哦~' # 检定次数超出范围后的提示
TEAM_NEED_STR = '必须先加入队伍哦~' # 需要先加入队伍的提示
TEAM_INFO_FEED_STR = '已将队伍的完整信息私聊给你啦~' # 查看队伍信息后的提示
SPELL_SLOT_ADJ_INVALID_STR = '{val}是无效的法术位调整值~ 合法范围:[-9, +9]' # 无效法术位调整提示
SEND_LEN_LIMIT_STR = '请不要随便骚扰Master哦~ (信息长度限制为10~100)' # 给Master发送的信息超过范围后的提示
SEND_FEED_STR = '已将信息转发给Master了~' # 给Master发送信息后的提示
EXAM_LIST_STR = '当前可用的题库是: {val}' # 题库列表
EXAM_MISS_STR = '找不到这个题库哦~' # 找不到题库
EXAM_MULT_STR = '想找的是哪一个题库呢?\n{possKey}' # 找到多个题库
WELCOME_FEED_STR = '已将入群欢迎词设为:' # 设置入群关键词
WELCOME_CLEAR_STR = '已经关闭入群欢迎' # 关闭入群关键词
NAME_FORMAT_STR = '输入的格式有些错误呢~' # 生成随机姓名指令格式不正确
NAME_LIMIT_STR = '生成的名字个数必须在1~10之间哦~' # 生成随机姓名指令数量不正确
DND_FEED_STR = '{nickName}的初始属性: {reason}\n{result}' # 生成属性的回复
JOKE_FEED_STR = '{nickName}的{flag}日随机TRPG笑话:\n{result}' # 今日笑话回复, flag为[昨, 今, 明]
JOKE_LIMIT_LAST_STR = '只有一次机会哦~昨天的今日笑话就是今天的昨日笑话, 你已经看过啦~'
JOKE_LIMIT_TODAY_STR = '只有一次机会哦~昨天的明日笑话就是今天的今日笑话, 你已经看过啦~'
JOKE_LIMIT_NEXT_STR = '只有一次机会哦~你已经提前把明天的笑话看过啦~'
ERROR2MASTER_STR = '啊咧, 遇到一点问题, 请汇报给梨子~' # 遇到错误时的反馈
MASTER_LIMIT_STR = '只有Master才能使用这个命令!'
SAVE_FEED_STR = '成功将所有资料保存到本地咯~'
INFO_MISS_STR = '{val}资料库加载失败了呢...'

NOTE_FEED_STR = '记下来咯~ 索引是"{index}"'
NOTE_NUM_LIMIT_STR = '一个群里最多只允许20条笔记哦~'
NOTE_LEN_LIMIT_STR = '呜...记不住啦~ 超过三百个字的内容就不要记到笔记上了吧...'
NOTE_TOTAL_LIMIT_STR = '呜...记不住啦~ 一个群的笔记总共最多只能保存两千个字哦~'
NOTE_CLEAR_ALL_STR = '成功删除所有笔记~'
NOTE_CLEAR_STR = '成功删除索引为{index}的笔记~'
NOTE_MULT_INDEX_STR = '可能的笔记索引:{resList}'
NOTE_MISS_STR = '无法找到相应的笔记索引'

COOK_FEED_STR = '{nickName}的烹饪结果是:\n{cookResult}' # 烹饪回复
ORDER_FEED_STR = '{nickName}的菜单:\n{orderResult}' # 点菜回复
ORDER_FEED_P2_STR = '于{num1}个备选中选择了{num2}种食物:\n'
ORDER_LIMIT_MIN_STR = '呃,您要不要点菜呢?' # 点菜数量小于1
ORDER_LIMIT_MAX_STR = '一个人点那么多会浪费的吧, 请将数量控制在5以内哦' # 点菜数量大于5
ORDER_INVALID_STR = '{key}不是有效的关键词, 请查看.help烹饪'
ORDER_FAIL_ALL_STR = '想不到满足要求的食物呢...'
ORDER_FAIL_PART_STR = '在无视了关键词{delKeyList}后, '

MENU_LIMIT_STR = '每天只有一个菜单哦~' # 今日菜单超出次数

QUERY_NOTICE_STR = '现在的记忆中共有{num}个条目呢, 可查询内容请输入 .help查询 查看'
QUERY_KEY_LIMIT_STR = '指定的关键词太多咯'
QUERY_MULT_SHORT_STR = '找到多个匹配的条目: {info}\n回复序号可直接查询对应内容'
QUERY_MULT_LONG_STR = '找到多个匹配的条目: {info}等, 共{num}个条目\n回复序号可直接查询对应内容'
QUERY_MISS_STR = '唔...找不到呢...'
QUERY_FEED_COMP_STR = '要找的是{key}吗?\n{result}'
INDEX_MISS_STR = '资料库中找不到任何含有关键字{keywordList}的词条呢~'

DRAW_NOTICE_STR = '现在的记忆中共有{num}个牌堆呢, 分别是{val}'
DRAW_NUM_LIMIT_STR = '抽取的数量必须为1到10之间的整数~'
DRAW_FEED_STR = '从{targetStr}中抽取的结果: \n{result}'
DRAW_MULT_SHORT_STR = '找到多个匹配的牌堆: {info}'
DRAW_MULT_LONG_STR = '找到多个匹配的牌堆: {info}等, 共{num}个牌堆'

EXAM_MISS_STR = '{key}不是可用的题库!'
EXAM_EXPIRE_STR = '时间到咯, 请你重新开始吧~'
EXAM_TRUE_STR = '回答正确~'
EXAM_FALSE_STR = '回答错误~ 答案是{answer}'

# 于 0.7.1 版本中新增
FUNC_ON_STR = '将{funcName}功能启用啦~'
FUNC_OFF_STR = '将{funcName}功能禁用啦~'
FUNC_BAN_NOTICE = '这个功能在本群已经被禁用咯, 如果需要的话请使用群管理指令启用吧~'
# --------------- #