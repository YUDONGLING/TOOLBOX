def _FindIp(Headers: dict, NameList: list, FallbackIp: str = '0.0.0.0') -> str:
    for _ in NameList:
        if _ in Headers:
            _Ip = Headers[_].split(',')[0].strip() != ''
            if _Ip: return _Ip
    return FallbackIp


def _ConvertSnakeCase(Body: dict) -> dict:
    def SnakeCase(Dict):
        _Dict = {}
        for _Key, _Value in Dict.items():
            _Key = ''.join(['_' + _.lower() if (_.isupper() and (_Index == 0 or not _Key[_Index - 1].isupper())) else _.lower() for _Index, _ in enumerate(_Key)]).lstrip('_')
            if isinstance(_Value, dict):
                _Dict[_Key] = _Value if _Value.get('*Ignore', False) else SnakeCase(_Value); continue
            if isinstance(_Value, list):
                _Dict[_Key] = [SnakeCase(_) if isinstance(_, dict) else _ for _ in _Value] ; continue
            _Dict[_Key] = _Value
        return _Dict
    return SnakeCase(Body)


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


class FcWsgi(object):
    '''
    A WSGI Application for Function Compute.
    '''
    def __init__(self, environ, start_response):
        import json
        import time
        import urllib.parse

        self._T1 = int(time.time() * 1000) # T1: Time @ Initing the Instance (Millisecond)
        self._T2 = -1                      # T2: Time @ Initing the Payloads (Millisecond)
        self._T3 = -1                      # T3: Time @ Sending the Response (Millisecond)
        self._T4 = -1                      # T4: Time @ Destroy the Instance (Millisecond)

        self._Inn_Size = -1                # Content Length of Requests Body
        self._Out_Size = -1                # Content Length of Response Body
        self._Out_Body = ''                # Response
        self._Out_Code = ''                # Response
        self._Out_Head = {}                # Response

        self._Geo           = ''
        self._Environ       = environ
        self._StartResponse = start_response

        self.Ram = {
            'Uid'   : self._Environ['FC_ACCOUNT_ID'],
            'AK'    : self._Environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
            'SK'    : self._Environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'],
            'Token' : self._Environ['ALIBABA_CLOUD_SECURITY_TOKEN'],
            'Region': self._Environ['FC_REGION']
        }

        self.Instance = {
            'Service' : self._Environ['FC_SERVICE_NAME'],
            'Function': self._Environ['FC_FUNCTION_NAME'],
            'Version' : self._Environ['FC_QUALIFIER'],
            'Instance': self._Environ['FC_INSTANCE_ID']
        }

        self.Id = self._Environ['fc.context'].request_id
        self.Ip = _FindIp(
            self._Environ,
            [
                'HTTP_X_FORWARDED_FOR',
                'HTTP_X_REAL_IP',
                'HTTP_X_FORWARDED',
                'HTTP_FORWARDED_FOR',
                'HTTP_FORWARDED',
                'HTTP_TRUE_CLIENT_IP',
                'HTTP_CLIENT_IP',
                'HTTP_ALI_CDN_REAL_IP',
                'HTTP_CDN_SRC_IP',
                'HTTP_CDN_REAL_IP',
                'HTTP_CF_CONNECTING_IP',
                'HTTP_X_CLUSTER_CLIENT_IP',
                'HTTP_WL_PROXY_CLIENT_IP',
                'HTTP_PROXY_CLIENT_IP',
                'HTTP_TRUE_CLIENT_IP',
                'REMOTE_ADDR'
            ],
            '0.0.0.0'
        )
        self.Ua = self._Environ.get('HTTP_USER_AGENT', '')

        self.Method  = self._Environ.get('REQUEST_METHOD', '').upper()
        self.Host    = self._Environ.get('HTTP_HOST', '').lower()
        self.Path    = urllib.parse.unquote(self._Environ.get('PATH_INFO', ''))
        self.Referer = self._Environ.get('HTTP_REFERER', '')

        self.Header  = {}
        for _Key, _Value in self._Environ.items():
            if _Key.startswith('HTTP_') and _Key not in ['HTTP_ALI_CDN_ADAPTIVE_PORTS', 'HTTP_ALI_CDN_REAL_IP', 'HTTP_ALI_SWIFT_LOG_HOST', 'HTTP_ALI_SWIFT_STAT_HOST', 'HTTP_EAGLEEYE_TRACEID', 'HTTP_VIA', 'HTTP_X_CDN_DAUTH_DATE', 'HTTP_X_CDN_ORIGIN_DAUTH', 'HTTP_X_CLIENT_SCHEME', 'HTTP_X_FORWARDED_FOR', 'HTTP_X_FORWARDED_PROTO', 'HTTP_X_OSS_SECURITY_TOKEN', 'HTTP_X_FC_FUNCTION_HANDLER', 'HTTP_COOKIE']:
                self.Header[
                    urllib.parse.unquote(_Key[5:].replace('_', '-').lower())
                ] = urllib.parse.unquote(_Value)

        self.Cookie  = {}
        for _Key_Value in [_.split('=', 1) for _ in urllib.parse.unquote(self._Environ.get('HTTP_COOKIE', '')).split('; ') if _]:
            if len(_Key_Value) > 1:
                try:    self.Cookie[urllib.parse.unquote(_Key_Value[0]).lower()] = json.loads(urllib.parse.unquote(_Key_Value[1]))
                except: self.Cookie[urllib.parse.unquote(_Key_Value[0]).lower()] = urllib.parse.unquote(_Key_Value[1])
            else:
                self.Cookie[urllib.parse.unquote(_Key_Value[0]).lower()] = ''

        self.Params  = {}
        for _Key_Value in [_.split('=', 1) for _ in urllib.parse.unquote(self._Environ.get('QUERY_STRING', '')).split('&') if _]:
            if len(_Key_Value) > 1:
                try:    self.Params[urllib.parse.unquote(_Key_Value[0])] = json.loads(urllib.parse.unquote(_Key_Value[1]))
                except: self.Params[urllib.parse.unquote(_Key_Value[0])] = urllib.parse.unquote(_Key_Value[1])
            else:
                self.Params[urllib.parse.unquote(_Key_Value[0])] = ''

        self.Payload = self.DecodePayload()

        self.Storage = {}
        self.Options = {
            'Log.Enable'      : False,
            'Log.Remote'      : False,
            'Log.Prefix'      : '',
            'Log.Key'         : '',

            'Body.Enable'     : False,
            'Body.Remote'     : False,
            'Body.Prefix'     : '',
            'Body.Key'        : '',

            'Webhook.Enable'  : False,
            'Webhook.Request' : False,
            'Webhook.Response': False,
        }

        self._T2 = int(time.time() * 1000) # T2: Time @ Initing the Payloads (Millisecond)
      # self._T3 = -1                      # T3: Time @ Sending the Response (Millisecond)
      # self._T4 = -1                      # T4: Time @ Destroy the Instance (Millisecond)

    def __call__(self, Body, Code: str = '200', Header: dict = None, SnakeCase: bool = True):
        import json
        import time

        self._Out_Body = Body if isinstance(Body, str) else json.dumps(_ConvertSnakeCase(Body) if SnakeCase else Body, ensure_ascii = False)
        self._Out_Code = Code
        self._Out_Size = len(self._Out_Body)

        try:
            self._Out_Head = {_Key.lower(): _Value for _Key, _Value in Header.items()}
            self._Out_Head.setdefault('content-type', 'application/json')
        except Exception as Error:
            self._Out_Head = {'content-type': 'application/json'}

        self._StartResponse(self._Out_Code, [(_Key, _Value) for _Key, _Value in Header.items()])

        self._T3 = int(time.time() * 1000) # T3: Time @ Sending the Response (Millisecond)
      # self._T4 = -1                      # T4: Time @ Destroy the Instance (Millisecond)

        return [self._Out_Body]

    @property
    def Geo(self):
        if self._Geo: return self._Geo

        if not __package__:
              from  Network import QueryIpLocation
        else: from .Network import QueryIpLocation

        self._Geo = QueryIpLocation(self.Ip, {'User-Agent': self.Ua}); return self._Geo

    def DecodePayload(self):
        import json
        import urllib.parse

        def __DecodeJson(_):
            try:    return json.loads(_)
            except: return {}

        def __DecodeForm(_):
            try:
                Form = {}
                for _Key_Value in [_.split('=', 1) for _ in urllib.parse.unquote(_).split('&') if _]:
                    if len(_Key_Value) > 1:
                        try:    Form[urllib.parse.unquote(_Key_Value[0])] = json.loads(urllib.parse.unquote(_Key_Value[1]))
                        except: Form[urllib.parse.unquote(_Key_Value[0])] = urllib.parse.unquote(_Key_Value[1])
                    else:
                        Form[urllib.parse.unquote(_Key_Value[0])] = ''
                return Form
            except:
                return {}
            
        def __DecodeMultipart(_):
            import cgi
            try:
                Form = {}
                FieldStorage = cgi.FieldStorage(fp = _['wsgi.input'], environ = _, keep_blank_values = True)
                for Field in FieldStorage.keys():
                    if FieldStorage[Field].filename:
                        Form[Field] = {'filename': FieldStorage[Field].filename, 'content': FieldStorage[Field].file.read()}
                    else:
                        Form[Field] = FieldStorage[Field].value
                return Form
            except:
                return {}

        self._Inn_Size = int(self._Environ.get('CONTENT_LENGTH', '0'))

        if self._Inn_Size <= 0:
            return {}

        if 'multipart/form-data' in self._Environ.get('CONTENT_TYPE', '').lower():
            return __DecodeMultipart(self._Environ)

        _Input = self._Environ['wsgi.input'].read(self._Inn_Size).decode('utf-8')

        if 'application/json' in self._Environ.get('CONTENT_TYPE', '').lower():
            return __DecodeJson(_Input)

        if 'application/x-www-form-urlencoded' in self._Environ.get('CONTENT_TYPE', '').lower():
            return __DecodeForm(_Input)

        return __DecodeJson(_Input) or __DecodeForm(_Input) or {}

    async def CallLog(self, Bucket: str = None, Region: str = None):
        return _CallLog(self, Bucket, Region)

    async def CallWebhook(self, Token: str, Topic: str = None):
        return _CallWebhook(self, Token, Topic)


