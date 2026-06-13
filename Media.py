IMAGE_EXTENSIONS = {
    '.BLP', '.BMP', '.DDS', '.DIB', '.EPS', '.GIF', '.ICO', '.IM', '.JPG', '.JPEG', '.JFIF', '.J2K', '.J2P', '.JPX',
    '.MSP', '.PCX', '.PNG', '.APNG', '.PPM', '.SPIDER', '.TGA', '.TIFF', '.TIF', '.WEBP', '.XBM', '.CUR', '.DCX',
    '.FITS', '.FLI', '.FLC', '.FPX', '.FTEX', '.GBR', '.GD', '.IMT', '.IPTC', '.NAA', '.MCIDAS', '.MIC', '.MPO',
    '.PCD', '.PIXAR', '.PSD', '.SUN', '.WAL', '.EMF', '.XPM', '.HEIC', '.HEIF', '.AVIF'
}

VIDEO_EXTENSIONS = {
    '.3G2', '.3GP', '.ASF', '.ASX', '.AVI', '.DIVX', '.FLV', '.M2TS', '.M2V', '.M4V', '.MKV', '.MOV', '.MP4',
    '.MPEG', '.MPG', '.MTS', '.MXF', '.OGV', '.RM', '.SWF', '.WEBM', '.WMV'
}


class SuppressStderr:
    def __enter__(self):
        import os
        import sys

        self._Stderr = sys.stderr
        self._Fd = None
        self._DevNull = None

        try:
            self._Fd = os.dup(2)
            self._DevNull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(self._DevNull, 2)
        except: self.__exit__(None, None, None)

        return self

    def __exit__(self, ExcType, ExcValue, Traceback):
        import os
        import sys

        try: os.dup2(self._Fd, 2)
        except: pass

        try: os.close(self._Fd)
        except: pass

        try: os.close(self._DevNull)
        except: pass

        try: sys.stderr = self._Stderr
        except: pass

        return False


def __GuessMediaType(Path: str, ContentType: str = '') -> str:
    import os
    import urllib.parse

    ContentType = (ContentType or '').split(';', 1)[0].strip().lower()

    if ContentType.startswith('image/'): return 'Image'
    if ContentType.startswith('video/'): return 'Video'

    Parsed = urllib.parse.urlparse(Path)
    Extension = os.path.splitext(Parsed.path or Path)[-1].upper()
    if Extension in IMAGE_EXTENSIONS: return 'Image'
    if Extension in VIDEO_EXTENSIONS: return 'Video'

    return ''


def __ReadImageInfo(Path: str) -> tuple:
    import PIL.Image

    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError: pass

    with PIL.Image.open(Path) as Image: return int(Image.height), int(Image.width)


def __ReadOnlineImageInfo(Path: str, Options: dict = None) -> tuple:
    import requests
    import PIL.ImageFile

    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError: pass

    MaxProbeBytes = int(Options.get('Online.ProbeSize', 1024 * 1024 * 8))
    Parser    = PIL.ImageFile.Parser()
    ReadBytes = 0
    Rsp       = None

    try:
        Rsp = requests.get(Path,
                           headers = Options.Header,
                           params  = Options.Params,
                           cookies = Options.Cookie,
                           timeout = Options.Timeout,
                           verify  = Options.Verify,
                           stream  = True,
                           allow_redirects = Options.AllowRedirects)

        if not 200 <= Rsp.status_code < 300:
            raise Exception(f'HTTP Code is {Rsp.status_code}')

        for Chunk in Rsp.iter_content(chunk_size = 1024 * 32):
            if not Chunk:
                continue

            ReadBytes += len(Chunk)
            if MaxProbeBytes > 0 and ReadBytes > MaxProbeBytes:
                raise Exception('Couldn\'t Read Image Size Within %s Bytes' % MaxProbeBytes)

            Parser.feed(Chunk)
            if Parser.image:
                Width, Height = Parser.image.size
                return int(Height), int(Width)

        Image = Parser.close(); Width, Height = Image.size
        return int(Height), int(Width)
    finally:
        try: Rsp.close()
        except: pass


