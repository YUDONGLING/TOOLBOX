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
        for Rule in Options.ForceReplace:
            if isinstance(Rule, (list, tuple)) and len(Rule) == 2:
                if isinstance(Rule[0], str) and isinstance(Rule[1], str):
                    Path = Path.replace(Rule[0], Rule[1])
        Response['Path'] = re.sub(r'\s+', ' ', re.sub(r'[\\/:*?"<>|\n]', ' ', Path)).lstrip()[:Options.MaxLength].rstrip()
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

    Units   = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    Weights = { Name: Index for Index, Name in enumerate(Units)}
    Sizes   = { Name: -1    for        Name in           Units }

    try:
        if not isinstance(Size, (int, float)): raise TypeError ('Size Must be Int or Float')
        if Size < 0                          : raise ValueError('Size Must be Positive')
        if not Unit in Units                 : raise ValueError('Unit Must in B, KB, MB, GB, TB or PB')
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        SizeInBytes = Size * (1024 ** Weights[Unit])

        for Unit in Units:
            Sizes[Unit] = SizeInBytes / (1024 ** Weights[Unit])

        AutoUnit = [Unit for Unit in Units[1:] if Sizes[Unit] >= 1]
        AutoUnit = AutoUnit[-1] if AutoUnit else 'B'
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Result = Options.Format.replace('{{Size}}', f'{Sizes[AutoUnit]:.{Options.Place_After_Decimal_Point}f}').replace('{{Unit}}', AutoUnit)

        for Unit in Units:
            Result = Result.replace(
                '{{Size:%s}}' % Unit, f'{Sizes[Unit]:.{Options.Place_After_Decimal_Point}f}'
            ).replace('{{Unit:%s}}' % Unit, Unit)

        Response['Result'] = Result
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response
    
    return Response
