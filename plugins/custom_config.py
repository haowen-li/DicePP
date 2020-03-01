import os

from .utils import ReadJson, UpdateJson

MASTER = ['821480843']

LOCAL_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
LOCAL_NICKNAME_PATH = os.path.join(LOCAL_DATA_PATH, 'nick_name.json')
LOCAL_INITINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'init_info.json')
LOCAL_PCSTATE_PATH = os.path.join(LOCAL_DATA_PATH, 'pc_state.json')
LOCAL_GROUPINFO_PATH = os.path.join(LOCAL_DATA_PATH, 'group_info.json')

LOCAL_CUSTOM_DATA_PATH = os.path.join(os.path.dirname(__file__), 'custom_data')
LOCAL_QUERYINFO_DIR_PATH = os.path.join(LOCAL_CUSTOM_DATA_PATH, 'query_info')

GIFT_LIST = ['小鱼干', '鲨鱼干', '鲸鱼干', '好看的玻璃球', '漂亮的珊瑚', '小螺号',
 '珍贵的水晶球', '水果硬糖', '水果软糖', '小木梳', '锋利的匕首', '幽蓝魔杖', '生锈的三戟叉', '迷你皇冠', '漂亮的鳞片',
 '椰蛋树牌椰汁', '苹果12袋', '最新的海底八卦杂志', 
 '隔壁家的WiFi密码', '咸鱼味果冻', '美白精华', '一瓶海水']

if os.path.exists(LOCAL_DATA_PATH) == False:
    os.makedirs(LOCAL_DATA_PATH)
    print("Make dir: " + LOCAL_DATA_PATH)

if os.path.exists(LOCAL_NICKNAME_PATH) == False:
    test_dict = {'TEST_personId':'Nickname'}
    UpdateJson(test_dict, LOCAL_NICKNAME_PATH)
    print("Create file: " + LOCAL_NICKNAME_PATH)
    del test_dict

if os.path.exists(LOCAL_INITINFO_PATH) == False:
    test_dict = {'TEST_groupId':'Init Info'}
    UpdateJson(test_dict, LOCAL_INITINFO_PATH)
    print("Create file: " + LOCAL_INITINFO_PATH)
    del test_dict
    
if os.path.exists(LOCAL_PCSTATE_PATH) == False:
    test_dict = {'TEST_personId':'PC State'}
    UpdateJson(test_dict, LOCAL_PCSTATE_PATH)
    print("Create file: " + LOCAL_PCSTATE_PATH)
    del test_dict

if os.path.exists(LOCAL_GROUPINFO_PATH) == False:
    test_dict = {'TEST_groupId':'Group Info'}
    UpdateJson(test_dict, LOCAL_GROUPINFO_PATH)
    print("Create file: " + LOCAL_GROUPINFO_PATH)
    del test_dict
    