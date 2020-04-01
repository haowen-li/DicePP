import os
import datetime

from .utils import ReadJson, UpdateJson

SELF_ID = '2192720436'
MASTER = ['821480843']
MASTER_GROUP = ['861919492']

GROUP_PASSWORD = 'dnd5e-pear'

# 环境信息
IS_COOLQ_PRO = True
PLATFORM_NAME = 'DOCKER' # 可选为 DOCKER 或 其他任意字符串
# PLATFORM_NAME = 'WINDOWS' # 可选为 DOCKER 或 其他任意字符串
# 刷屏上限
MESSAGE_LIMIT_NUM = 12
# 刷屏阈值
MESSAGE_LIMIT_TIME = datetime.timedelta(seconds = 6)
# 每日额外好感度上限
DAILY_CREDIT_LIMIT = 10

LOCAL_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
LOCAL_NICKNAME_PATH = os.path.join(LOCAL_DATA_PATH, 'nick_name.json')
LOCAL_INITINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'init_info.json')
LOCAL_PCSTATE_PATH = os.path.join(LOCAL_DATA_PATH, 'pc_state.json')
LOCAL_GROUPINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'group_info.json')
LOCAL_USERINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'user_info.json')
LOCAL_TEAMINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'team_info.json')
LOCAL_DAILYINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'daily_info.json')

ALL_LOCAL_DATA_PATH = [LOCAL_NICKNAME_PATH, LOCAL_INITINFO_PATH, LOCAL_PCSTATE_PATH,
                       LOCAL_GROUPINFO_PATH, LOCAL_USERINFO_PATH, LOCAL_TEAMINFO_PATH,
                       LOCAL_DAILYINFO_PATH]

LOCAL_CUSTOM_DATA_PATH = os.path.join(os.path.dirname(__file__), 'custom_data')
LOCAL_QUERYINFO_DIR_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'query_info')
LOCAL_DECKINFO_DIR_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'deck_info')
LOCAL_MENUINFO_DIR_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'menu_info')
LOCAL_JOKEINFO_DIR_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'joke_info')
LOCAL_JOKEIMG_DIR_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'joke_img')

ALL_LOCAL_DIR_PATH = [LOCAL_DATA_PATH, LOCAL_CUSTOM_DATA_PATH, LOCAL_QUERYINFO_DIR_PATH,
                      LOCAL_DECKINFO_DIR_PATH, LOCAL_DECKINFO_DIR_PATH, LOCAL_MENUINFO_DIR_PATH,
                      LOCAL_JOKEINFO_DIR_PATH, LOCAL_JOKEIMG_DIR_PATH]

WINE_COOLQ_PATH = 'Z:/home/user/coolq'
WINE_COOLQ_JOKEIMG_PATH = WINE_COOLQ_PATH + '/data/image/joke/'

GIFT_LIST = ['秘制蜜汁小鱼干', '吹起来很好听的小螺号', '特别美味的大青蟹',
 '珍贵的水晶球(听说吞下去可以转运)', '偷偷带出来的淬毒匕首', '父皇宝库里的幽蓝魔杖',
 '路上随便捡的一把生锈三叉戟', '超迷你皇冠(建国666周年纪念品)', '漂亮的鳞片(来源不明)',
 '椰蛋树牌椰汁', '最新的海底八卦杂志', '皇宫大殿的WiFi密码', '咸鱼味果冻', '母后偷偷在用的美白精华', '一瓶从六核之洋深处取来的海水',
 '阿罗德斯之镜']

MENU_CUISINE_LIST = ['经典', '精灵', '矮人', '东方', '异域']
MENU_TYPE_LIST = ['小菜', '主菜', '汤', '甜品', '酒', '饮料']
MENU_STYLE_LIST = ['黑暗', '野炊', '酒馆', '奢侈']
MENU_KEYWORD_LIST = MENU_CUISINE_LIST + MENU_TYPE_LIST + MENU_STYLE_LIST

COOK_FAIL_STR_LIST = ['略加思索', '灵机一动', '毫不犹豫', '啊!就是这个', '不如这样']


for dirPath in ALL_LOCAL_DIR_PATH:
    if os.path.exists(dirPath) == False:
        os.makedirs(dirPath)
        print("Make dir: " + dirPath)

for path in ALL_LOCAL_DATA_PATH:
    if os.path.exists(path) == False:
        UpdateJson({}, path)
        print("Create file: " + path)