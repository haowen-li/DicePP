from nonebot.default_config import *

SUPERUSERS = {821480843} # 超级用户

COMMAND_START = {'sudo '} # 命令起始字符 (目前只应用于特殊命令)

HOST = '0.0.0.0'
PORT = 8080
SUPERUSERS = {821480843}

DEBUG = False
SHORT_MESSAGE_MAX_LENGTH = 800


#sudo docker run --name=coolq -d -p 8080:9000 -v /coolq-data:/home/user/coolq -e VNC_PASSWD=12345678 -e COOLQ_ACCOUNT=2418715861 coolq/wine-coolq