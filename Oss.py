class ProgressBar(object):
    '''
    Tqdm Progress Bar.
    '''
    def __init__(self, Description, Total):
        import tqdm
        self.Bar  = tqdm.tqdm(desc = Description, total = Total, unit = 'B', unit_scale = True)

    def __call__(self, Consumed, Total):
        self.Bar.total = Total or self.Bar.total
        self.Bar.update(Consumed - self.Bar.n)

    def Close(self):
        self.Bar.update(self.Bar.total - self.Bar.n)
        self.Bar.close()


def _ValidateAndInitEndPoint(
        Options: object,
        RequireCheck: bool = True,
        RequireField: list = ['Region', 'Bucket', 'AK', 'SK'],
        EndPointFunc: callable = None,
        EndPointProduct: str = 'Oss',
        EndPointBucketKey: str = 'Oss.Bucket',
        **Kwargs
        ) -> object:
    if RequireCheck and RequireField and [_Key for _Key in RequireField if not Options[_Key]]:
        raise Exception('Missing Required Fields')

    if Options.Endpoint is None: Options.Endpoint = {}

    if isinstance(Options.Endpoint, str):
        Options.Endpoint = Options.Endpoint.removeprefix('http://').removeprefix('https://').removeprefix('//')

    if isinstance(Options.Endpoint, dict) and EndPointFunc:
        if EndPointBucketKey:
            Options.Endpoint.setdefault(EndPointBucketKey, Options.Bucket)
        Options.Endpoint = EndPointFunc(EndPointProduct, Options.Region, Options = Options.Endpoint)

    return Options


def _FormatContentType(Path: str = None, Value: str = None) -> str:
    if Value:
        return Value

    import mimetypes
    return (mimetypes.guess_type(str(Path).lower())[0] if Path else None) or 'application/octet-stream'


def _FormatContentDisposition(Value: str = None) -> str:
    if not Value:
        return 'attachment'

    from urllib.parse import quote
    return 'attachment; filename="%s"; filename*=utf-8\'\'%s' % (Value, quote(Value))


def _ExtractResponse(OSSSDKResponse: object) -> object:
    if hasattr(OSSSDKResponse, 'resp'):
        return OSSSDKResponse.resp
    raise Exception('Can Not Extract Response from OSS SDK Result Object, Please Check the Result Object Directly for Details')


def __Service(AK: str, SK: str, Region: str, STSToken: str = None, Timeout: int = None) -> object:
    '''
    Initiate an OSS Service Object.
    '''
    if not __package__:
          from  Aliyun import __EndPoint
    else: from .Aliyun import __EndPoint

    if STSToken:
        from oss2 import StsAuth
        Auth = StsAuth(AK, SK, STSToken, auth_version = 'v4')
    else:
        from oss2 import AuthV4
        Auth = AuthV4(AK, SK)

    from oss2 import Service as OssService
    return OssService(
        auth            = Auth,
        region          = Region,
        endpoint        = __EndPoint('Oss', Region),
        connect_timeout = Timeout
    )


def __Bucket(AK: str, SK: str, Region: str, Bucket: str, Cname: str = None, STSToken: str = None, Timeout: int = None) -> object:
    '''
    Initiate an OSS Bucket Object. \n
    The Endpoint Should Include BucketName when Given.
    '''
    if not __package__:
          from  Aliyun import __EndPoint
    else: from .Aliyun import __EndPoint

    if STSToken:
        from oss2 import StsAuth
        Auth = StsAuth(AK, SK, STSToken, auth_version = 'v4')
    else:
        from oss2 import AuthV4
        Auth = AuthV4(AK, SK)

    from oss2 import Bucket as OssBucket
    return OssBucket(
        auth            = Auth,
        region          = Region,
        bucket_name     = Bucket,
        endpoint        = Cname or __EndPoint('Oss', Region),
        is_cname        = True if Cname else False,
        connect_timeout = Timeout
    )


