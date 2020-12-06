from utils import *
from info_help import *

userInfoTemp = {'name': '', 'credit': 0, 'activeDate': GetCurrentDateStr(), 'spamAccu': 0, 'commandAccu': 0,
                'messageAccu': 0, 'dndCommandAccu': 0, 'commandDaily': 0, 'messageDaily': 0, 'dndCommandDaily': 0,
                'warning': 0, 'ban': 0, 'dailyCredit': 0, 'seenJoke': [1, 1, 1], 'seenJRRP': False, 'seenJRCD': False,
                'seenCredit': False, 'IACommand': []}
# IACommand = [{'name':'IAFunctionName', 'date':'expireDateStr',
#               'groupId':groupId'|'Private', 'args':argsList, 'IAType':0,1,2...}]
# IATYPE: -1:未定义 0:查询或索引
# userDictTemp = {'userId':userInfoTemp}
groupInfoTemp = {'name': '未知群名称', 'inviter': '', 'activeDate': GetCurrentDateStr(), 'days': 0,
                 'chatDate': GetCurrentDateStr(), 'active': True, 'credit': 0,
                 'commandAccu': 0, 'messageAccu': 0, 'dndCommandAccu': 0, 'commandDaily': 0, 'messageDaily': 0,
                 'dndCommandDaily': 0,
                 'welcome': '欢迎新人~', 'warning': 0, 'noticeBool': True, 'noticeStr': FIRST_TIME_STR, 'note': {},
                 'BanFunc': {}}
# groupDictTemp = {'groupId':groupInfoTemp}

memberInfoTemp = {'activeDate': GetCurrentDateStr(), 'days': 0, 'messageDaily': 0, 'messageAccu': 0}
groupMemberDictTemp = {}
# memberDictTemp = {'groupId':{'userId':memberInfoTemp}}

initInfoTemp = {'id': '', 'init': 0, 'hp': 0, 'maxhp': 0, 'alive': True, 'isPC': False}
initDictTemp = {'date': GetCurrentDateStr(), 'initList': {}}

pcInfoBasicTemp = {'hp': 0, 'maxhp': 0, 'alive': True}  # 最基础的部分
groupPcDictTemp = {}
# pcInfoDictTemp = {'groupId':{'userId':pcInfoBasicTemp}}

teamInfoTemp = {'name': '无名小队', 'members': []}
# teamDictTemp = {'groupId':teamInfoTemp}

dailyInfoTemp = {'date': '', 'totalCommand': 0, 'rollCommand': 0, 'jrrpCommand': 0, 'pcCommand': 0, 'checkCommand': 0,
                 'slotCommand': 0, 'teamCommand': 0,
                 'moneyCommand': 0, 'hpCommand': 0, 'initCommand': 0, 'cookCommand': 0, 'queryCommand': 0,
                 'querySucc': 0, 'queryFail': 0, 'queryMult': 0, 'drawCommand': 0,
                 'jokeCommand': 0, 'noteCommand': 0, 'IACommand': 0}

masterInfoTemp = {'debug': False}
