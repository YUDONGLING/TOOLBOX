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