def __ReadVideoInfo_FFProbe(Path: str, Options: dict = None) -> tuple:
    import json
    import subprocess
    import urllib.parse

    Command = [
        'ffprobe', '-v', 'error',
    ]

    if Options:
        Timeout = Options.get('Timeout', 10)
        ProbeSize = Options.get('FFProbe.ProbeSize', 1024 * 1024 * 5)
        AnalyzeDuration = Options.get('FFProbe.AnalyzeDuration', 5000000)
        Headers = dict(Options.Header or {})
        Cookies = Options.Cookie or {}
        UserAgent = (Options.Header or {}).get('User-Agent', '')

        if Cookies and not any(Key.lower() == 'cookie' for Key in Headers):
            Headers['Cookie'] = '; '.join('%s=%s' % (Key, Value) for Key, Value in Cookies.items())

        if Timeout:
            Command.extend(['-rw_timeout', str(int(float(Timeout) * 1000000))])
        if ProbeSize:
            Command.extend(['-probesize', str(int(ProbeSize))])
        if AnalyzeDuration:
            Command.extend(['-analyzeduration', str(int(AnalyzeDuration))])
        if UserAgent:
            Command.extend(['-user_agent', UserAgent])
        if Headers:
            Command.extend(['-headers', ''.join('%s: %s\r\n' % (Key, Value) for Key, Value in Headers.items() if Value is not None)])

        if Options.Params:
            Path = Path + (('&' if '?' in Path else '?') + urllib.parse.urlencode(Options.Params))

    Command.extend([
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'json',
        Path
    ])

    Timeout = (Options or {}).get('Timeout', 10)
    Result = subprocess.run(Command, capture_output = True, text = True, timeout = int(float(Timeout or 10)) + 5)

    if Result.returncode != 0:
        raise Exception((Result.stderr or Result.stdout or 'ffprobe Failed').strip())

    Info = json.loads(Result.stdout or '{}')
    Stream = (Info.get('streams') or [{}])[0]
    Width  = int(Stream.get('width')  or 0)
    Height = int(Stream.get('height') or 0)

    if Width <= 0 or Height <= 0:
        raise Exception('Couldn\'t Read Video Stream Size from File %s' % Path)

    return Height, Width


def __ReadVideoInfo_CV2(Path: str) -> tuple:
    import cv2

    Mda = None
    try:
        with SuppressStderr():
            Mda = cv2.VideoCapture(Path)
            if not Mda.isOpened(): raise Exception('Couldn\'t Read Video Stream from File %s' % Path)

            Height = int(Mda.get(cv2.CAP_PROP_FRAME_HEIGHT))
            Width  = int(Mda.get(cv2.CAP_PROP_FRAME_WIDTH))
        if Width <= 0 or Height <= 0:
            raise Exception('Couldn\'t Read Video Stream Size from File %s' % Path)

        return Height, Width
    finally:
        with SuppressStderr():
            try: Mda.release()
            except: pass


def __ReadUnknownOnlineInfo(Path: str, Options: dict = None, Size: int = -1, MediaType: str = '') -> tuple:
    import urllib.parse

    if MediaType == 'Video':
        Readers = ['Video', 'Image']
    elif MediaType == 'Image':
        Readers = ['Image', 'Video']
    elif Size != -1 and Size > Options.get('Online.ProbeSize', 1024 * 1024 * 8):
        Readers = ['Video', 'Image']
    else:
        Readers = ['Image', 'Video']

    Errors = []
    for Reader in Readers:
        try:
            if Reader == 'Image':
                return __ReadOnlineImageInfo(Path, Options)

            FFProbeError = None
            try:
                return __ReadVideoInfo_FFProbe(Path, Options)
            except Exception as Error:
                FFProbeError = Error

            if Options.get('Online.Fallback', True):
                try:
                    VideoPath = Path + (('&' if '?' in Path else '?') + urllib.parse.urlencode(Options.Params)) if Options.Params else Path
                    return __ReadVideoInfo_CV2(VideoPath)
                except Exception as Error:
                    raise Exception('FFProbe Error: %s; CV2 Error: %s' % (FFProbeError, Error))

            raise FFProbeError
        except Exception as Error:
            Errors.append('%s: %s' % (Reader, Error))

    raise Exception('Couldn\'t Read Media Info from Url %s. %s' % (Path, '; '.join(Errors)))


def GetInfo(Path: str, Options: dict = None) -> dict:
    '''
    Get Information of a Media File, Including Height, Width, Size, etc.
    '''
    return __GetOnline(Path, Options) if (Path.startswith('http://') or Path.startswith('https://')) \
      else __GetLocal(Path, Options)