def __Sign(AK: str, SK: str, Region: str, Bucket: str, Method: str, Url: str, STSToken: str = None, Expires: int = None, Version: str = None) -> str:
    '''
    Sign a URL for Bucket Operation or Object Operation, and Return a Signed URL Startswith '/'.
    '''
    import hmac
    import time
    import base64
    import hashlib
    import urllib.parse

    Key_And_Query = Url.removeprefix('/')

    if Version == 'v1':
        if not Expires or not isinstance(Expires, int): Expires = int(time.time() + 3600)
        elif Expires < time.time(): Expires = int(time.time() + Expires)

        if STSToken: StringToSign = f'{Method}\n\n\n{Expires}\n/{Bucket}/{Key_And_Query}{"&" if "?" in Key_And_Query else "?"}security-token={STSToken}'
        else:        StringToSign = f'{Method}\n\n\n{Expires}\n/{Bucket}/{Key_And_Query}'

        Signature = urllib.parse.quote(base64.b64encode(hmac.new(SK.encode(), StringToSign.encode(), hashlib.sha1).digest()).decode(), safe = '')

        if STSToken: return f'/{Key_And_Query}{"&" if "?" in Key_And_Query else "?"}OSSAccessKeyId={AK}&Expires={Expires}&Signature={Signature}&security-token={urllib.parse.quote(STSToken, safe = "")}'
        else:        return f'/{Key_And_Query}{"&" if "?" in Key_And_Query else "?"}OSSAccessKeyId={AK}&Expires={Expires}&Signature={Signature}'

    else:
        if not Expires or not isinstance(Expires, int): Expires = 3600
        elif Expires > 604800: Expires = 604800

        CurrentTime = time.gmtime()
        Url, Query  = Key_And_Query.split('?') if '?' in Key_And_Query else (Key_And_Query, '')

        Param = {
            'x-oss-signature-version': 'OSS4-HMAC-SHA256',
            'x-oss-credential'       : f'{AK}/{time.strftime("%Y%m%d", CurrentTime)}/{Region}/oss/aliyun_v4_request',
            'x-oss-date'             : time.strftime("%Y%m%dT%H%M%SZ", CurrentTime),
            'x-oss-expires'          : str(Expires)
        }
        if STSToken: Param['x-oss-security-token'] = STSToken

        for _Key, _Value in [_Query.split('=', 1) if '=' in _Query else (_Query, '') for _Query in Query.split('&')]:
            Param[_Key] = _Value
        Param = dict(sorted(Param.items(), key = lambda x: x[0]))

        Query = ''
        for _Key, _Value in Param.items():
            if _Value: Query += '%s=%s&' % (urllib.parse.quote(_Key, safe=''), urllib.parse.quote(_Value, safe=''))
            elif _Key: Query += '%s&' % urllib.parse.quote(_Key, safe='')
        Query = Query[:-1]

        Sign = hmac.new(hmac.new(hmac.new(hmac.new(hmac.new(f'aliyun_v4{SK}'.encode(), time.strftime('%Y%m%d', CurrentTime).encode(), hashlib.sha256).digest(), Region.encode(), hashlib.sha256).digest(), 'oss'.encode(), hashlib.sha256).digest(), 'aliyun_v4_request'.encode(), hashlib.sha256).digest(), ('OSS4-HMAC-SHA256\n%s\n%s\n%s' % (Param['x-oss-date'], Param['x-oss-credential'].removeprefix(f'{AK}/'), hashlib.sha256(f'{Method}\n/{Bucket}{Url}\n{Query}\n\n\nUNSIGNED-PAYLOAD'.encode()).hexdigest())).encode(), hashlib.sha256).hexdigest()
        return f'/{Url}?{Query}&x-oss-signature={Sign}'


