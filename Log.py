def MakeLog(Content: str, Path: str = 'Log/{{YYYY}}-{{MM}}-{{DD}}.txt') -> dict:
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

    if not __package__:
          from  Init import DotAccessDict
    else: from  Init import DotAccessDict

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    TimeConst = time.localtime()

    Path = Path.replace('{{YYYY}}', time.strftime('%Y', TimeConst)) # 年　, Eg: 2021
    Path = Path.replace('{{YY}}'  , time.strftime('%y', TimeConst)) # 年　, Eg: 21
    Path = Path.replace('{{MM}}'  , time.strftime('%m', TimeConst)) # 月　, Eg: 01
    Path = Path.replace('{{DD}}'  , time.strftime('%d', TimeConst)) # 日　, Eg: 01
    Path = Path.replace('{{HH}}'  , time.strftime('%H', TimeConst)) # 时　, Eg: 00
    Path = Path.replace('{{MI}}'  , time.strftime('%M', TimeConst)) # 分　, Eg: 00
    Path = Path.replace('{{SS}}'  , time.strftime('%S', TimeConst)) # 秒　, Eg: 00
    Path = Path.replace('{{TZ}}'  , time.strftime('%z', TimeConst)) # 时区, Eg: +0800
    Path = Path.replace('{{TZS}}' , time.strftime('%Z', TimeConst)) # 时区, Eg: CST

    try:
        if os.path.dirname(Path):
            os.makedirs(os.path.dirname(Path), exist_ok = True)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        with portalocker.Lock(Path, 'a', encoding = 'utf-8') as File:
            File.write('[%s] %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S', TimeConst), Content))
        Response['Result'] = Path
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
          ) or 'N/A'
        Func = ('Function <%s>' % Error.__traceback__.tb_frame.f_code.co_name.replace('<module>', '')).replace('Function <>', 'N/A')
        Line = Error.__traceback__.tb_lineno or 'N/A'
    else:
        Modu = 'N/A'
        Func = 'N/A'
        Line = 'N/A'

    if hasattr(Error.__class__, '__name__') and Error.__class__.__name__:
        Type = Error.__class__.__name__
    else:
        Type = 'Error'

    return 'File "%s", Line %s, in %s @%s: %s.' % (Modu, Line, Func, Type, str(Error).title().rstrip('.'))