class FlaskWsgi(object):
    '''
    A WSGI Application for Flask.
    '''
    def __init__(self, environ, flask_request):
        import os
        import json
        import time
        import random
        import traceback
        import urllib.parse

        if not __package__:
              from  UUID import HashUUID
        else: from .UUID import HashUUID

        self._T1 = int(time.time() * 1000) # T1: Time @ Initing the Instance (Millisecond)
        self._T2 = -1                      # T2: Time @ Initing the Payloads (Millisecond)
        self._T3 = -1                      # T3: Time @ Sending the Response (Millisecond)
        self._T4 = -1                      # T4: Time @ Destroy the Instance (Millisecond)

        self._Inn_Size = -1                # Content Length of Requests Body
        self._Out_Size = -1                # Content Length of Response Body
        self._Out_Body = ''                # Response
        self._Out_Code = ''                # Response
        self._Out_Head = {}                # Response

        self._Geo          = ''
        self._Environ      = environ
        self._FlaskRequest = flask_request

        self.Ram = {
            'Uid'   : self._Environ.get('Uid', ''),
            'AK'    : self._Environ.get('AK', ''),
            'SK'    : self._Environ.get('SK', ''),
            'Token' : self._Environ.get('Token', ''),
            'Region': self._Environ.get('Region', '')
        }

        try: self.Instance = {
            'Service' : self._FlaskRequest.environ.get('SERVER_SOFTWARE', '').split('/')[ 0] or 'Flask',
            'Function': traceback.extract_stack()[-2].name.title().replace('_', '') if len(traceback.extract_stack()) > 1 else 'None',
            'Version' : self._FlaskRequest.environ.get('SERVER_SOFTWARE', '').split('/')[-1] or 'None',
            'Instance': HashUUID(''.join(os.uname()))
        }
        except Exception as Error: self.Instance = {
            'Service' : 'Flask',
            'Function': 'None',
            'Version' : 'None',
            'Instance': '00000000-0000-0000-0000-000000000000'
        }

        self.Id = '%d%09d' % (int(time.time() * 1000), random.randint(1, 999999999))
        self.Ip = _FindIp(
            self._FlaskRequest.headers,
            [
                'x-forwarded-for',
                'x-real-ip',
                'x-forwarded',
                'forwarded-for',
                'forwarded',
                'true-client-ip',
                'client-ip',
                'ali-cdn-real-ip',
                'cdn-src-ip',
                'cdn-real-ip',
                'cf-connecting-ip',
                'x-cluster-client-ip',
                'wl-proxy-client-ip',
                'proxy-client-ip',
                'true-client-ip'
            ],
            self._FlaskRequest.remote_addr or '0.0.0.0'
        )
        self.Ua = self._FlaskRequest.headers.get('user-agent', '')

        self.Method  = self._FlaskRequest.method
        self.Host    = self._FlaskRequest.host
        self.Path    = self._FlaskRequest.path
        self.Referer = self._FlaskRequest.headers.get('referer', '')

        self.Header  = {}
        for _Key, _Value in self._FlaskRequest.headers.items():
            if _Key.upper() not in ['ALI-CDN-ADAPTIVE-PORTS', 'ALI-CDN-REAL-IP', 'ALI-SWIFT-LOG-HOST', 'ALI-SWIFT-STAT-HOST', 'EAGLEEYE-TRACEID', 'VIA', 'X-CDN-DAUTH-DATE', 'X-CDN-ORIGIN-DAUTH', 'X-CLIENT-SCHEME', 'X-FORWARDED-FOR', 'X-FORWARDED-PROTO', 'X-OSS-SECURITY-TOKEN', 'X-FC-FUNCTION-HANDLER', 'COOKIE']:
                self.Header[
                    urllib.parse.unquote(_Key).lower()
                ] = urllib.parse.unquote(_Value)

        self.Cookie  = {}
        for _Key, _Value in self._FlaskRequest.cookies.items():
            try:    self.Cookie[urllib.parse.unquote(_Key.lower())] = json.loads(urllib.parse.unquote(_Value))
            except: self.Cookie[urllib.parse.unquote(_Key.lower())] = urllib.parse.unquote(_Value)

        self.Params  = {}
        for _Key, _Value in self._FlaskRequest.args.items():
            try:    self.Params[urllib.parse.unquote(_Key)] = json.loads(urllib.parse.unquote(_Value))
            except: self.Params[urllib.parse.unquote(_Key)] = urllib.parse.unquote(_Value)

        self.Payload = self.DecodePayload()

        self.Storage = {}
        self.Options = {
            'Log.Enable'      : False,
            'Log.Remote'      : False,
            'Log.Prefix'      : '',
            'Log.Key'         : '',

            'Body.Enable'     : False,
            'Body.Remote'     : False,
            'Body.Prefix'     : '',
            'Body.Key'        : '',

            'Webhook.Enable'  : False,
            'Webhook.Request' : False,
            'Webhook.Response': False,
        }

        self._T2 = int(time.time() * 1000) # T2: Time @ Initing the Payloads (Millisecond)
      # self._T3 = -1                      # T3: Time @ Sending the Response (Millisecond)
      # self._T4 = -1                      # T4: Time @ Destroy the Instance (Millisecond)

    def __call__(self, Body, Code: str = '200', Header: dict = None, SnakeCase: bool = True):
        import json
        import time

        self._Out_Body = Body if isinstance(Body, str) else json.dumps(_ConvertSnakeCase(Body) if SnakeCase else Body, ensure_ascii = False)
        self._Out_Code = Code
        self._Out_Size = len(self._Out_Body)

        try:
            self._Out_Head = {_Key.lower(): _Value for _Key, _Value in (Header or {}).items()}
            self._Out_Head.setdefault('content-type', 'application/json')
        except Exception as Error:
            self._Out_Head = {'content-type': 'application/json'}

        self._T3 = int(time.time() * 1000) # T3: Time @ Sending the Response (Millisecond)
      # self._T4 = -1                      # T4: Time @ Destroy the Instance (Millisecond)

        return self._Out_Body, self._Out_Code, self._Out_Head

    @property
    def Geo(self):
        if self._Geo: return self._Geo

        if not __package__:
              from  Network import QueryIpLocation
        else: from .Network import QueryIpLocation

        self._Geo = QueryIpLocation(self.Ip, {'User-Agent': self.Ua}); return self._Geo

    def DecodePayload(self):
        def __DecodeJson(_):
            try:    return _.get_json(force = True) or {}
            except: return {}

        def __DecodeForm(_):
            try:    return dict(_.form)
            except: return {}
            
        def __DecodeMultipart(_):
            try:
                Form = {}
                for Field in _.files:
                    Fp = _[Field]
                    Form[Field] = {'filename': Fp.filename, 'content': Fp.read()}
                for Field in _.form:
                    Form[Field] = _.form[Field]
                return Form
            except: return {}

        self._Inn_Size = self._FlaskRequest.content_length or 0

        if self._Inn_Size <= 0:
            return {}

        if 'multipart/form-data' in self._FlaskRequest.content_type.lower():
            return __DecodeMultipart(self._FlaskRequest)

        if 'application/json' in self._FlaskRequest.content_type.lower():
            return __DecodeJson(self._FlaskRequest)

        if 'application/x-www-form-urlencoded' in self._FlaskRequest.content_type.lower():
            return __DecodeForm(self._FlaskRequest)

        return __DecodeJson(self._FlaskRequest) or __DecodeForm(self._FlaskRequest) or {}

    async def CallLog(self, Bucket: str = None, Region: str = None):
        return _CallLog(self, Bucket, Region)

    async def CallWebhook(self, Token: str, Topic: str = None):
        return _CallWebhook(self, Token, Topic)