def SignUrl(Method: str, Key: str, Header: dict = None, Param: dict = None, Expires: int = 3600, Options: dict = None) -> dict:
    '''
    Sign a URL for Bucket Operation or Object Operation, and Return a Signed URL with Host.
    '''
    import urllib.parse

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  Aliyun import __EndPoint
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .Aliyun import __EndPoint

    DftOpts = {
        'Region'  : '',
        'Bucket'  : '',
        'Endpoint': None,
        'AK'      : '',
        'SK'      : '',
        'STSToken': None,
        'Timeout' : None
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '',
        'Url': {
            'Http'   : '',
            'Https'  : '',
            'NoSheme': ''
        }
    })

    try:
        Options = _ValidateAndInitEndPoint(
            Options,
            EndPointFunc = __EndPoint
        )
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if Key.removeprefix('/') == '':
            SignedUrl_WithoutEndpoint = __Sign(
                AK         = Options.AK,
                SK         = Options.SK,
                Region     = Options.Region,
                Bucket     = Options.Bucket,
                Method     = Method,
                Url        = Key + ((('&' if '?' in Key else '?') + urllib.parse.urlencode(Param)) if Param else ''),
                STSToken   = Options.STSToken,
                Expires    = Expires
            )
            Response['Url']['NoSheme'] = '%s%s' % (__EndPoint('Oss', Options.Region, Options = {'Oss.Bucket': Options.Bucket}) if not Options.Endpoint else Options.Endpoint, SignedUrl_WithoutEndpoint)
            Response['Url']['Https']   = 'https://%s' % Response['Url']['NoSheme']
            Response['Url']['Http']    = 'http://%s'  % Response['Url']['NoSheme']
        else:
            Response['Url']['NoSheme'] = __Bucket(
                AK         = Options.AK,
                SK         = Options.SK,
                Region     = Options.Region,
                Bucket     = Options.Bucket,
                Cname      = Options.Endpoint,
                STSToken   = Options.STSToken,
                Timeout    = Options.Timeout
            ).sign_url(
                method     = Method,
                key        = Key.removeprefix('/'),
                expires    = Expires,
                headers    = Header,
                params     = Param,
                slash_safe = True
            ).removeprefix('http://').removeprefix('https://').removeprefix('//')
            Response['Url']['Https']   = 'https://%s' % Response['Url']['NoSheme']
            Response['Url']['Http']    = 'http://%s'  % Response['Url']['NoSheme']
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def GetObject(Key: str = None, Url: str = None, Path: str = None, Header: dict = None, Param: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Get Object from OSS Bucket.
    '''
    import os

    from oss2 import Bucket
    from oss2 import AnonymousAuth
    from oss2.exceptions import NotFound

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  Aliyun import __EndPoint
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .Aliyun import __EndPoint

    DftOpts = {
        'Region'  : '',
        'Bucket'  : '',
        'Endpoint': None,
        'AK'      : '',
        'SK'      : '',
        'STSToken': None,
        'Timeout' : None
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        if Key is None and Url is None:
            raise Exception('Either Key or Url Must be Given')

        Options = _ValidateAndInitEndPoint(
            Options,
            RequireCheck = Url is None,
            EndPointFunc = __EndPoint
        )
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if Url is None:
            if Path and os.path.dirname(Path):
                os.makedirs(os.path.dirname(Path), exist_ok = True)

            Bucket = __Bucket(
                AK       = Options.AK,
                SK       = Options.SK,
                Region   = Options.Region,
                Bucket   = Options.Bucket,
                Cname    = Options.Endpoint,
                STSToken = Options.STSToken,
                Timeout  = Options.Timeout
            )

            Response['Result'] = Bucket.get_object_to_file(
                key               = Key.removeprefix('/'),
                filename          = Path,
                headers           = Header,
                params            = Param,
                progress_callback = ProgressCallback
            ) if Path else Bucket.get_object(
                key               = Key.removeprefix('/'),
                headers           = Header,
                params            = Param,
                progress_callback = ProgressCallback
            )
        else:
            if Path and os.path.dirname(Path):
                os.makedirs(os.path.dirname(Path), exist_ok = True)

            Bucket = Bucket(
                auth        = AnonymousAuth(),
                endpoint    = 'oss.aliyuncs.com',
                bucket_name = 'oss-aliyuncs-com'
            )

            Response['Result'] = Bucket.get_object_with_url_to_file(
                sign_url          = Url,
                filename          = Path,
                headers           = Header,
                progress_callback = ProgressCallback
            ) if Path else Bucket.get_object_with_url(
                sign_url          = Url,
                headers           = Header,
                progress_callback = ProgressCallback
            )
    except NotFound  as Error:
        Response['Ec'] = 40400; Response['Em'] = MakeErrorMessage(Error); return Response
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def MultiPartGetObject(Key: str, Path: str, Header: dict = None, Param: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Resumable Get Object from OSS Bucket (Multipart Download).
    '''
    import os

    from oss2 import resumable_download

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  Aliyun import __EndPoint
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .Aliyun import __EndPoint

    DftOpts = {
        'Region'  : '',
        'Bucket'  : '',
        'Endpoint': None,
        'AK'      : '',
        'SK'      : '',
        'STSToken': None,
        'Timeout' : None,

        'Resumable.Thread': 5,
        'Resumable.BlockSize': 10 * 1024 * 1024
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        Options = _ValidateAndInitEndPoint(
            Options,
            EndPointFunc = __EndPoint
        )
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if Path and os.path.dirname(Path):
            os.makedirs(os.path.dirname(Path), exist_ok = True)

        Bucket = __Bucket(
            AK       = Options.AK,
            SK       = Options.SK,
            Region   = Options.Region,
            Bucket   = Options.Bucket,
            Cname    = Options.Endpoint,
            STSToken = Options.STSToken,
            Timeout  = Options.Timeout
        )

        Response['Result'] = resumable_download(
            bucket             = Bucket,
            key                = Key.removeprefix('/'),
            filename           = Path,
            multiget_threshold = Options['Resumable.BlockSize'],
            part_size          = Options['Resumable.BlockSize'],
            progress_callback  = ProgressCallback,
            num_threads        = Options['Resumable.Thread'],
            params             = Param,
            headers            = Header
        )
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def PutObject(Key: str = None, Url: str = None, Path: str = None, Data: str = None, Header: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Put Object to OSS Bucket.
    '''
    from oss2 import Bucket
    from oss2 import AnonymousAuth

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  Aliyun import __EndPoint
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .Aliyun import __EndPoint

    DftOpts = {
        'Region'  : '',
        'Bucket'  : '',
        'Endpoint': None,
        'AK'      : '',
        'SK'      : '',
        'STSToken': None,
        'Timeout' : None
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        if Key is None and Url is None:
            raise Exception('Either Key or Url Must be Given')

        if Path is None and Data is None:
            raise Exception('Either Path or Data Must be Given')

        Options = _ValidateAndInitEndPoint(
            Options,
            RequireCheck = Url is None,
            EndPointFunc = __EndPoint
        )
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if Url is None:
            Bucket = __Bucket(
                AK       = Options.AK,
                SK       = Options.SK,
                Region   = Options.Region,
                Bucket   = Options.Bucket,
                Cname    = Options.Endpoint,
                STSToken = Options.STSToken,
                Timeout  = Options.Timeout
            )

            Response['Result'] = Bucket.put_object(
                key               = Key.removeprefix('/'),
                data              = Data,
                headers           = Header,
                progress_callback = ProgressCallback
            ) if Data is not None else Bucket.put_object_from_file(
                key               = Key.removeprefix('/'),
                filename          = Path,
                headers           = Header,
                progress_callback = ProgressCallback
            )
        else:
            Bucket = Bucket(
                auth            = AnonymousAuth(),
                endpoint        = 'oss.aliyuncs.com',
                bucket_name     = 'oss-aliyuncs-com',
                connect_timeout = Options.Timeout
            )

            Response['Result'] = Bucket.put_object_with_url(
                sign_url          = Url,
                data              = Data,
                headers           = Header,
                progress_callback = ProgressCallback
            ) if Data is not None else Bucket.put_object_with_url_from_file(
                sign_url          = Url,
                filename          = Path,
                headers           = Header,
                progress_callback = ProgressCallback
            )
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def FormPutObject(Key: str, Path: str, Header: dict = None, MultipartField: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Form Put Object to OSS Bucket. \n
    Hint! Only Support to use Signed Policy and Generate Signature is NOT Available.
    '''
    import requests

    from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  Aliyun import __EndPoint
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .Aliyun import __EndPoint

    DftOpts = {
        'Region'  : '',
        'Bucket'  : '',
        'Endpoint': None,
        'Timeout' : None,

        'Validate.RequireCheck'     : None,
        'Validate.RequireField'     : ['Region', 'Bucket'],
        'Validate.EndPointFunc'     : __EndPoint,
        'Validate.EndPointProduct'  : 'Oss',
        'Validate.EndPointBucketKey': 'Oss.Bucket'
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        if Options['Validate.RequireCheck'] is None:
            Options['Validate.RequireCheck'] = Options.Endpoint is None

        Options = _ValidateAndInitEndPoint(
            Options,
            **{ Key.removeprefix('Validate.'): Value for Key, Value in Options.items() if Key.startswith('Validate.') and Value is not None }
        )

        Header  = requests.structures.CaseInsensitiveDict(Header or {})
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error); return Response

    def _Callback(Monitor):
        if ProgressCallback: ProgressCallback(Monitor.bytes_read, Monitor.len)

    try:
        with open(Path, 'rb') as File:
            Fields  = dict(MultipartField or {})
            Fields.setdefault('key' , Key.removeprefix('/'))
            Fields.setdefault('file', (Path, File, _FormatContentType(Path = Path, Value = Header.get('Content-Type'))))

            Encoder = MultipartEncoder(fields = { Key: Value for Key, Value in Fields.items() if Value is not None })
            Monitor = MultipartEncoderMonitor(Encoder, _Callback); Header['Content-Type'] = Monitor.content_type
            Results = requests.post(url = 'https://%s/' % Options.Endpoint.removesuffix('/'), data = Monitor, headers = Header, timeout = Options.Timeout)

        if not Results.ok:
            raise requests.exceptions.HTTPError(Results.text)
        else:        
            Response['Result'] = Results
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def MultiPartPutObject(Key: str, Path: str, Header: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Resumable Put Object to OSS Bucket. (Multipart Upload)
    '''
    from oss2 import resumable_upload

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  Aliyun import __EndPoint
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .Aliyun import __EndPoint

    DftOpts = {
        'Region'  : '',
        'Bucket'  : '',
        'Endpoint': None,
        'AK'      : '',
        'SK'      : '',
        'STSToken': None,
        'Timeout' : None,

        'Resumable.Thread': 5,
        'Resumable.BlockSize': 10 * 1024 * 1024
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        Options = _ValidateAndInitEndPoint(
            Options,
            EndPointFunc = __EndPoint
        )
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Bucket = __Bucket(
            AK       = Options.AK,
            SK       = Options.SK,
            Region   = Options.Region,
            Bucket   = Options.Bucket,
            Cname    = Options.Endpoint,
            STSToken = Options.STSToken,
            Timeout  = Options.Timeout
        )

        Response['Result'] = resumable_upload(
            bucket              = Bucket,
            key                 = Key.removeprefix('/'),
            filename            = Path,
            headers             = Header,
            multipart_threshold = Options['Resumable.BlockSize'],
            part_size           = Options['Resumable.BlockSize'],
            num_threads         = Options['Resumable.Thread'],
            progress_callback   = ProgressCallback
        )
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def AppendObject(Key: str, Path: str = None, Data: str = None, Header: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Append Object to OSS Bucket. The Object Must be Appendable and The New Data will be Appended to the End of the Object.
    '''
    from oss2.exceptions import NotFound

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  Aliyun import __EndPoint
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .Aliyun import __EndPoint

    DftOpts = {
        'Region'  : '',
        'Bucket'  : '',
        'Endpoint': None,
        'AK'      : '',
        'SK'      : '',
        'STSToken': None,
        'Timeout' : None
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        if Path is None and Data is None:
            raise Exception('Either Path or Data Must be Given')

        Options = _ValidateAndInitEndPoint(
            Options,
            EndPointFunc = __EndPoint
        )
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Bucket = __Bucket(
            AK       = Options.AK,
            SK       = Options.SK,
            Region   = Options.Region,
            Bucket   = Options.Bucket,
            Cname    = Options.Endpoint,
            STSToken = Options.STSToken,
            Timeout  = Options.Timeout
        )

        try:
            Position = Bucket.head_object(
                key     = Key.removeprefix('/'),
                headers = Header
            ).content_length
        except NotFound:
            Position = 0

        if Data is None:
            with open(Path, 'rb') as File: Data = File.read()

        Response['Result'] = Bucket.append_object(
            key               = Key.removeprefix('/'),
            position          = Position,
            data              = Data,
            headers           = Header,
            progress_callback = ProgressCallback
        )
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def DeleteObject(Key: str | list, Header: dict = None, Param: dict = None, Options: dict = None) -> dict:
    '''
    Delete Object from OSS Bucket.
    '''
    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  Aliyun import __EndPoint
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .Aliyun import __EndPoint

    DftOpts = {
        'Region'  : '',
        'Bucket'  : '',
        'Endpoint': None,
        'AK'      : '',
        'SK'      : '',
        'STSToken': None,
        'Timeout' : None
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        Options = _ValidateAndInitEndPoint(
            Options,
            EndPointFunc = __EndPoint
        )
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Bucket = __Bucket(
            AK       = Options.AK,
            SK       = Options.SK,
            Region   = Options.Region,
            Bucket   = Options.Bucket,
            Cname    = Options.Endpoint,
            STSToken = Options.STSToken,
            Timeout  = Options.Timeout
        )

        if isinstance(Key, str):
            Response['Result'] = Bucket.delete_object(
                key      = Key.removeprefix('/'),
                headers  = Header,
                params   = Param
            )
        else:
            Response['Result'] = Bucket.batch_delete_objects(
                key_list = [_Key.removeprefix('/') for _Key in Key],
                headers  = Header
            )
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response
