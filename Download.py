def HeadUrl(Url: str, Options: dict = None) -> dict:
    '''
    Head a URL. Return the Information of the URL,
    Including the HTTP Code, Location, Content Type, Content Length, etc.
    '''
    import time
    import requests

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

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

    Response = DotAccessDict({
        'Ec': 0, 'Em': '',
        'Code'    : -1,
        'Url'     : '',
        'Location': '',
        'Content-Type'    : '',
        'Content-Length'  : -1,
        'Last-Modified-At': -1
    })

    try:
        Response['Url'] = ('&' if '?' in Url else '?').join([Url, '&'.join([f'{Key}={Value}' for Key, Value in Options.Params.items()])]) if Options.Params else Url
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Rsp = requests.head(   Url,
                               headers = Options.Header,
                               params  = Options.Params,
                               cookies = Options.Cookie,
                               timeout = Options.Timeout,
                               verify  = Options.Verify,
                               allow_redirects = Options.AllowRedirects)

        if not Rsp.ok:
            Rsp = requests.get(Url,
                               headers = Options.Header,
                               params  = Options.Params,
                               cookies = Options.Cookie,
                               timeout = Options.Timeout,
                               verify  = Options.Verify,
                               stream  = True,
                               allow_redirects = Options.AllowRedirects)
            try: Rsp.close()
            except: pass
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Response['Code']             = Rsp.status_code
        Response['Location']         = Rsp.headers.get('Location', '') or Rsp.url
        Response['Content-Type']     = Rsp.headers.get('Content-Type', '')
        Response['Content-Length']   = int(Rsp.headers.get('Content-Length', -1))
        Response['Last-Modified-At'] = int(time.mktime(time.strptime(Rsp.headers.get('Last-Modified', ''), '%a, %d %b %Y %H:%M:%S %Z'))) if 'Last-Modified' in Rsp.headers else -1
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response
    
    return Response


def DownloadUrl(Url: str, Path: str, Options: dict = None) -> dict:
    '''
    Download a File from URL to Local Path, via Python Requests or DownloadKit (Need to Install).
    '''
    import os

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

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

        'Time': None,
        'DownloadKit.Block': 1024 * 1024 * 10,
        'DownloadKit.ShowDownloading' : False,
        'DownloadKit.CleanDownloading': False,
        'DownloadKit.ShowDownloading.Prefix': '',
        'DownloadKit.ShowDownloading.Suffix': ''
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '',
        'Size'    : -1,
        'Code'    : -1,
        'Url'     : '',
        'Location': '',
        'Content-Type'    : '',
        'Content-Length'  : -1,
        'Last-Modified-At': -1
    })

    try:
        Head = HeadUrl(Url, Options); Response.update({Key: Value for Key, Value in Head.items() if Key not in ['Ec', 'Em', 'Size']})

        if Head['Ec']          != 0: raise Exception(Head['Em'])
        if Head['Code'] // 100 != 2: raise Exception(f'HTTP Code is {Head["Code"]}')

        Tool = 'Requests' if (Head['Content-Length'] != -1 and Head['Content-Length'] <= Options['DownloadKit.Block']) else 'DownloadKit'
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if not os.path.isabs(Path):
            Path = os.path.abspath(Path)
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if os.path.dirname(Path):
            os.makedirs(os.path.dirname(Path), exist_ok = True)
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if Tool == 'Requests':
            Download = __GetFileViaRequests(Response['Location'], Path, Options)
        else:
            Download = __GetFileViaDownloadKit(Response['Location'], Path, Options)

        if Download['Ec']         !=  0                                               : raise Exception(Download['Em'])
        if Head['Content-Length'] != -1 and Download['Size'] != Head['Content-Length']: raise Exception(f'File Size is {Download["Size"]}, Content-Length is {Head["Content-Length"]}')

        Response['Size'] = Download['Size']
    except Exception as Error:
        try: os.remove(Path)
        except: pass
        Response['Ec'] = 50004; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        if Options.Time:
            os.utime(Path, (int(Options.Time), int(Options.Time)))
        elif Head['Last-Modified-At'] > 0:
            os.utime(Path, (int(Head['Last-Modified-At']), int(Head['Last-Modified-At'])))
    except Exception as Error:
        try: os.remove(Path)
        except: pass
        Response['Ec'] = 50005; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def __GetFileViaRequests(Url: str, Path: str, Options: dict = None) -> dict:
    '''
    DownloadUrl's Internal Function. Download a File from URL to Local Path via Python Requests.
    '''
    import os
    import requests

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

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

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Size': -1
    })

    try:
        Rsp = requests.get(Url,
                           headers = Options.Header,
                           params  = Options.Params,
                           cookies = Options.Cookie,
                           timeout = Options.Timeout,
                           verify  = Options.Verify,
                           allow_redirects = Options.AllowRedirects)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response
    
    try:
        if 200 <= Rsp.status_code < 300:
            with open(Path, 'wb') as File: File.write(Rsp.content)
            Response['Size'] = os.path.getsize(Path)
        else:
            raise Exception(f'HTTP Code is {Rsp.status_code}')
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response
    
    return Response


