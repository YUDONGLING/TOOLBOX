def GetInfo(Path: str, Options: dict = None) -> dict:
    '''
    Get Information of a Media File, Including Height, Width, Size, etc.
    '''
    return __GetOnline(Path, Options) if Path.startswith('http') \
       else __GetLocal(Path, Options)


def __GetLocal(Path: str, Options: dict = None) -> dict:
    '''
    GetInfo's Internal Function. Get Information of a Local Media File.
    '''
    import os
    import cv2

    if not __package__:
          from  Log import MakeErrorMessage
    else: from .Log import MakeErrorMessage

    Response = {
        'Ec': 0, 'Em': '',
        'Height': -1,
        'Width' : -1,
        'Size'  : -1
    }

    try:
        Response['Size'] = os.path.getsize(Path)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Mda = cv2.VideoCapture(Path)
        if not Mda.isOpened(): raise Exception('Couldn\'t Read Video Stream from File %s' % Path)

        Response['Height'] = int(Mda.get(cv2.CAP_PROP_FRAME_HEIGHT))
        Response['Width']  = int(Mda.get(cv2.CAP_PROP_FRAME_WIDTH))
        Mda.release()
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def __GetOnline(Path: str, Options: dict = None) -> dict:
    '''
    GetInfo's Internal Function. Get Information of an Online Media File.
    '''
    import cv2

    if not __package__:
          from  Init import MergeDictionaries; from  Log import MakeErrorMessage; from  Download import HeadUrl
    else: from .Init import MergeDictionaries; from .Log import MakeErrorMessage; from .Download import HeadUrl

    DftOpts = {
        'Header' : {
            'Accept'    : '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        },
        'Params' : {},
        'Cookie' : {},
        'Timeout': 10,
        'Verify' : True,
        'AllowRedirects': True
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = {
        'Ec': 0, 'Em': '',
        'Height': -1,
        'Width' : -1,
        'Size'  : -1
    }

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
        Mda = cv2.VideoCapture(Path)
        if not Mda.isOpened(): raise Exception('Couldn\'t Read Video Stream from File %s' % Path)

        Response['Height'] = int(Mda.get(cv2.CAP_PROP_FRAME_HEIGHT))
        Response['Width']  = int(Mda.get(cv2.CAP_PROP_FRAME_WIDTH))
        Mda.release()
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def MakeThumbnail(Path: str, Options: dict = None) -> dict:
    '''
    Generate a Thumbnail for a Media File.
    '''
    import os

    if not __package__:
          from  Log import MakeErrorMessage
    else: from .Log import MakeErrorMessage

    Response = {
        'Ec': 0, 'Em': '',
        'Path': '',
        'Size': -1
    }

    try:
        if os.path.splitext(Path)[-1].upper() in ['.BLP', '.BMP', '.DDS', '.DIB', '.EPS', '.GIF', '.ICO', '.IM', '.JPG', '.JPEG', '.JFIF', '.J2K', '.J2P', '.JPX', '.MSP', '.PCX', '.PNG', '.APNG', '.PPM', '.SPIDER', '.TGA', '.TIFF', '.TIF', '.WEBP', '.XBM', '.CUR', '.DCX', '.FITS', '.FLI', '.FLC', '.FPX', '.FTEX', '.GBR', '.GD', '.IMT', '.IPTC', '.NAA', '.MCIDAS', '.MIC', '.MPO', '.PCD', '.PIXAR', '.PSD', '.SUN', '.WAL', '.EMF', '.XPM']:
            return __MakeThumbnail_PIL(Path, Options)
        
        if os.path.splitext(Path)[-1].upper() in ['.3G2', '.3GP', '.ASF', '.ASX', '.AVI', '.DIVX', '.FLV', '.M2TS', '.M2V', '.M4V', '.MKV', '.MOV', '.MP4', '.MPEG', '.MPG', '.MTS', '.MXF', '.OGV', '.RM', '.SWF', '.WEBM', '.WMV']:
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
          from  Init import MergeDictionaries; from  Log import MakeErrorMessage; from  UUID import TimeUUID
    else: from .Init import MergeDictionaries; from .Log import MakeErrorMessage; from .UUID import TimeUUID

    DftOpts = {
        'Path'     : '%s-%s.jpg' % (Path, TimeUUID()),
        'Size'     : (400, 300),
        'Quality'  : 25,
        'RemoveOrg': False
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = {
        'Ec': 0, 'Em': '',
        'Path': '',
        'Size': -1
    }

    try:
        if os.path.dirname(Options['Path']):
            os.makedirs(os.path.dirname(Options['Path']), exist_ok = True)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        pillow_heif.register_heif_opener()

        Image  = PIL.Image.open(Path).convert('RGB')
        Ratio1 = float(Image.width) / float(Image.height)
        Ratio2 = float(Options['Size'][0]) / float(Options['Size'][1])

        if Ratio1 > Ratio2:
            _      = int(Image.height * Ratio2)
            Margin = (Image.width - _) // 2
            Image  = Image.crop((Margin, 0, Margin + _, Image.height))
        else: 
            _      = int(Image.width / Ratio2)
            Margin = (Image.height - _) // 2
            Image  = Image.crop((0, Margin, Image.width, Margin + _))

        Image.thumbnail((min(Options['Size'][0], Image.width), min(Options['Size'][1], Image.height)))
        Image.save(Options['Path'], quality = Options['Quality'], format = 'JPEG')

        Response['Path'] = Options['Path']
        Response['Size'] = os.path.getsize(Options['Path'])
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if Options['RemoveOrg']:
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
          from  Init import MergeDictionaries; from  Log import MakeErrorMessage; from  UUID import TimeUUID
    else: from .Init import MergeDictionaries; from .Log import MakeErrorMessage; from .UUID import TimeUUID

    DftOpts = {
        'Path'     : '%s-%s.jpg' % (Path, TimeUUID()),
        'Size'     : (400, 300),
        'Quality'  : 25,
        'RemoveOrg': False
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = {
        'Ec': 0, 'Em': '',
        'Path': '',
        'Size': -1
    }

    try:
        if os.path.dirname(Options['Path']):
            os.makedirs(os.path.dirname(Options['Path']), exist_ok = True)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Mda = cv2.VideoCapture(Path)
        if not Mda.isOpened(): raise Exception('Couldn\'t Read Video Stream from File %s' % Path)

        Pos = int(min(Mda.get(cv2.CAP_PROP_FRAME_COUNT) / Mda.get(cv2.CAP_PROP_FPS) * 1000, 0.05 * 1000))
        Mda.set(cv2.CAP_PROP_POS_MSEC, Pos)

        cv2.imwrite(Options['Path'], Mda.read()[1])
        Mda.release()
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if Options['RemoveOrg']:
            os.remove(Path)
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response

    return __MakeThumbnail_PIL(Options['Path'], Options = {
                                                    'Path'     : '%s-%s.jpg' % (Path, TimeUUID()),
                                                    'Size'     : Options['Size'],
                                                    'Quality'  : Options['Quality'],
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
          from  Init import MergeDictionaries; from  Log import MakeErrorMessage; from  UUID import TimeUUID
    else: from .Init import MergeDictionaries; from .Log import MakeErrorMessage; from .UUID import TimeUUID

    DftOpts = {
        'Path'     : '%s-%s.jpg' % (Path, TimeUUID()),
        'Size'     : (400, 300),
        'Quality'  : 25,
        'RemoveOrg': False
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = {
        'Ec': 0, 'Em': '',
        'Path': '',
        'Size': -1
    }

    try:
        if os.path.dirname(Options['Path']):
            os.makedirs(os.path.dirname(Options['Path']), exist_ok = True)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Pdf = fitz.open(Path)
        Img = Pdf[0].get_pixmap()
        Img = PIL.Image.frombytes('RGB', [Img.width, Img.height], Img.samples)
        Img.save(Options['Path'], format = 'JPEG')
        Pdf.close()
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if Options['RemoveOrg']:
            os.remove(Path)
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response

    return __MakeThumbnail_PIL(Options['Path'], Options = {
                                                    'Path'     : '%s-%s.jpg' % (Path, TimeUUID()),
                                                    'Size'     : Options['Size'],
                                                    'Quality'  : Options['Quality'],
                                                    'RemoveOrg': True
                                                })
