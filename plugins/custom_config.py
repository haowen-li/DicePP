import os
import datetime

from .utils import ReadJson, UpdateJson

SELF_ID = '2192720436'
MASTER = ['821480843']
MASTER_GROUP = ['861919492']

GROUP_PASSWORD = 'dnd5e-pear'

# 环境信息
IS_COOLQ_PRO = True
# PLATFORM_NAME = 'DOCKER' # 可选为 DOCKER 或 其他任意字符串
PLATFORM_NAME = 'WINDOWS' # 可选为 DOCKER 或 其他任意字符串
# 刷屏上限
MESSAGE_LIMIT_NUM = 12
# 刷屏阈值
MESSAGE_LIMIT_TIME = datetime.timedelta(seconds = 6)
# 聊天命令回复间隔
CHAT_LIMIT_TIME = datetime.timedelta(seconds = 10)
# 交互命令上限
IA_LIMIT_NUM = 3
# 交互命令有效期
IA_EXPIRE_TIME = datetime.timedelta(seconds = 60)
# 每日固定好感度
DAILY_CREDIT_FIX = 5
# 每日额外好感度上限
DAILY_CREDIT_LIMIT = 15
# 查询最多显示的条目
QUERY_SHOW_LIMIT = 50

LOCAL_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
LOCAL_NICKNAME_PATH = os.path.join(LOCAL_DATA_PATH, 'nick_name.json')
LOCAL_INITINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'init_info.json')
LOCAL_PCSTATE_PATH = os.path.join(LOCAL_DATA_PATH, 'pc_state.json')
LOCAL_GROUPINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'group_info.json')
LOCAL_USERINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'user_info.json')
LOCAL_TEAMINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'team_info.json')
LOCAL_DAILYINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'daily_info.json')

LOCAL_CUSTOM_DATA_PATH = os.path.join(os.path.dirname(__file__), 'custom_data')
LOCAL_QUERYINFO_DIR_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'query_info')
LOCAL_DECKINFO_DIR_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'deck_info')
LOCAL_MENUINFO_DIR_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'menu_info')
LOCAL_JOKEIMG_DIR_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'joke_img')
LOCAL_EMOTIMG_DIR_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'emotion_img')
LOCAL_JOKEINFO_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'joke.json')
LOCAL_NAMEINFO_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'name.json')
LOCAL_QUESINFO_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'question.json')

ALL_LOCAL_DATA_PATH = [LOCAL_NICKNAME_PATH, LOCAL_INITINFO_PATH, LOCAL_PCSTATE_PATH,
                       LOCAL_GROUPINFO_PATH, LOCAL_USERINFO_PATH, LOCAL_TEAMINFO_PATH,
                       LOCAL_DAILYINFO_PATH]

ALL_LOCAL_DIR_PATH = [LOCAL_DATA_PATH, LOCAL_CUSTOM_DATA_PATH, LOCAL_QUERYINFO_DIR_PATH,
                      LOCAL_DECKINFO_DIR_PATH, LOCAL_DECKINFO_DIR_PATH, LOCAL_MENUINFO_DIR_PATH,
                      LOCAL_JOKEIMG_DIR_PATH, LOCAL_EMOTIMG_DIR_PATH]

WINE_COOLQ_PATH = 'Z:/home/user/coolq'
WINE_COOLQ_JOKEIMG_PATH = WINE_COOLQ_PATH + '/data/image/joke/'
WINE_COOLQ_EMOTIMG_PATH = WINE_COOLQ_PATH + '/data/image/emotion/'

for dirPath in ALL_LOCAL_DIR_PATH:
    if os.path.exists(dirPath) == False:
        os.makedirs(dirPath)
        print("Make dir: " + dirPath)

for path in ALL_LOCAL_DATA_PATH:
    if os.path.exists(path) == False:
        UpdateJson({}, path)
        print("Create file: " + path)

if PLATFORM_NAME == 'DOCKER':
    LOCAL_JOKEIMG_DIR_PATH = WINE_COOLQ_JOKEIMG_PATH
    LOCAL_EMOTIMG_DIR_PATH = WINE_COOLQ_EMOTIMG_PATH