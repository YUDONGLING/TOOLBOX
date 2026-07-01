def _AdaptCallback(ProgressCallback: callable) -> callable:
    '''
    Adapt the ProgressCallback to the DataTransferListener of TOS SDK.
    Document: https://www.volcengine.com/docs/6349/92800
    '''
    if not ProgressCallback: return None

    def Callback(Consumed: int, Total: int, RwOnceBytes: int, Type: object):
        ProgressCallback(Consumed, Total)

    return Callback


def __EndPoint(Product: str = None, Region: str = None, Options: dict = None) -> str:
    '''
    Volcengine OpenAPI EndPoint.
    '''
    try:    Product = Product.title()
    except: raise Exception('Invalid Product')

    try:    Region  = (Region or 'CN-BEIJING').lower()
    except: raise Exception('Invalid Region')

    if not Options or not isinstance(Options, dict): Options = {}

    if Product == 'Tos':
        Region = Region.removeprefix('tos-')
        EndPoint = 'tos-{Region}.volces.com'.format(Region = Region)
        return '{Bucket}.{EndPoint}'.format(Bucket = Options.get('Tos.Bucket'), EndPoint = EndPoint) if Options.get('Tos.Bucket') else EndPoint

    raise Exception('Invalid Product')


def __Service(AK: str, SK: str, Region: str, STSToken: str = None, Timeout: int = None) -> object:
    '''
    Initiate a TOS Service Object.
    '''
    from tos import TosClientV2

    Kwargs = {
        'ak'            : AK,
        'sk'            : SK,
        'endpoint'      : __EndPoint('Tos', Region),
        'region'        : Region,
        'security_token': STSToken
    }
    if Timeout is not None:
        Kwargs['connection_time'] = Timeout
        Kwargs['request_timeout'] = Timeout
        Kwargs['socket_timeout']  = Timeout

    return TosClientV2(**Kwargs)


def __Bucket(AK: str, SK: str, Region: str, Bucket: str, Cname: str = None, STSToken: str = None, Timeout: int = None) -> object:
    '''
    Initiate a TOS Bucket Object.
    '''
    from tos import TosClientV2

    Kwargs = {
        'ak'              : AK,
        'sk'              : SK,
        'endpoint'        : Cname or '',
        'region'          : Region,
        'security_token'  : STSToken,
        'is_custom_domain': True if Cname else False
    }
    if Timeout is not None:
        Kwargs['connection_time'] = Timeout
        Kwargs['request_timeout'] = Timeout
        Kwargs['socket_timeout']  = Timeout

    return TosClientV2(**Kwargs)


def __Sign(AK: str, SK: str, Region: str, Bucket: str, Method: str, Url: str, STSToken: str = None, Expires: int = None, Version: str = None) -> str:
    '''
    Sign a URL for Bucket Operation or Object Operation, and Return a Signed URL Startswith '/'.
    '''
    raise NotImplementedError()


def SignUrl(Method: str, Key: str, Header: dict = None, Param: dict = None, Expires: int = 3600, Options: dict = None) -> dict:
    '''
    Sign a URL for Bucket Operation or Object Operation, and Return a Signed URL with Host.
    '''
    raise NotImplementedError()


