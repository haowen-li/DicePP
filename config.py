from nonebot.default_config import *

SUPERUSERS = {821480843} # 超级用户

COMMAND_START = {'sudo '} # 命令起始字符 (目前只应用于特殊命令)

HOST = '127.0.0.1'
PORT = 8080
SUPERUSERS = {821480843}

DEBUG = False
SHORT_MESSAGE_MAX_LENGTH = 500

SESSION_RUNNING_EXPRESSION = '当前网络延迟较高或服务器压力过大, 请考虑暂停使用...'


#sudo docker run --name=coolq -d -p 8080:9000 -v /coolq-data:/home/user/coolq -e VNC_PASSWD=12345678 -e COOLQ_ACCOUNT=2418715861 coolq/wine-coolq