def MakeLog(Content: str, Path: str = 'Log/{{YYYY}}-{{MM}}-{{DD}}.txt') -> None:
    '''
    Make Log File with Content, Support Magic Variables for Path. \n

    Table of Magic Variables: \n
    Year         `{{YYYY}}`|`{{YY}}` ; Month            `{{MM}}`  ; Day         `{{DD}}` ;
    Hour         `{{HH}}`            ; Minute           `{{MI}}`  ; Second      `{{SS}}` ;
    Time Zone    `{{TZ}}`            ; Time Zone String `{{TZS}}` .
    '''
    import os
    import time
    import portalocker

    Response = {
        'Ec': 0, 'Em': '', 'Path': ''
    }

    Path = Path.replace('{{YYYY}}', time.strftime('%Y', time.localtime())) # 年　, Eg: 2021
    Path = Path.replace('{{YY}}'  , time.strftime('%y', time.localtime())) # 年　, Eg: 21
    Path = Path.replace('{{MM}}'  , time.strftime('%m', time.localtime())) # 月　, Eg: 01
    Path = Path.replace('{{DD}}'  , time.strftime('%d', time.localtime())) # 日　, Eg: 01
    Path = Path.replace('{{HH}}'  , time.strftime('%H', time.localtime())) # 时　, Eg: 00
    Path = Path.replace('{{MI}}'  , time.strftime('%M', time.localtime())) # 分　, Eg: 00
    Path = Path.replace('{{SS}}'  , time.strftime('%S', time.localtime())) # 秒　, Eg: 00
    Path = Path.replace('{{TZ}}'  , time.strftime('%z', time.localtime())) # 时区, Eg: +0800
    Path = Path.replace('{{TZS}}' , time.strftime('%Z', time.localtime())) # 时区, Eg: CST

    try:
        if os.path.dirname(Path):
            os.makedirs(os.path.dirname(Path), exist_ok = True)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        with portalocker.Lock(Path, 'a') as File:
            File.write('[%s] %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), Content))
        Response['Path'] = Path
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def MakeErrorMessage(Error: Exception) -> str:
    '''
    Make Error Message, Include File, Line Number and Function Name, for Debugging.
    '''
    import os
    import sys

    if hasattr(Error, '__traceback__') and Error.__traceback__:
        Modu = os.path.relpath(
            Error.__traceback__.tb_frame.f_code.co_filename,
            start = os.path.dirname(os.path.abspath(sys.argv[0]))
        )
        Func = 'Function <%s>' % Error.__traceback__.tb_frame.f_code.co_name
        Line = Error.__traceback__.tb_lineno
    else:
        Modu = 'N/A'
        Func = 'N/A'
        Line = 'N/A'

    if hasattr(Error, '__class__') and hasattr(Error.__class__, '__name__') and Error.__class__.__name__:
        Type = Error.__class__.__name__
    else:
        Type = 'Error'

    return 'File "%s", Line %s, in %s @%s: %s.' % (Modu, Line, Func, Type, str(Error).title().rstrip('.'))
