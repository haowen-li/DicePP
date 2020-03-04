__all__ = ["bot_tool"]

import time
from time import sleep

from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import on_request, RequestSession, on_notice, NoticeSession
from nonebot.permission import PRIVATE_FRIEND,PRIVATE_GROUP, PRIVATE_DISCUSS, PRIVATE_OTHER, PRIVATE
from nonebot.permission import DISCUSS, GROUP_MEMBER, GROUP_ADMIN, GROUP_OWNER, GROUP, SUPERUSER, EVERYBODY

from .bot_tool import Bot
from .custom_config import *

bot = Bot()
DEBUG_MODE = False
LIMIT_MODE = False

@on_command('PROCESS_COMMAND', only_to_me=True)
async def processCommand(session: CommandSession):
    commandResult = session.get('result')
    if DEBUG_MODE:
        print(f'Output:{commandResult.resultStr} Person:{commandResult.personIdList} Group:{commandResult.groupIdList}')
    if commandResult is None:
        return

    if commandResult.coolqCommand == CoolqCommandType.MESSAGE:
        # 如果群聊列表不为空, 则对指定的群发送消息
        if commandResult.groupIdList:
            nonebot = session.bot
            for gId in commandResult.groupIdList:
                await nonebot.send_group_msg(group_id=gId, message=commandResult.resultStr)
        else:
            # 如果用户列表不为空, 则对指定的用户发送消息
            nonebot = session.bot
            if commandResult.personIdList:
                for pId in commandResult.personIdList:
                    await nonebot.send_private_msg(user_id=pId, message=commandResult.resultStr)
            # 否则原样返回
            else:
                await session.send(commandResult.resultStr)
    elif commandResult.coolqCommand == CoolqCommandType.DISMISS:
        try:
            nonebot = session.bot
            for gId in commandResult.groupIdList:
                await nonebot.send_group_msg(group_id=gId, message=commandResult.resultStr)
                await nonebot.set_group_leave(group_id = gId)
        except:
            pass


@processCommand.args_parser
async def _(session: CommandSession):
    content = session.current_arg['arg']
    only_to_me = session.current_arg['only_to_me']
    if DEBUG_MODE:
        print(f'Input:{content}')
    uid = str(session.ctx['user_id'])
    uname = session.ctx['sender']['nickname']
    if 'group_id' not in session.ctx.keys():
        commandResult = bot.ProcessInput(content, uid, uname, only_to_me = only_to_me)
    else:
        groupId = str(session.ctx['group_id'])
        commandResult = bot.ProcessInput(content, uid, uname, groupId, only_to_me = only_to_me)

    session.state['result'] = commandResult

@on_natural_language(keywords={'.', '。'}, only_to_me=False)
async def _(session: NLPSession):
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    if session.msg_text[0] == '.' or session.msg_text[0] == '。':
        return IntentCommand(90.0, 'PROCESS_COMMAND', current_arg = {'arg':session.msg_text, 'only_to_me':False})

@on_natural_language(keywords={'.', '。'}, only_to_me=True)
async def _(session: NLPSession):
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    index = session.msg_text.find('.')
    if index == -1:
        index = session.msg_text.find('。')
    if index != -1:
        return IntentCommand(91.0, 'PROCESS_COMMAND', current_arg = {'arg':session.msg_text[index:], 'only_to_me':True})


@on_command('radio', permission = SUPERUSER)
async def processCommand(session: CommandSession):
    msg = session.current_arg_text
    nonebot = session.bot
    try:
        info = await nonebot.get_group_list()
    except CQHttpError:
        pass

    for groupInfo in info:
        try:
            await nonebot.send_group_msg(group_id=groupInfo['group_id'], message=msg)
            sleep(10)
            # print(f'RADIO to {groupInfo['group_name']} {groupInfo['group_id']}:{msg}')
        except:
            pass

@on_command('debug', permission = SUPERUSER)
async def processCommand(session: CommandSession):
    if DEBUG_MODE == True:
        await session.send('关闭调试模式')
        DEBUG_MODE = False
    else:
        await session.send('开启调试模式')
        DEBUG_MODE = True

@on_command('limit', permission = SUPERUSER)
async def processCommand(session: CommandSession):
    if LIMIT_MODE == True:
        await session.send('关闭限制模式')
        LIMIT_MODE = False
    else:
        await session.send('开启限制模式')
        LIMIT_MODE = True


# 将函数注册为好友请求处理器
@on_request('friend')
async def _(session: RequestSession):
    # 判断验证信息是否符合要求
    # if session.ctx['comment'] == 'DND5E':
    #     # 验证信息正确，同意
    #     await session.approve()
    # await session.reject('请说正确的暗号')
    await session.approve()

# 将函数注册为群请求处理器
@on_request('group')
async def _(session: RequestSession):
    # 判断验证信息是否符合要求
    if session.ctx['sub_type'] == 'invite':
        if LIMIT_MODE and session.ctx['comment'] != GROUP_PASSWORD:
        # 验证信息错误，拒绝入群
            await session.reject('请输入正确的暗号')
        else:
        # 验证信息正确或不需要验证，同意入群
            try:
                # for mId in MASTER:
                #     await nonebot.send_private_msg(user_id=mId, message=f'经{session.ctx["user_id"]}邀请, 加入群{session.ctx["group_id"]}')
                nonebot = session.bot
                for gId in MASTER_GROUP:
                    await nonebot.send_group_msg(group_id=gId, message=f'经{session.ctx["user_id"]}邀请, 加入群{session.ctx["group_id"]}')
            except:
                pass
            await session.approve()

@on_notice('group_increase')
async def _(session: NoticeSession):
    # 发送欢迎消息
    if session.ctx['user_id'] != SELF_ID:
        await session.send(f'欢迎新人~')