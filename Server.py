async def _CallLog(Wsgi: object, Bucket: str = None, Region: str = None) -> None:
    import json
    import time
    import asyncio

    if not __package__:
          from  Log import MakeLog; from  Oss import AppendObject, PutObject
    else: from .Log import MakeLog; from .Oss import AppendObject, PutObject

    _Await = []

    if Wsgi.Options['Log.Enable']:
        _LogKey = '%s%s' % (Wsgi.Options.get('Log.Prefix', ''), Wsgi.Options.get('Log.Key', ''))
        _LogStr = '%s - %s [%s] "%s /%s$%s@%s%s%s HTTP/1.1" %s %s %s "%s" "%s"\n' % (
            Wsgi.Ip,
            Wsgi.Id,
            time.strftime('%d/%b/%Y:%H:%M:%S %z', time.localtime()),
            Wsgi.Method,
            Wsgi.Instance['Service'],
            Wsgi.Instance['Function'],
            Wsgi.Instance['Version'],
            Wsgi.Path,
            '?%s' % ('&'.join(['%s=%s' % (Key, Value) for Key, Value in Wsgi.Params.items()])) if Wsgi.Params else '',
            Wsgi._Out_Code,
            Wsgi._Out_Size,
            Wsgi._T3 - Wsgi._T1,
            Wsgi.Referer,
            Wsgi.Ua
        )

        if Wsgi.Options['Log.Remote']:
            _Await.append(asyncio.to_thread(AppendObject,
                                            Key     = _LogKey,
                                            Data    = _LogStr,
                                            Options = {
                                                'Region'  : Region,
                                                'Bucket'  : Bucket,
                                                'AK'      : Wsgi.Ram['AK'],
                                                'SK'      : Wsgi.Ram['SK'],
                                                'STSToken': Wsgi.Ram['Token']
                                            }))
        else:
            MakeLog(Content = _LogStr, Path = _LogKey)

    if Wsgi.Options['Body.Enable']:
        _BodyKey  = '%s%s' % (Wsgi.Options.get('Body.Prefix', ''), (Wsgi.Options.get('Body.Key', '') or '%s.txt' % Wsgi.Id))
        _BodyStr  = ''
        _BodyStr += '[Header] %s\n\n'  % json.dumps(Wsgi.Header , ensure_ascii = False)
        _BodyStr += '[Cookie] %s\n\n'  % json.dumps(Wsgi.Cookie , ensure_ascii = False)
        _BodyStr += '[Params] %s\n\n'  % json.dumps(Wsgi.Params , ensure_ascii = False)
        _BodyStr += '[Payload] %s\n\n' % json.dumps(Wsgi.Payload, ensure_ascii = False)
        _BodyStr += '[Response] %s'    % Wsgi._Out_Body

        if Wsgi.Options['Body.Remote']:
            _Await.append(asyncio.to_thread(PutObject,
                                            Key     = _BodyKey,
                                            Data    = _BodyStr,
                                            Options = {
                                                'Region'  : Region,
                                                'Bucket'  : Bucket,
                                                'AK'      : Wsgi.Ram['AK'],
                                                'SK'      : Wsgi.Ram['SK'],
                                                'STSToken': Wsgi.Ram['Token']
                                            }))
        else:
            MakeLog(Content = _BodyStr, Path = _BodyKey)

    if _Await: await asyncio.gather(*_Await)
    return None


async def _CallWebhook(Wsgi: object, Token: str, Topic: str = None) -> None:
    if not Wsgi.Options['Webhook.Enable']: return None
    if Wsgi.Method in ['HEAD', 'OPTIONS']: return None

    import json
    import asyncio

    if not __package__:
          from  Webhook import DingTalk
    else: from .Webhook import DingTalk

    try:    _Body = json.loads(Wsgi._Out_Body)
    except: _Body = {}

    Message = [
        {
            'Title': '用户请求信息',
            'Color': 'BLUE',
            'Text' : [
                '请求接口: %s/%s' % (Wsgi.Instance['Service'], Wsgi.Instance['Function']),
                '请求方法: %s' % Wsgi.Method,
                '用户来源: %s' % Wsgi.Ip,
                '用户地区: %s' % Wsgi.Geo,
                '用户设备: %s' % Wsgi.Ua
            ]
        },
        {
            'Title': '接口响应信息',
            'Color': 'RED' if _Body.get('ErrorCode', _Body.get('error_code', _Body.get('Ec', _Body.get('ec', 9999)))) else 'GREEN',
            'Text' : [
                '集群编号: %s_%s' % (Wsgi.Instance['Service'], Wsgi.Instance['Instance']),  
                '错误代码: %s' % _Body.get('ErrorCode', _Body.get('error_code', _Body.get('Ec', _Body.get('ec', '')))) or 'None',
                '错误信息: %s' % _Body.get('ErrorMsg' , _Body.get('error_msg' , _Body.get('Em', _Body.get('em', '')))) or 'None'
            ]
        }
    ]

    if Wsgi.Options['Webhook.Request']:
        Message.append({
            'Title': '详细请求日志',
            'Color': 'BLUE',
            'Text' : [
                '请求参数: %s' % json.dumps(Wsgi.Params , ensure_ascii = False).replace('{}', 'None'),
                '请求负载: %s' % json.dumps(Wsgi.Payload, ensure_ascii = False).replace('{}', 'None')
            ]
        })

    if Wsgi.Options['Webhook.Response']:
        Message.append({
            'Title': '详细响应日志',
            'Color': 'BLUE',
            'Text' : [
                '响应负载: %s' % _Body
            ]
        })

    await asyncio.to_thread(DingTalk, Token, Topic or '【Serverless】WSGI 请求监控', Message)
    return None
