__all__ = ["bot_tool"]


from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import on_request, RequestSession, on_notice, NoticeSession

from .bot_tool import Bot
from .custom_config import *

bot = Bot()

@on_command('PROCESS_COMMAND', only_to_me=True)
async def processCommand(session: CommandSession):
    result = session.get('result')
    print(f'Output:{result}')
    await session.send(result)

@processCommand.args_parser
async def _(session: CommandSession):
    content = session.current_arg['arg']
    only_to_me = session.current_arg['only_to_me']
    print(f'Input:{content}')
    uid = str(session.ctx['user_id'])
    uname = session.ctx['sender']['nickname']
    if 'group_id' not in session.ctx.keys():
        result = bot.ProcessInput(content, uid, uname, only_to_me = only_to_me)
    else:
        groupId = str(session.ctx['group_id'])
        result = bot.ProcessInput(content, uid, uname, groupId, only_to_me = only_to_me)

    session.state['result'] = result

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

# @on_natural_language(keywords={'.send', '。send'}, only_to_me=True)
# async def _(session: NLPSession):
#     # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
#     if session.msg_text[0] == '.' or session.msg_text[0] == '。':
#         if session.msg_text[1:5] == 'send':
#             await session.send(result)





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
    # if session.ctx['sub_type'] == 'invite' and session.ctx['comment'] == 'DND5E':
    #     # 验证信息正确，同意入群
    #     await session.approve()
    # # 验证信息错误，拒绝入群
    # await session.reject('请说正确的暗号')
    await session.approve()

@on_notice('group_increase')
async def _(session: NoticeSession):
    # 发送欢迎消息
    await session.send(f'欢迎新人~')