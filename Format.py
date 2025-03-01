def SafePath(Path: str, Options: dict = None) -> dict:
    '''
    Check and Safety the Path, Return the Safety Path.
    '''
    import re

    if not __package__:
          from  Init import MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import MergeDictionaries; from .Log import MakeErrorMessage

    DftOpts = {
        'MaxLength'   : 50,
        'ForceReplace': []
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = {
        'Ec': 0, 'Em': '',
        'Path': ''
    }

    try:
        for Rule in Options['ForceReplace']:
            if len(Rule) == 2: Path = Path.replace(Rule[0], Rule[1])
        Response['Path'] = re.sub(r'\s+', ' ', re.sub(r'[\\/:*?\"<>|\n]', ' ', Path)).lstrip()[:Options['MaxLength']].rstrip()
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response
    
    return Response


def ConvertSize(Size: int, Unit: str = 'B', Options: dict = None) -> dict:
    '''
    Convert the Size to Human Readable Format, Support Magic Variables for Storage Unit. \n

    Table of Magic Variables: \n
    Size `{{Size}}` for Auto Decided Unit, or `{{Size:B|KB|MB|GB|TB|PB}}` to Convert to Specific Unit. \n
    Unit `{{Unit}}` for Auto Decided Unit, or `{{Unit:B|KB|MB|GB|TB|PB}}` to Convert to Specific Unit. \n
    '''

    if not __package__:
          from  Init import MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import MergeDictionaries; from .Log import MakeErrorMessage

    DftOpts = {
        'Format': '{{Size}} {{Unit}}',
        'Place_After_Decimal_Point': 2
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = {
        'Ec': 0, 'Em': '',
        'Result': ''
    }

    Units   = ['B',     'KB',     'MB',     'GB',     'TB',     'PB'    ]
    Weights = {'B':  0, 'KB':  1, 'MB':  2, 'GB':  3, 'TB':  4, 'PB':  5}
    Sizes   = {'B': -1, 'KB': -1, 'MB': -1, 'GB': -1, 'TB': -1, 'PB': -1}

    try:
        if Size < 0          : raise ValueError('Size Must be Positive')
        if not Unit in Units : raise ValueError('Unit Must in B, KB, MB, GB, TB or PB')
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        SizeInBytes = Size * (1024 ** Weights[Unit])

        for Unit in Units:
            Sizes[Unit] = SizeInBytes / (1024 ** Weights[Unit])

        AutoUnit = [Unit for Unit in Units if Sizes[Unit] >= 1][-1]
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Result = Options['Format'].replace('{{Size}}', f'{Sizes[AutoUnit]:.{Options["Place_After_Decimal_Point"]}f}').replace('{{Unit}}', AutoUnit)

        for Unit in Units:
            Result = Result.replace(
                '{{Size:%s}}' % Unit, f'{Sizes[Unit]:.{Options["Place_After_Decimal_Point"]}f}'
            ).replace('{{Unit:%s}}' % Unit, Unit)

        Response['Result'] = Result
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response
    
    return Response
