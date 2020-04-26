from .utils import *
from .info_help import *

userInfoTemp = {'credit':0, 'activeDate':GetCurrentDateStr(), 'spamAccu':0, 'commandAccu':0, 'messageAccu':0, 'dndCommandAccu':0, 'commandDaily':0, 'messageDaily': 0, 'dndCommandDaily':0 ,
				 'warning':0, 'ban':0, 'dailyCredit':0, 'seenJRRP':False, 'seenJRXH':False, 'seenJRCD':False, 'title':[]}
userDictTemp = {'userId':userInfoTemp}
groupInfoTemp = {'name':'未知群名称' , 'activeDate':GetCurrentDateStr(), 'chatDate':GetCurrentDateStr(), 'active':True, 'credit':0,
				 'commandAccu':0, 'messageAccu':0, 'dndCommandAccu':0, 'commandDaily':0, 'messageDaily': 0, 'dndCommandDaily':0 ,
				 'welcome':'欢迎新人~', 'warning':0, 'noticeBool':True, 'noticeStr':FIRST_TIME_STR, 'note':{}}
groupDictTemp = {'groupId':groupInfoTemp}
dailyInfoTemp = {'date':'', 'totalCommand':0, 'rollCommand':0, 'jrrpCommand':0, 'pcCommand':0, 'checkCommand':0, 'slotCommand':0, 'teamCommand':0, 
				 'moneyCommand':0, 'hpCommand':0, 'initCommand':0, 'cookCommand':0, 'queryCommand':0, 'querySucc':0, 'queryFail':0, 'queryMult':0, 'drawCommand':0,
				 'jokeCommand':0, 'noteCommand':0}