def __GetLocal(Path: str, Options: dict = None) -> dict:
    '''
    GetInfo's Internal Function. Get Information of a Local Media File.
    '''
    import os

    if not __package__:
          from  Init import DotAccessDict; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict; from .Log import MakeErrorMessage

    Response = DotAccessDict({
        'Ec': 0, 'Em': '',
        'Height': -1, 'Width' : -1, 'Size'  : -1
    })

    try:
        Response['Size'] = os.path.getsize(Path)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        MediaType = __GuessMediaType(Path)

        if MediaType == 'Image':
            try:
                Response['Height'], Response['Width'] = __ReadImageInfo(Path)
            except Exception:
                try:
                    Response['Height'], Response['Width'] = __ReadVideoInfo_FFProbe(Path)
                except Exception:
                    Response['Height'], Response['Width'] = __ReadVideoInfo_CV2(Path)
        elif MediaType == 'Video':
            try:
                try:
                    Response['Height'], Response['Width'] = __ReadVideoInfo_FFProbe(Path)
                except Exception:
                    Response['Height'], Response['Width'] = __ReadVideoInfo_CV2(Path)
            except Exception:
                Response['Height'], Response['Width'] = __ReadImageInfo(Path)
        else:
            ImageError = None

            try:
                Response['Height'], Response['Width'] = __ReadImageInfo(Path)
            except Exception as Error:
                ImageError = Error

            if ImageError:
                try:
                    try:
                        Response['Height'], Response['Width'] = __ReadVideoInfo_FFProbe(Path)
                    except Exception:
                        Response['Height'], Response['Width'] = __ReadVideoInfo_CV2(Path)
                except Exception as Error:
                    raise Exception('Couldn\'t Read Media Info from File %s. Image Error: %s; Video Error: %s' % (Path, ImageError, Error))
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def __GetOnline(Path: str, Options: dict = None) -> dict:
    '''
    GetInfo's Internal Function. Get Information of an Online Media File.
    '''
    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  Download import HeadUrl
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .Download import HeadUrl

    DftOpts = {
        'Header' : {
            'Accept'    : '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        },
        'Params' : {},
        'Cookie' : {},
        'Timeout': 10,
        'Verify' : True,
        'AllowRedirects': True,

        'Online.ProbeSize' : 1024 * 1024 * 8,
        'Online.Fallback'  : True,
        'FFProbe.ProbeSize': 1024 * 1024 * 5,
        'FFProbe.AnalyzeDuration': 5000000
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '',
        'Height': -1, 'Width' : -1, 'Size'  : -1
    })

    try:
        Head = HeadUrl(Path, Options)

        if Head['Ec'] != 0: raise Exception(Head['Em'])

        if 200 <= Head['Code'] < 400 and (Head['Content-Length'] > 1024 or Head['Content-Length'] == -1):
            Response['Size'] = Head['Content-Length']
        else:
            raise Exception(f'HTTP Code is {Head["Code"]}, Content-Length is {Head["Content-Length"]}')
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        MediaType = __GuessMediaType(Head['Location'] or Path, Head['Content-Type'])
        Response['Height'], Response['Width'] = __ReadUnknownOnlineInfo(Path, Options, Response['Size'], MediaType)
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def MakeThumbnail(Path: str, Options: dict = None) -> dict:
    '''
    Generate a Thumbnail for a Media File.
    '''
    import os

    if not __package__:
          from  Init import DotAccessDict; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict; from .Log import MakeErrorMessage

    Response = DotAccessDict({
        'Ec': 0, 'Em': '',
        'Path': '',
        'Size': -1
    })

    try:
        if os.path.splitext(Path)[-1].upper() in IMAGE_EXTENSIONS:
            return __MakeThumbnail_PIL(Path, Options)
        
        if os.path.splitext(Path)[-1].upper() in VIDEO_EXTENSIONS:
            return __MakeThumbnail_CV2(Path, Options)
        
        if os.path.splitext(Path)[-1].upper() in ['.PDF']:
            return __MakeThumbnail_FITZ(Path, Options)

        raise TypeError('Unsupported File Type of %s' % os.path.splitext(Path)[-1].upper())
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def __MakeThumbnail_PIL(Path: str, Options: dict = None) -> dict:
    '''
    MakeThumbnail's Internal Function. Generate a Thumbnail for a PIL Supported Media File.
    '''
    import os
    import PIL.Image
    import pillow_heif

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  UUID import TimeUUID
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .UUID import TimeUUID

    DftOpts = {
        'Path'     : '%s-%s.jpg' % (Path, TimeUUID()),
        'Size'     : (400, 300),
        'Quality'  : 25,
        'RemoveOrg': False
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '',
        'Path': '',
        'Size': -1
    })

    try:
        if os.path.dirname(Options.Path):
            os.makedirs(os.path.dirname(Options.Path), exist_ok = True)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        pillow_heif.register_heif_opener()

        with PIL.Image.open(Path) as SourceImage:
            Image = SourceImage.convert('RGB')

            if Options.Size[0] <= 0 or Options.Size[1] <= 0:
                if Options.Size[1] <= 0:                              # 按宽度等比例缩放
                    Ratio_Resize = float(Options.Size[0]) / float(Image.width)
                    Options.Size = (Options.Size[0], int(Image.height * Ratio_Resize))
                else:                                                 # 按高度等比例缩放
                    Ratio_Resize = float(Options.Size[1]) / float(Image.height)
                    Options.Size = (int(Image.width * Ratio_Resize), Options.Size[1])

                Image = Image.resize(Options.Size, PIL.Image.LANCZOS)

            else:
                Ratio_Orig = float(Image.width) / float(Image.height)
                Ratio_Crop = float(Options.Size[0]) / float(Options.Size[1])

                if Ratio_Orig > Ratio_Crop:
                    _      = int(Image.height * Ratio_Crop)
                    Margin = (Image.width - _) // 2
                    Image  = Image.crop((Margin, 0, Margin + _, Image.height))
                else: 
                    _      = int(Image.width / Ratio_Crop)
                    Margin = (Image.height - _) // 2
                    Image  = Image.crop((0, Margin, Image.width, Margin + _))

                Image.thumbnail((min(Options.Size[0], Image.width), min(Options.Size[1], Image.height)))

            Image.save(Options.Path, quality = Options.Quality, format = 'JPEG')
        Response['Path'] = Options.Path
        Response['Size'] = os.path.getsize(Options.Path)
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if Options.RemoveOrg:
            os.remove(Path)
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def __MakeThumbnail_CV2(Path: str, Options: dict = None) -> dict:
    '''
    MakeThumbnail's Internal Function. Generate a Thumbnail for a CV2 Supported Media File.
    '''
    import os
    import cv2

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  UUID import TimeUUID
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .UUID import TimeUUID

    DftOpts = {
        'Path'     : '%s-%s.jpg' % (Path, TimeUUID()),
        'Size'     : (400, 300),
        'Quality'  : 25,
        'RemoveOrg': False
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '',
        'Path': '',
        'Size': -1
    })

    try:
        if os.path.dirname(Options.Path):
            os.makedirs(os.path.dirname(Options.Path), exist_ok = True)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        with SuppressStderr():
            Mda = cv2.VideoCapture(Path)
            if not Mda.isOpened(): raise Exception('Couldn\'t Read Video Stream from File %s' % Path)

            Pos = int(min(Mda.get(cv2.CAP_PROP_FRAME_COUNT) / (Mda.get(cv2.CAP_PROP_FPS) or 1) * 1000, 0.05 * 1000))
            Mda.set(cv2.CAP_PROP_POS_MSEC, Pos)

            Success, Frame = Mda.read()
        if not Success or Frame is None:
            raise Exception('Couldn\'t Read Video Frame from File %s' % Path)

        cv2.imwrite(Options.Path, Frame)
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response
    finally:
        with SuppressStderr():
            try: Mda.release()
            except: pass

    try:
        if Options.RemoveOrg:
            os.remove(Path)
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response

    return __MakeThumbnail_PIL(Options.Path, Options = {
                                                    'Path'     : '%s-%s.jpg' % (Path, TimeUUID()),
                                                    'Size'     : Options.Size,
                                                    'Quality'  : Options.Quality,
                                                    'RemoveOrg': True
                                                })


