def Lark(Token: str, Topic: str = '', Message: list = []) -> dict:
    '''
    Send Message to Lark Chat Group.
    '''
    raise NotImplementedError()


def Slack(Token: str, Topic: str = '', Message: list = []) -> dict:
    '''
    Send Message to Slack Chat Group.
    '''
    raise NotImplementedError()


def WeChat(Token: str, Topic: str = '', Message: list = []) -> dict:
    '''
    Send Message to Enterprise WeChat Chat Group. `Token` Should Likes `{{ACCESS_TOKEN}}|{{CHAT_ID}}`.
    '''
    raise NotImplementedError()


def DingTalk(Token: str, Topic: str = '', Message: list = []) -> dict:
    '''
    Send Message to DingTalk Chat Group.
    '''
    import json
    import time
    import requests

    if not __package__:
          from  Log import MakeErrorMessage
    else: from .Log import MakeErrorMessage

    Response = {
        'Ec': 0, 'Em': ''
    }

    try:
        MessageBody = '<font color=#6A65FF>**%s**</font> \n\n %s \n\n' % (Topic, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        for Item in Message:
            if Item.get('Title', '') == '':
                MessageBody += ' --- \n\n '
            else:
                Color = Item.get('Color', 'UNKNOW').upper()
                if not Color.startswith('#') or len(Color) != 7:
                    Color = {'PURPLE': '#6A65FF', 'RED': '#FF6666', 'GREEN': '#92D050', 'BLUE': '#76CCFF'}.get(Color, '#76CCFF')
                MessageBody += ' --- \n\n <font color=%s>**%s**</font> \n\n ' % (Color, Item.get('Title', ''))
            MessageBody += ' \n\n '.join(Item.get('Text', [])) + ' \n\n '

        MessageBody += '<font color=#6A65FF>%s</font>' % Topic
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Url = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % Token.removeprefix('https://oapi.dingtalk.com/robot/send?access_token=')
        Hed = {
            'content-type': 'application/json'
        }
        Dat = {
            'msgtype'  : 'markdown',
            'markdown' : {
                'title': Topic,
                'text' : MessageBody
            }
        }
        Rsp = requests.post(Url, headers = Hed, data = json.dumps(Dat), timeout = 10).json()

        if Rsp['errcode'] != 0:
            raise Exception('%s-%s' % (Rsp['errcode'], Rsp['errmsg']))
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def Telegram(Token: str, Topic: str = '', Message: list = []) -> dict:
    '''
    Send Message via Telegram Bot.
    '''
    raise NotImplementedError()


def SeverChan(Token: str, Topic: str = '', Message: list = []) -> dict:
    '''
    Send Message via SeverChan.
    '''
    raise NotImplementedError()