class FlowControl(object):
    '''
    API Flow Control. \n
    Limit the Number of Requests in a Period of Time with a Specific Feature.
    '''
    def __init__(self, TTL: int, Quota: int, Feature: str | list, Options: dict = None):
        import os
        import time

        if not __package__:
              from  Init import MergeDictionaries; from  UUID import HashUUID
        else: from .Init import MergeDictionaries; from .UUID import HashUUID

        self._TTL     = self.TTL   = TTL
        self._Quota   = self.Quota = Quota
        self._Feature = Feature if isinstance(Feature, list) else [Feature]; self._Feature = [str(_) for _ in sorted(self._Feature)]

        DftOpts = {
            'Folder'    : 'FlowCtrl',
            'Prefix.+'  : 'P',
            'Prefix.-'  : 'M'
        }
        self._Options = MergeDictionaries(DftOpts, Options)

        try:
            os.makedirs(self._Options['Folder'], exist_ok = True)
        except Exception as Error:
            self._Options['Folder']   = self._Options['Folder'].replace('/', '-').replace('\\', '-')
            self._Options['Prefix.+'] = '%s_%s' % (self._Options['Folder'], self._Options['Prefix.+'])
            self._Options['Prefix.-'] = '%s_%s' % (self._Options['Folder'], self._Options['Prefix.-'])
            self._Options['Folder']   = ''

        self._HashKey     = '%s_%s_' % (int(time.time() // self._TTL), HashUUID('_'.join(self._Feature)))
        self._Plus_Prefix = '%s_%s'  % (self._Options['Prefix.+'], self._HashKey)
        self._Minu_Prefix = '%s_%s'  % (self._Options['Prefix.-'], self._HashKey)

    def __iadd__(self, Count: int) -> object:
        for _ in range(Count): self.__MakeFile(self._Plus_Prefix)
        return self
    
    def __isub__(self, Count: int) -> object:
        for _ in range(min(Count, self.Count)): self.__MakeFile(self._Minu_Prefix)
        return self

    def __MakeFile(self, Prefix):
        import os
        import uuid
        try:
            with open(os.path.join(self._Options['Folder'], '%s%s' % (Prefix, uuid.uuid4())), 'w') as File: File.write('')
        except Exception as Error: pass

    def __CountFile(self, Prefix):
        import os
        try:
            return len([File for File in os.listdir(self._Options['Folder']) if File.startswith(Prefix)])
        except Exception as Error: return 0

    @property
    def OK(self) -> bool:
        '''
        Get the Status of the Flow Control.
        '''
        return self.Count <= self._Quota

    @property
    def Count(self) -> int:
        return self.__CountFile(self._Plus_Prefix) - self.__CountFile(self._Minu_Prefix)

    @property
    def RetryAfter(self) -> int:
        import time
        return 0 if self.OK else int((time.time() // self._TTL + 1) * self._TTL - time.time())

    def Reset(self):
        '''
        Reset the Flow Control.
        '''
        self = self.__isub__(self.Count)
