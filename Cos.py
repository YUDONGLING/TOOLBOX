def __EndPoint(Product: str = None, Region: str = None, Options: dict = None) -> str:
    '''
    Tencent Cloud OpenAPI EndPoint.
    '''
    try:    Product = Product.title()
    except: raise Exception('Invalid Product')

    try:    Region  = (Region or 'AP-SHANGHAI').lower()
    except: raise Exception('Invalid Region')

    if not Options or not isinstance(Options, dict): Options = {}

    if Product == 'Cos':
        EndPoint = 'cos.{Region}.myqcloud.com'.format(Region = Region)
        return '{Bucket}.{EndPoint}'.format(Bucket = Options.get('Cos.Bucket'), EndPoint = EndPoint) if Options.get('Cos.Bucket') else EndPoint

    raise Exception('Invalid Product')


def __Service(AK: str, SK: str, Region: str, STSToken: str = None, Timeout: int = None) -> object:
    '''
    Initiate a COS Service Object.
    '''
    from qcloud_cos import CosConfig, CosS3Client

    Config = CosConfig(
        Region    = Region,
        SecretId  = AK,
        SecretKey = SK,
        Token     = STSToken,
        Scheme    = 'https',
        Timeout   = Timeout,
        Endpoint  = __EndPoint('Cos', Region)
    )
    return CosS3Client(Config)


def __Bucket(AK: str, SK: str, Region: str, Bucket: str, Cname: str = None, STSToken: str = None, Timeout: int = None) -> object:
    '''
    Initiate a COS Bucket Object.
    '''
    from qcloud_cos import CosConfig, CosS3Client

    Config = CosConfig(
        Region    = Region,
        SecretId  = AK,
        SecretKey = SK,
        Token     = STSToken,
        Scheme    = 'https',
        Timeout   = Timeout,
        Domain    = Cname
    )
    return CosS3Client(Config)


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
    Get Object from COS Bucket.
    '''
    raise NotImplementedError()


def MultiPartGetObject(Key: str, Path: str, Header: dict = None, Param: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Resumable Get Object from COS Bucket (Multipart Download).
    '''
    raise NotImplementedError()


def PutObject(Key: str = None, Url: str = None, Path: str = None, Data: str = None, Header: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Put Object to COS Bucket.
    '''
    import io
    import os
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
            EndPointProduct   = 'Cos',
            EndPointBucketKey = 'Cos.Bucket'
        )

        Header  = requests.structures.CaseInsensitiveDict(Header or {})
    except Exception as Error:
        Response['Ec'] = 40000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    class _Reader(object):
        def __init__(self, File, Total):
            self.File  = File
            self.Total = Total
            self.Consumed = 0

        def read(self, Size = -1):
            Chunk = self.File.read(Size)
            if Chunk and ProgressCallback:
                self.Consumed += len(Chunk)
                try: ProgressCallback(self.Consumed, self.Total)
                except Exception as Error: pass
            return Chunk

        def __getattr__(self, Name):
            return getattr(self.File, Name)

    def _WrapPayload(Payload: object) -> object:
        if hasattr(Payload, 'read'):
            try:
                Current = Payload.tell()
                Payload.seek(0, os.SEEK_END)
                Total = Payload.tell() - Current
                Payload.seek(Current)
            except Exception:
                Total = None
            return _Reader(Payload, Total)

        if isinstance(Payload, str):
            Payload = Payload.encode('utf-8')

        if isinstance(Payload, bytearray):
            Payload = bytes(Payload)

        if isinstance(Payload, bytes):
            return _Reader(io.BytesIO(Payload), len(Payload))

        return Payload

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

            Kwargs = {
                'CacheControl'        : Header.get('Cache-Control'),
                'ContentType'         : Header.get('Content-Type'),
                'ContentDisposition'  : Header.get('Content-Disposition'),
                'ContentEncoding'     : Header.get('Content-Encoding'),
                'ContentLanguage'     : Header.get('Content-Language'),
                'ContentLength'       : Header.get('Content-Length'),
                'ContentMD5'          : Header.get('Content-MD5'),
                'ServerSideEncryption': Header.get('X-Cos-Server-Side-Encryption')
            }

            if Data is not None:
                Response['Result'] = requests.structures.CaseInsensitiveDict(Bucket.put_object(
                    Bucket = Options.Bucket,
                    Key    = Key.removeprefix('/'),
                    Body   = _WrapPayload(Data),
                    **Kwargs
                ))
            else:
                with open(Path, 'rb') as File:
                    Response['Result'] = requests.structures.CaseInsensitiveDict(Bucket.put_object(
                        Bucket = Options.Bucket,
                        Key    = Key.removeprefix('/'),
                        Body   = _Reader(File, os.path.getsize(Path)),
                        **Kwargs
                    ))
        else:
            Result = _PutObject(
                Key = Key, Url = Url, Path = Path, Data = Data, Header = Header, ProgressCallback = ProgressCallback, Options = Options
            )

            if Result['Ec'] != 0:
                raise Exception(Result['Em'])

            Response['Result'] = _ExtractResponse(Result['Result']).headers
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Response


def FormPutObject(Key: str, Path: str, Header: dict = None, MultipartField: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Form Put Object to COS Bucket. \n
    Hint! Only Support to use Signed Policy and Generate Signature is NOT Available.
    '''
    if not __package__:
          from  Oss import FormPutObject as _FormPutObject
    else: from .Oss import FormPutObject as _FormPutObject

    Options = dict(Options or {})
    Options.setdefault('Validate.EndPointFunc'     , __EndPoint)
    Options.setdefault('Validate.EndPointProduct'  , 'Cos')
    Options.setdefault('Validate.EndPointBucketKey', 'Cos.Bucket')

    return _FormPutObject(
        Key = Key, Path = Path, Header = Header, MultipartField = MultipartField, ProgressCallback = ProgressCallback, Options = Options
    )


def MultiPartPutObject(Key: str, Path: str, Header: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Resumable Put Object to COS Bucket. (Multipart Upload)
    '''
    import math
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
            EndPointProduct   = 'Cos',
            EndPointBucketKey = 'Cos.Bucket'
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

        Response['Result'] = requests.structures.CaseInsensitiveDict(Bucket.upload_file(
            Bucket               = Options.Bucket,
            Key                  = Key.removeprefix('/'),
            LocalFilePath        = Path,
            PartSize             = max(1, int(math.ceil(Options['Resumable.BlockSize'] / 1024 / 1024))),
            MAXThread            = Options['Resumable.Thread'],
            CacheControl         = Header.get('Cache-Control'),
            ContentType          = Header.get('Content-Type'),
            ContentDisposition   = Header.get('Content-Disposition'),
            ContentEncoding      = Header.get('Content-Encoding'),
            ContentLanguage      = Header.get('Content-Language'),
            ContentLength        = Header.get('Content-Length'),
            ContentMD5           = Header.get('Content-MD5'),
            ServerSideEncryption = Header.get('X-Cos-Server-Side-Encryption'),
            progress_callback    = ProgressCallback
        ))
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error, Code = Response['Ec']); return Response

    return Response


def AppendObject(Key: str, Path: str = None, Data: str = None, Header: dict = None, ProgressCallback: callable = None, Options: dict = None) -> dict:
    '''
    Append Object to COS Bucket. The Object Must be Appendable and The New Data will be Appended to the End of the Object.
    '''
    raise NotImplementedError()


def DeleteObject(Key: str | list, Header: dict = None, Param: dict = None, Options: dict = None) -> dict:
    '''
    Delete Object from COS Bucket.
    '''
    raise NotImplementedError()