def GetObject(Key: str = None, Url: str = None, Path: str = None, Header: dict = None, Param: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Get Object from TOS Bucket.
    '''
    raise NotImplementedError()


def MultiPartGetObject(Key: str, Path: str, Header: dict = None, Param: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Resumable Get Object from TOS Bucket (Multipart Download).
    '''
    raise NotImplementedError()


def PutObject(Key: str = None, Url: str = None, Path: str = None, Data: str = None, Header: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Put Object to TOS Bucket.
    '''
    import tos
    import requests

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  Oss import _ValidateAndInitEndPoint, _ExtractResponse, PutObject as _PutObject
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .Oss import _ValidateAndInitEndPoint, _ExtractResponse, PutObject as _PutObject

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
            raise Exception('Missing Required Parameter: Key or Url')

        if Path is None and Data is None:
            raise Exception('Missing Required Parameter: Path or Data')

        Options = _ValidateAndInitEndPoint(
            Options,
            RequireCheck      = Url is None,
            EndPointFunc      = __EndPoint,
            EndPointProduct   = 'Tos',
            EndPointBucketKey = 'Tos.Bucket'
        )

        Header  = requests.structures.CaseInsensitiveDict(Header or {})
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

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
                bucket                 = Options.Bucket,
                key                    = Key.removeprefix('/'),
                content                = Data,
                content_length         = Header.get('Content-Length'),
                content_md5            = Header.get('Content-MD5'),
                content_sha256         = Header.get('X-Tos-Content-Sha256'),
                cache_control          = Header.get('Cache-Control'),
                content_disposition    = Header.get('Content-Disposition'),
                content_encoding       = Header.get('Content-Encoding'),
                content_language       = Header.get('Content-Language'),
                content_type           = Header.get('Content-Type'),
                acl                    = tos.convert_acl_type(Header.get('X-Tos-Acl')) if Header.get('X-Tos-Acl') else None,
                server_side_encryption = Header.get('X-Tos-Server-Side-Encryption'),
                data_transfer_listener = _AdaptCallback(ProgressCallback)
            ) if Data is not None else Bucket.put_object_from_file(
                bucket                 = Options.Bucket,
                key                    = Key.removeprefix('/'),
                file_path              = Path,
                content_length         = Header.get('Content-Length'),
                content_md5            = Header.get('Content-MD5'),
                content_sha256         = Header.get('X-Tos-Content-Sha256'),
                cache_control          = Header.get('Cache-Control'),
                content_disposition    = Header.get('Content-Disposition'),
                content_encoding       = Header.get('Content-Encoding'),
                content_language       = Header.get('Content-Language'),
                content_type           = Header.get('Content-Type'),
                acl                    = tos.convert_acl_type(Header.get('X-Tos-Acl')) if Header.get('X-Tos-Acl') else None,
                server_side_encryption = Header.get('X-Tos-Server-Side-Encryption'),
                data_transfer_listener = _AdaptCallback(ProgressCallback)
            )
        else:
            Result = _PutObject(
                Key = Key, Url = Url, Path = Path, Data = Data, Header = Header, ProgressCallback = ProgressCallback, Options = Options
            )

            if Result['Ec'] != 0:
                raise Exception(Result['Em'])

            Response['Result'] = tos.models2.PutObjectOutput(_ExtractResponse(Result['Result']))
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Response


def FormPutObject(Key: str, Path: str, Header: dict = None, MultipartField: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Form Put Object to TOS Bucket. \n
    Hint! Only Support to use Signed Policy and Generate Signature is NOT Available.
    '''
    if not __package__:
          from  Oss import FormPutObject as _FormPutObject
    else: from .Oss import FormPutObject as _FormPutObject

    Options = dict(Options or {})
    Options.setdefault('Validate.EndPointFunc'     , __EndPoint)
    Options.setdefault('Validate.EndPointProduct'  , 'Tos')
    Options.setdefault('Validate.EndPointBucketKey', 'Tos.Bucket')

    return _FormPutObject(
        Key = Key, Path = Path, Header = Header, MultipartField = MultipartField, ProgressCallback = ProgressCallback, Options = Options
    )


def MultiPartPutObject(Key: str, Path: str, Header: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Resumable Put Object to TOS Bucket. (Multipart Upload)
    '''
    import tos
    import requests

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  Oss import _ValidateAndInitEndPoint
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .Oss import _ValidateAndInitEndPoint

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
            EndPointFunc      = __EndPoint,
            EndPointProduct   = 'Tos',
            EndPointBucketKey = 'Tos.Bucket'
        )

        Header  = requests.structures.CaseInsensitiveDict(Header or {})
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

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

        Response['Result'] = Bucket.upload_file(
            bucket                 = Options.Bucket,
            key                    = Key.removeprefix('/'),
            file_path              = Path,
            cache_control          = Header.get('Cache-Control'),
            content_disposition    = Header.get('Content-Disposition'),
            content_encoding       = Header.get('Content-Encoding'),
            content_language       = Header.get('Content-Language'),
            content_type           = Header.get('Content-Type'),
            acl                    = tos.convert_acl_type(Header.get('X-Tos-Acl')) if Header.get('X-Tos-Acl') else None,
            server_side_encryption = Header.get('X-Tos-Server-Side-Encryption'),
            part_size              = Options['Resumable.BlockSize'],
            task_num               = Options['Resumable.Thread'],
            data_transfer_listener = _AdaptCallback(ProgressCallback)
        )
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Response


def AppendObject(Key: str, Path: str = None, Data: str = None, Header: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Append Object to TOS Bucket. The Object Must be Appendable and The New Data will be Appended to the End of the Object.
    '''
    raise NotImplementedError()


def DeleteObject(Key: str | list, Header: dict = None, Param: dict = None, Options: dict = None) -> dict:
    '''
    Delete Object from TOS Bucket.
    '''
    raise NotImplementedError()


def ApplyImageUpload(Service: str, SignWith: str, Count: int = 1, Options: dict = None) -> dict:
    import os
    import sys
    import json

    from volcengine.imagex.v2.imagex_trait import service_info_map

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

    DftOpts = {
        'Region'  : '',
        'Endpoint': None,
        'AK'      : '',
        'SK'      : '',
        'STSToken': None,

        'Header'  : {
            'Accept'    : '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        },
        'Params'  : {},
        'Cookie'  : {},
        'Timeout' : None,
        'Verify'  : True,
        'AllowRedirects': True
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        if SignWith not in ('SDK', 'AWS'):
            raise ValueError('Unsupported Sign Method: %s' % (SignWith))

        if not 1 <= Count <= 10:
            raise ValueError('Invalid Count of %s, Expected in Range [1, 10]' % (Count))

        if not Service       : raise ValueError('Missing Required Parameter: Service')
        if not Options.AK    : raise ValueError('Missing Required Parameter: AK')
        if not Options.SK    : raise ValueError('Missing Required Parameter: SK')
        if not Options.Region: raise ValueError('Missing Required Parameter: Region')

        if Options.Region not in service_info_map:
            raise ValueError('Unsupported Region: %s' % (Options.Region))

        Options.Endpoint = str(Options.Endpoint or '').strip().split('//', 1)[-1].split('/', 1)[0] or \
            service_info_map[Options.Region].host.replace(
                'imagex.volcengineapi.com',
                'imagex.volcengineapi.com' if SignWith == 'SDK' else 'imagex.bytedanceapi.com')
        Options.Params   = MergeDictionaries(Options.Params or {}, {'ServiceId': Service, 'UploadNum': Count})
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    try:
        match SignWith:
            case 'SDK': Result = __ApplyImageUpload_SDK(Options)
            case 'AWS': Result = __ApplyImageUpload_AWS(Options)

        if Result.Ec:
            raise Exception(Result.Em)

        Body = Result.get('Result')
        if not isinstance(Body, dict):
            raise ValueError('Invalid ApplyUpload Result: %s' % (Body))

        Metadata = Body.get('ResponseMetadata', {})
        if Metadata.get('Error'):
            Error = Metadata['Error']
            raise ValueError('<Interface [%s]> %s' % (Error.get('Code') or Error.get('CodeN') or None, Error.get('Message') or json.dumps(Error, ensure_ascii = False) or None))

        UploadAddress = Body.get('Result', {}).get('UploadAddress', {})
        if not UploadAddress.get('StoreInfos') or not UploadAddress.get('UploadHosts'):
            raise ValueError('Invalid ApplyUpload Result, Missing UploadAddress: %s' % (Body))
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Result


def __ApplyImageUpload_SDK(Options: dict) -> dict:
    import os
    import sys

    from volcengine.imagex.v2.imagex_service import ImagexService

    if not __package__:
          from  Init import DotAccessDict; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict; from .Log import MakeErrorMessage

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        Client = ImagexService(region = Options.Region)
        Client.set_ak(Options.AK)
        Client.set_sk(Options.SK)
        Client.set_session_token(Options.STSToken or '')
        Client.set_host(Options.Endpoint)

        if Options.Timeout is not None:
            Client.set_socket_timeout(Options.Timeout)
            Client.set_connection_timeout(Options.Timeout)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    try:
        Response['Result'] = Client.apply_upload(Options.Params)
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Response


def __ApplyImageUpload_AWS(Options: dict) -> dict:
    import os
    import sys
    import requests
    import urllib.parse

    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import Credentials

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        Params = MergeDictionaries(dict(Options.Params or {}), {
            'Action'   : 'ApplyImageUpload',
            'Version'  : '2018-08-01'
        })

        QueryItems = []
        for Key in sorted(Params):
            Value = Params[Key]
            if isinstance(Value, (list, tuple)):
                QueryItems.extend((Key, _Value) for _Value in Value)
            else:
                QueryItems.append((Key, Value))

        Url    = 'https://%s/?%s' % (Options.Endpoint, urllib.parse.urlencode(QueryItems, doseq = True, quote_via = urllib.parse.quote, safe = '-_.~'))
        Header = requests.structures.CaseInsensitiveDict()
        for Key, Value in dict(Options.Header or {}).items():
            LowerKey = Key.lower()
            if LowerKey == 'host' or LowerKey == 'authorization' or LowerKey.startswith('x-amz-'):
                continue
            Header[Key] = Value
        Header['Host'] = Options.Endpoint

        Request = AWSRequest(method = 'GET', url = Url, data = b'', headers = {'Host': Options.Endpoint})
        SigV4Auth(Credentials(Options.AK, Options.SK, Options.STSToken), 'imagex', Options.Region).add_auth(Request)

        for Key, Value in Request.headers.items():
            if Key.lower() in ('authorization', 'x-amz-date', 'x-amz-security-token', 'x-amz-content-sha256'):
                Header[Key] = Value

        Result = requests.get(Url, headers = Header, cookies = Options.Cookie, timeout = Options.Timeout, verify = Options.Verify, allow_redirects = Options.AllowRedirects)
        if not Result.ok:
            raise requests.exceptions.HTTPError('<Response [%s]> %s' % (Result.status_code, Result.text or None))

        Response['Result'] = Result.json()
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Response


def CommitImageUpload(Service: str, SessionKey: str, SignWith: str, Options: dict = None) -> dict:
    import os
    import sys
    import json

    from volcengine.imagex.v2.imagex_trait import service_info_map

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

    DftOpts = {
        'Region'  : '',
        'Endpoint': None,
        'AK'      : '',
        'SK'      : '',
        'STSToken': None,

        'Header'  : {
            'Accept'      : '*/*',
            'Content-Type': 'application/json',
            'User-Agent'  : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        },
        'Params'  : {},
        'Body'    : '',
        'Cookie'  : {},
        'Timeout' : None,
        'Verify'  : True,
        'AllowRedirects': True
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        if SignWith not in ('SDK', 'AWS'):
            raise ValueError('Unsupported Sign Method: %s' % (SignWith))

        if not Service       : raise ValueError('Missing Required Parameter: Service')
        if not SessionKey    : raise ValueError('Missing Required Parameter: SessionKey')
        if not Options.AK    : raise ValueError('Missing Required Parameter: AK')
        if not Options.SK    : raise ValueError('Missing Required Parameter: SK')
        if not Options.Region: raise ValueError('Missing Required Parameter: Region')

        if Options.Region not in service_info_map:
            raise ValueError('Unsupported Region: %s' % (Options.Region))

        Options.Endpoint = str(Options.Endpoint or '').strip().split('//', 1)[-1].split('/', 1)[0] or \
            service_info_map[Options.Region].host.replace(
                'imagex.volcengineapi.com',
                'imagex.volcengineapi.com' if SignWith == 'SDK' else 'imagex.bytedanceapi.com')
        Options.Params   = MergeDictionaries(Options.Params or {}, {
            'ServiceId' : Service,
            'SessionKey': SessionKey
        })

        if Options.Body is None:
            Options.Body = ''
        elif isinstance(Options.Body, (dict, list)):
            Options.Body = json.dumps(Options.Body, ensure_ascii = False)
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    try:
        match SignWith:
            case 'SDK': Result = __CommitImageUpload_SDK(Options)
            case 'AWS': Result = __CommitImageUpload_AWS(Options)

        if Result.Ec:
            raise Exception(Result.Em)

        Body = Result.get('Result')
        if not isinstance(Body, dict):
            raise ValueError('Invalid CommitUpload Result: %s' % (Body))

        Metadata = Body.get('ResponseMetadata', {})
        if Metadata.get('Error'):
            Error = Metadata['Error']
            raise ValueError('<Interface [%s]> %s' % (Error.get('Code') or Error.get('CodeN') or None, Error.get('Message') or json.dumps(Error, ensure_ascii = False) or None))

        CommitResults = Body.get('Result', {}).get('Results', [])
        if not CommitResults:
            raise ValueError('Invalid CommitUpload Result: %s' % (Body))
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    try:
        FailedResults = [_Result for _Result in CommitResults if _Result.get('UriStatus') != 2000]
        if FailedResults:
            raise ValueError('Upload Failed: %s' % (FailedResults))
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Result


def __CommitImageUpload_SDK(Options: dict) -> dict:
    import os
    import sys

    from volcengine.imagex.v2.imagex_service import ImagexService

    if not __package__:
          from  Init import DotAccessDict; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict; from .Log import MakeErrorMessage

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        Client = ImagexService(region = Options.Region)
        Client.set_ak(Options.AK)
        Client.set_sk(Options.SK)
        Client.set_session_token(Options.STSToken or '')
        Client.set_host(Options.Endpoint)

        if Options.Timeout is not None:
            Client.set_socket_timeout(Options.Timeout)
            Client.set_connection_timeout(Options.Timeout)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    try:
        Response['Result'] = Client.commit_upload(Options.Params, Options.Body)
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Response


def __CommitImageUpload_AWS(Options: dict) -> dict:
    import os
    import sys
    import requests
    import urllib.parse

    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import Credentials

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        Params = MergeDictionaries(dict(Options.Params or {}), {
            'Action' : 'CommitImageUpload',
            'Version': '2018-08-01'
        })

        QueryItems = []
        for Key in sorted(Params):
            Value = Params[Key]
            if isinstance(Value, (list, tuple)):
                QueryItems.extend((Key, _Value) for _Value in Value)
            else:
                QueryItems.append((Key, Value))

        Url    = 'https://%s/?%s' % (Options.Endpoint, urllib.parse.urlencode(QueryItems, doseq = True, quote_via = urllib.parse.quote, safe = '-_.~'))
        Header = requests.structures.CaseInsensitiveDict()
        for Key, Value in dict(Options.Header or {}).items():
            LowerKey = Key.lower()
            if LowerKey == 'host' or LowerKey == 'authorization' or LowerKey.startswith('x-amz-'):
                continue
            Header[Key] = Value
        Header['Host'] = Options.Endpoint
        Header.setdefault('Content-Type', 'application/json')

        Request = AWSRequest(method = 'POST', url = Url, data = Options.Body or b'', headers = {'Host': Options.Endpoint})
        SigV4Auth(Credentials(Options.AK, Options.SK, Options.STSToken), 'imagex', Options.Region).add_auth(Request)

        for Key, Value in Request.headers.items():
            if Key.lower() in ('authorization', 'x-amz-date', 'x-amz-security-token', 'x-amz-content-sha256'):
                Header[Key] = Value

        Result = requests.post(Url, headers = Header, cookies = Options.Cookie, data = Options.Body, timeout = Options.Timeout, verify = Options.Verify, allow_redirects = Options.AllowRedirects)
        if not Result.ok:
            raise requests.exceptions.HTTPError('<Response [%s]> %s' % (Result.status_code, Result.text or None))

        Response['Result'] = Result.json()
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Response


def ApplyUploadInner(SpaceName: str, SignWith: str, Type: str = 'media' or 'image' or 'object', Count: int = 1, Options: dict = None) -> dict:
    import os
    import sys
    import json

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

    DftOpts = {
        'Region'  : '',
        'Endpoint': None,
        'AK'      : '',
        'SK'      : '',
        'STSToken': None,

        'Header'  : {
            'Accept'    : '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        },
        'Params'  : {},
        'Cookie'  : {},
        'Timeout' : None,
        'Verify'  : True,
        'AllowRedirects': True
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        if SignWith not in ('SDK', 'AWS'):
            raise ValueError('Unsupported Sign Method: %s' % (SignWith))

        if not Type in ('media', 'image', 'object'):
            raise ValueError('Unsupported Type: %s, Expected in (`Media`, `Image`, `Object`)' % (Type))

        MaxAllowCount = {'media' : 30, 'image' : 50, 'object': 50}[Type]
        if not 1 <= Count <= MaxAllowCount:
            raise ValueError('Invalid Count of %s, Expected in Range [1, %s]' % (Count, MaxAllowCount))

        if not SpaceName     : raise ValueError('Missing Required Parameter: Space')
        if not Options.AK    : raise ValueError('Missing Required Parameter: AK')
        if not Options.SK    : raise ValueError('Missing Required Parameter: SK')
        if not Options.Region: raise ValueError('Missing Required Parameter: Region')

        Options.Endpoint = str(Options.Endpoint or '').strip().split('//', 1)[-1].split('/', 1)[0] or ('vod.bytedanceapi.com' if SignWith == 'AWS' else 'vod.volcengineapi.com')
        Options.Params   = MergeDictionaries(Options.Params or {}, {
            'SpaceName': SpaceName,
            'FileType' : Type,
            'IsInner'  : 1,
            'UploadNum': Count
        })
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    try:
        match SignWith:
            case 'SDK': Result = __ApplyUploadInner_SDK(Options)
            case 'AWS': Result = __ApplyUploadInner_AWS(Options)

        if Result.Ec:
            raise Exception(Result.Em)

        Body = Result.get('Result')
        if not isinstance(Body, dict):
            raise ValueError('Invalid ApplyUpload Result: %s' % (Body))

        Metadata = Body.get('ResponseMetadata', {})
        if Metadata.get('Error'):
            Error = Metadata['Error']
            raise ValueError('<Interface [%s]> %s' % (Error.get('Code') or Error.get('CodeN') or None, Error.get('Message') or json.dumps(Error, ensure_ascii = False) or None))

        UploadAddress = Body.get('Result', {}).get('InnerUploadAddress', {}).get('UploadNodes', [{}])[0]
        if not UploadAddress.get('StoreInfos') or not UploadAddress.get('UploadHost') or not UploadAddress.get('SessionKey'):
            raise ValueError('Invalid ApplyUpload Result, Missing UploadAddress: %s' % (Body))
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Result


def __ApplyUploadInner_SDK(Options: dict) -> dict:
    raise NotImplementedError()


def __ApplyUploadInner_AWS(Options: dict) -> dict:
    import os
    import sys
    import requests
    import urllib.parse

    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import Credentials

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        Params = MergeDictionaries(dict(Options.Params or {}), {
            'Action'   : 'ApplyUploadInner',
            'Version'  : '2020-11-19'
        })

        QueryItems = []
        for Key in sorted(Params):
            Value = Params[Key]
            if isinstance(Value, (list, tuple)):
                QueryItems.extend((Key, _Value) for _Value in Value)
            else:
                QueryItems.append((Key, Value))

        Url    = 'https://%s/?%s' % (Options.Endpoint, urllib.parse.urlencode(QueryItems, doseq = True, quote_via = urllib.parse.quote, safe = '-_.~'))
        Header = requests.structures.CaseInsensitiveDict()
        for Key, Value in dict(Options.Header or {}).items():
            LowerKey = Key.lower()
            if LowerKey == 'host' or LowerKey == 'authorization' or LowerKey.startswith('x-amz-'):
                continue
            Header[Key] = Value
        Header['Host'] = Options.Endpoint

        Request = AWSRequest(method = 'GET', url = Url, data = b'', headers = {'Host': Options.Endpoint})
        SigV4Auth(Credentials(Options.AK, Options.SK, Options.STSToken), 'vod', Options.Region).add_auth(Request)

        for Key, Value in Request.headers.items():
            if Key.lower() in ('authorization', 'x-amz-date', 'x-amz-security-token', 'x-amz-content-sha256'):
                Header[Key] = Value

        Result = requests.get(Url, headers = Header, cookies = Options.Cookie, timeout = Options.Timeout, verify = Options.Verify, allow_redirects = Options.AllowRedirects)
        if not Result.ok:
            raise requests.exceptions.HTTPError('<Response [%s]> %s' % (Result.status_code, Result.text or None))

        Response['Result'] = Result.json()
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Response


def CommitUploadInner(SpaceName: str, SessionKey: str, SignWith: str, Options: dict = None) -> dict:
    import os
    import sys
    import json

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

    DftOpts = {
        'Region'  : '',
        'Endpoint': None,
        'AK'      : '',
        'SK'      : '',
        'STSToken': None,

        'Header'  : {
            'Accept'      : '*/*',
            'Content-Type': 'text/plain;charset=UTF-8',
            'User-Agent'  : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        },
        'Params'  : {},
        'Body'    : '',
        'Cookie'  : {},
        'Timeout' : None,
        'Verify'  : True,
        'AllowRedirects': True
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        if SignWith not in ('SDK', 'AWS'):
            raise ValueError('Unsupported Sign Method: %s' % (SignWith))

        if not SpaceName     : raise ValueError('Missing Required Parameter: Space')
        if not SessionKey    : raise ValueError('Missing Required Parameter: SessionKey')
        if not Options.AK    : raise ValueError('Missing Required Parameter: AK')
        if not Options.SK    : raise ValueError('Missing Required Parameter: SK')
        if not Options.Region: raise ValueError('Missing Required Parameter: Region')

        Options.Endpoint = str(Options.Endpoint or '').strip().split('//', 1)[-1].split('/', 1)[0] or ('vod.bytedanceapi.com' if SignWith == 'AWS' else 'vod.volcengineapi.com')
        Options.Params   = MergeDictionaries(Options.Params or {}, {
            'SpaceName' : SpaceName,
            'SessionKey': SessionKey
        })

        if Options.Body is None:
            Options.Body = ''
        elif isinstance(Options.Body, (dict, list)):
            Options.Body = json.dumps(Options.Body, ensure_ascii = False)
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    try:
        match SignWith:
            case 'SDK': Result = __CommitUploadInner_SDK(Options)
            case 'AWS': Result = __CommitUploadInner_AWS(Options)

        if Result.Ec:
            raise Exception(Result.Em)

        Body = Result.get('Result')
        if not isinstance(Body, dict):
            raise ValueError('Invalid CommitUpload Result: %s' % (Body))

        Metadata = Body.get('ResponseMetadata', {})
        if Metadata.get('Error'):
            Error = Metadata['Error']
            raise ValueError('<Interface [%s]> %s' % (Error.get('Code') or Error.get('CodeN') or None, Error.get('Message') or json.dumps(Error, ensure_ascii = False) or None))

        if not Body.get('Result', {}).get('Data'):
            raise ValueError('Invalid CommitUpload Result: %s' % (Body))
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Result


def __CommitUploadInner_SDK(Options: dict) -> dict:
    raise NotImplementedError()


def __CommitUploadInner_AWS(Options: dict) -> dict:
    import os
    import sys
    import requests
    import urllib.parse

    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import Credentials

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        Params = MergeDictionaries(dict(Options.Params or {}), {
            'Action' : 'CommitUploadInner',
            'Version': '2020-11-19'
        })

        QueryItems = []
        for Key in sorted(Params):
            Value = Params[Key]
            if isinstance(Value, (list, tuple)):
                QueryItems.extend((Key, _Value) for _Value in Value)
            else:
                QueryItems.append((Key, Value))

        Url    = 'https://%s/?%s' % (Options.Endpoint, urllib.parse.urlencode(QueryItems, doseq = True, quote_via = urllib.parse.quote, safe = '-_.~'))
        Header = requests.structures.CaseInsensitiveDict()
        for Key, Value in dict(Options.Header or {}).items():
            LowerKey = Key.lower()
            if LowerKey == 'host' or LowerKey == 'authorization' or LowerKey.startswith('x-amz-'):
                continue
            Header[Key] = Value
        Header['Host'] = Options.Endpoint
        Header.setdefault('Content-Type', 'text/plain;charset=UTF-8')

        Request = AWSRequest(method = 'POST', url = Url, data = Options.Body or b'', headers = {'Host': Options.Endpoint})
        SigV4Auth(Credentials(Options.AK, Options.SK, Options.STSToken), 'vod', Options.Region).add_auth(Request)

        for Key, Value in Request.headers.items():
            if Key.lower() in ('authorization', 'x-amz-date', 'x-amz-security-token', 'x-amz-content-sha256'):
                Header[Key] = Value

        Result = requests.post(Url, headers = Header, cookies = Options.Cookie, data = Options.Body, timeout = Options.Timeout, verify = Options.Verify, allow_redirects = Options.AllowRedirects)
        if not Result.ok:
            raise requests.exceptions.HTTPError('<Response [%s]> %s' % (Result.status_code, Result.text or None))

        Response['Result'] = Result.json()
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Response
