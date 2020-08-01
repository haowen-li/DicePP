__all__ = ["bot_core"]

import time
from time import sleep
import datetime
import asyncio
import os

import nonebot
from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import on_request, RequestSession, on_notice, NoticeSession
from nonebot.permission import PRIVATE_FRIEND,PRIVATE_GROUP, PRIVATE_DISCUSS, PRIVATE_OTHER, PRIVATE
from nonebot.permission import DISCUSS, GROUP_MEMBER, GROUP_ADMIN, GROUP_OWNER, GROUP, SUPERUSER, EVERYBODY

from .bot_core import Bot, CoolqCommandType
from .custom_config import *

bot = Bot()
DEBUG_MODE = False
LIMIT_MODE = False

@on_command('PROCESS_MESSAGE', only_to_me=True)
async def processMessage(session: CommandSession):
    commandResultList = session.get('result')
    if DEBUG_MODE:
        print(f'Output:{[[commandResult.resultStr, commandResult.personIdList, commandResult.groupIdList]  for commandResult in commandResultList]}')
    if commandResultList:
        await processCommandResult(session, commandResultList)

@on_command('TEST', only_to_me=True)
async def _(session: CommandSession):
    try:
        print('JOKE IMG PATH')
        for i,j,k in os.walk(WINE_COOLQ_JOKEIMG_PATH):
            print(i,j,k)
        print('EMO IMG PATH')
        for i,j,k in os.walk(WINE_COOLQ_EMOTIMG_PATH):
            print(i,j,k)
        print('COOLQ IMG PATH')
        for i,j,k in os.walk(WINE_COOLQ_PATH):
            print(i,j,k)
    except Error as e:
        print(e)


@on_command('pull group', only_to_me=True)
async def _(session: CommandSession):
    botNone = nonebot.get_bot()
    info = None
    try:
        info = await botNone.get_group_list()
    except CQHttpError:
        for pId in MASTER:
            await botNone.send_private_msg(user_id=pId, message="自动获取群信息失败!")
    if info:
        groupInfoDictUpdate = {}
        for gInfo in info:
            groupInfoDictUpdate[gInfo['group_id']] = gInfo['group_name']
        commandResultList = await bot.UpdateGroupInfo(groupInfoDictUpdate)
        for pId in MASTER:
            await botNone.send_private_msg(user_id=pId, message="手动拉取群信息成功! "+f'{groupInfoDictUpdate}'[:200])
        if commandResultList:
            await processCommandResult(None, commandResultList)

@processMessage.args_parser
async def _(session: CommandSession):
    content = session.current_arg['arg']
    onlyToMe = session.current_arg['only_to_me']
    if DEBUG_MODE:
        print(f'Input:{content}')
    uid = str(session.ctx['user_id'])
    uname = session.ctx['sender']['nickname']
    groupId = None
    if 'group_id' in session.ctx.keys():
        groupId = str(session.ctx['group_id'])
        # 如果来自群聊, 尝试查询用户的群名片
        # try:
        #     nonebot = session.bot
        #     memberInfo = nonebot.get_group_member_info(groupId, uid)
        #     if memberInfo['card']:
        #         uname = memberInfo['card']
        # except Exception as e:
        #     print(e)

    commandResult = await bot.ProcessMessage(content, uid, uname, groupId, onlyToMe)

    session.state['result'] = commandResult

@on_natural_language(keywords=None, only_to_me=False)
async def _(session: NLPSession):
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'PROCESS_MESSAGE', current_arg = {'arg':session.msg_text, 'only_to_me':False})

@on_natural_language(keywords=None, only_to_me=True)
async def _(session: NLPSession):
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(91.0, 'PROCESS_MESSAGE', current_arg = {'arg':session.msg_text, 'only_to_me':True})


# @on_natural_language(keywords={'.', '。'}, only_to_me=False)
# async def _(session: NLPSession):
#     # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
#     if session.msg_text[0] == '.' or session.msg_text[0] == '。':
#         return IntentCommand(90.0, 'PROCESS_MESSAGE', current_arg = {'arg':session.msg_text, 'only_to_me':False})

# @on_natural_language(keywords={'.', '。'}, only_to_me=True)
# async def _(session: NLPSession):
#     # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
#     text = session.msg_text.strip()
#     if text[0] == '.' or text[0] == '。':
#         return IntentCommand(91.0, 'PROCESS_MESSAGE', current_arg = {'arg':text, 'only_to_me':True})