def __MakeThumbnail_FITZ(Path: str, Options: dict = None) -> dict:
    '''
    MakeThumbnail's Internal Function. Generate a Thumbnail for a PyMuPDF Supported Media File.
    '''
    import os
    import fitz
    import PIL.Image

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage; from  UUID import TimeUUID
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage; from .UUID import TimeUUID

    DftOpts = {
        'Path'     : '%s-%s.jpg' % (Path, TimeUUID()),
        'Size'     : (400, 300),
        'Quality'  : 25,
        'RemoveOrg': False
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '',
        'Path': '',
        'Size': -1
    })

    try:
        if os.path.dirname(Options.Path):
            os.makedirs(os.path.dirname(Options.Path), exist_ok = True)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    Pdf = None
    try:
        Pdf = fitz.open(Path)
        Img = Pdf[0].get_pixmap()
        Img = PIL.Image.frombytes('RGB', [Img.width, Img.height], Img.samples)
        Img.save(Options.Path, format = 'JPEG')
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response
    finally:
        try: Pdf.close()
        except: pass

    try:
        if Options.RemoveOrg:
            os.remove(Path)
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response

    return __MakeThumbnail_PIL(Options.Path, Options = {
                                                    'Path'     : '%s-%s.jpg' % (Path, TimeUUID()),
                                                    'Size'     : Options.Size,
                                                    'Quality'  : Options.Quality,
                                                    'RemoveOrg': True
                                                })
