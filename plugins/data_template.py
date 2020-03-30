from .utils import *
from .help_info import *

userInfoTemp = {'credit':0, 'commandDate':GetCurrentDateStr(), 'commandAccu':0, 'warning':0, 'ban':0, 'dailyCredit':0, 'seenJRRP':False, 'seenJRXH':False, 'seenJRCD':False}
userDictTemp = {'userId':userInfoTemp}
groupInfoTemp = {'active':True, 'credit':0, 'commandDate':GetCurrentDateStr(), 'commandAccu':0, 'welcome':'欢迎新人~', 'warning':0, 'noticeBool':True, 'noticeStr':FIRST_TIME_STR, 'note':{}}
groupDictTemp = {'groupId':groupInfoTemp}
dailyInfoTemp = {'date':'', 'totalCommand':0, 'rollCommand':0, 'jrrpCommand':0, 'pcCommand':0, 'checkCommand':0, 'slotCommand':0, 'teamCommand':0, 
				 'moneyCommand':0, 'hpCommand':0, 'initCommand':0, 'cookCommand':0, 'queryCommand':0, 'querySucc':0, 'queryFail':0, 'queryMult':0, 'drawCommand':0,
				 'jokeCommand':0, 'noteCommand':0}