async def processCommandResult(session, commandResultList):
    for commandResult in commandResultList:
        if commandResult.coolqCommand == CoolqCommandType.MESSAGE:
            # 如果群聊列表不为空, 则对指定的群发送消息
            if commandResult.groupIdList:
                if session:
                    botNone = session.bot
                else:
                    botNone = nonebot.get_bot()
                for gId in commandResult.groupIdList:
                    await botNone.send_group_msg(group_id=gId, message=commandResult.resultStr)
            else:
                # 如果用户列表不为空, 则对指定的用户发送消息
                if session:
                    botNone = session.bot
                else:
                    botNone = nonebot.get_bot()
                if commandResult.personIdList:
                    for pId in commandResult.personIdList:
                        await botNone.send_private_msg(user_id=pId, message=commandResult.resultStr)
                # 否则原样返回
                else:
                    if session:
                        await session.send(commandResult.resultStr)
                    else:
                        print('未指定发送对象!')
        elif commandResult.coolqCommand == CoolqCommandType.DISMISS:
            try:
                if session:
                    botNone = session.bot
                else:
                    botNone = nonebot.get_bot()
                if commandResult.groupIdList:
                    for gId in commandResult.groupIdList:
                        if commandResult.resultStr:
                            await botNone.send_group_msg(group_id=gId, message=commandResult.resultStr)
                        await botNone.set_group_leave(group_id = gId)
                else:
                    print('未指定退群对象!')
            except:
                pass

# @nonebot.scheduler.scheduled_job(
#     'interval',
#     # weeks=0,
#     # days=0,
#     # hours=0,
#     minutes=5,
#     # seconds=0,
#     # start_date=time.now(),
#     # end_date=None,
# )
# async def _():
#     bot.UpdateTime(datetime.now())


@nonebot.scheduler.scheduled_job(
    'cron',
    hour=0,
    timezone='Asia/Shanghai'
)
async def _():
    commandResultList = await bot.DailyUpdate()
    if commandResultList:
        await processCommandResult(None, commandResultList)


@nonebot.scheduler.scheduled_job(
    'interval',
    minutes=10,
)
async def _():
    await bot.UpdateLocalData()

# 无法正常处理Linux环境的情况, 应改用额外脚本清理
# @nonebot.scheduler.scheduled_job(
#     'interval',
#     hours=1,
# )
# async def _():
#     botNone = nonebot.get_bot()
#     await botNone.clean_data_dir(data_dir='image')
#     await botNone.clean_data_dir(data_dir='record')
#     await botNone.clean_plugin_log()

# 可能会删除存在的群, 暂时不执行该命令
# @nonebot.scheduler.scheduled_job(
#     'interval',
#     hours=24,
# )
# async def _():
#     botNone = nonebot.get_bot()
#     info = None
#     try:
#         info = await botNone.get_group_list()
#     except CQHttpError:
#         for pId in MASTER:
#             await botNone.send_private_msg(user_id=pId, message="自动获取群信息失败!")
#     if info:
#         groupInfoDictUpdate = {}
#         for gInfo in info:
#             groupInfoDictUpdate[str(gInfo['group_id'])] = gInfo['group_name']
#         commandResultList = await bot.UpdateGroupInfo(groupInfoDictUpdate)
#         if commandResultList:
#             await processCommandResult(None, commandResultList)

# 将函数注册为好友请求处理器
@on_request('friend')
async def _(session: RequestSession):
    # 判断验证信息是否符合要求
    if session.ctx['comment'] == '伊丽傻白':
        # 验证信息正确，同意
        await session.approve()
    await session.reject('请说正确的暗号')
    # await session.approve()

# 将函数注册为群请求处理器
@on_request('group')
async def _(session: RequestSession):
    # 判断验证信息是否符合要求
    groupId = str(session.ctx["group_id"])
    personId = str(session.ctx["user_id"])
    if session.ctx['sub_type'] == 'invite':
        isValid = await bot.ValidateGroupInvite(groupId, personId)
        if isValid and session.ctx['comment'] == '伊丽傻白':
            try:
                nonebot = session.bot
                try:
                    strangerInfo = await nonebot.get_stranger_info(user_id = session.ctx["user_id"], no_cache = True)
                    nickName = strangerInfo["nickname"]
                except:
                    nickName = ''
                try:
                    groupInfo = await nonebot.get_group_info (group_id = session.ctx["group_id"])
                    groupName = groupInfo["group_name"]
                except:
                    groupName = ''
                
                for gId in MASTER_GROUP:
                    await nonebot.send_group_msg(group_id=gId, message=f'经{nickName} {personId}邀请, 加入群{groupName} {groupId}')
            except Exception as e:
                try:
                    for mId in MASTER:
                        await nonebot.send_private_msg(user_id=mId, message=str(e))
                except:
                    pass
            await session.approve()
        else:
            # 拒绝入群
            await session.reject('你的条件不符合哦~')

@on_notice('group_increase')
async def _(session: NoticeSession):
    # 发送欢迎消息
    if session.ctx['user_id'] != SELF_ID:
        welcomeStr = bot.GetWelcome(session.ctx['group_id'])
        await session.send(welcomeStr)