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
            raise Exception('Either Key or Url Must be Given')

        if Path is None and Data is None:
            raise Exception('Either Path or Data Must be Given')

        Options = _ValidateAndInitEndPoint(
            Options,
            RequireCheck      = Url is None,
            EndPointFunc      = __EndPoint,
            EndPointProduct   = 'Tos',
            EndPointBucketKey = 'Tos.Bucket'
        )

        Header  = requests.structures.CaseInsensitiveDict(Header or {})
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
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

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
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

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
