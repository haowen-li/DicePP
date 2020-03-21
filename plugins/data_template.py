from .utils import *
from .help_info import *

userInfoTemp = {'credit':0, 'commandDate':GetCurrentDateStr(), 'commandAccu':0, 'warning':0, 'ban':0}
userDictTemp = {'userId':userInfoTemp}
groupInfoTemp = {'active':True, 'credit':0, 'commandDate':GetCurrentDateStr(), 'commandAccu':0, 'welcome':'欢迎新人~', 'warning':0, 'noticeBool':True, 'noticeStr':FIRST_TIME_STR}
groupDictTemp = {'groupId':groupInfoTemp}