def __GetFileViaDownloadKit(Url: str, Path: str, Options: dict = None) -> dict:
    '''
    DownloadUrl's Internal Function. Download a File from URL to Local Path via DownloadKit.
    '''
    import os
    import time

    from DownloadKit import DownloadKit

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

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

        'DownloadKit.Block': 1024 * 1024 * 10,
        'DownloadKit.ShowDownloading' : False,
        'DownloadKit.CleanDownloading': False,
        'DownloadKit.ShowDownloading.Prefix': '',
        'DownloadKit.ShowDownloading.Suffix': ''
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Size': -1
    })

    try:
        Kit = DownloadKit(); Kit.block_size = Options['DownloadKit.Block']
        Tsk = Kit.add(Url, os.path.dirname(Path), os.path.basename(Path),
                      file_exists     = 'overwrite',
                      split           = True,
                      headers         = Options.Header,
                      params          = Options.Params,
                      cookies         = Options.Cookie,
                      timeout         = Options.Timeout,
                      verify          = Options.Verify,
                      allow_redirects = Options.AllowRedirects)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Timer = 0

        if Options['DownloadKit.ShowDownloading']:
            print(f'\r{Options["DownloadKit.ShowDownloading.Prefix"]}0.00 %{Options["DownloadKit.ShowDownloading.Suffix"]}', end = '')

            while Tsk.rate == None or Tsk.rate == 0.0:
                if Timer >= 10:
                    Tsk.cancel()
                    raise Exception('Connecting Timeout')
                Timer += 1
                time.sleep(1)

            while True:
                print(f'\r{Options["DownloadKit.ShowDownloading.Prefix"]}{Tsk.rate} %{Options["DownloadKit.ShowDownloading.Suffix"]}', end = '     ')
                if Tsk.is_done:
                    break
                else:
                    time.sleep(0.1)

        else:
            while Tsk.rate == None or Tsk.rate == 0.0:
                if Timer >= 10:
                    Tsk.cancel()
                    raise Exception('Connecting Timeout')
                Timer += 1
                time.sleep(1)
            Tsk.wait(show = False)

        if Tsk.result == 'success':
            Kit = None

            if Tsk.info != Path:
                try:
                    os.replace(Tsk.info, Path)
                except:
                    if os.path.exists(Path):
                        os.remove(Path)
                    os.rename(Tsk.info, Path)

            Response['Size'] = os.path.getsize(Path)
        else:
            Kit = None
            raise Exception('Download Failed, Result is %s' % Tsk.info)

        print(f'\r{" " * (os.get_terminal_size().columns - 1)}\r', end = '') if Options['DownloadKit.CleanDownloading'] else print()
    except Exception as Error:
        print(f'\r{" " * (os.get_terminal_size().columns - 1)}\r', end = '') if Options['DownloadKit.CleanDownloading'] else print()
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Response['Size'] = os.path.getsize(Path)
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response
