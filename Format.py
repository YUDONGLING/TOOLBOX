def SafePath(Path: str, Options: dict = None) -> dict:
    '''
    Check and Safety the Path, Return the Safety Path.
    '''
    import re
    import unicodedata

    if not __package__:
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

    DftOpts = {
        'MaxLength'   : 50,
        'ForceReplace': [],
        'ConvertMacSpecialChars' : True,
        'NormalizeUnicode'       : True,
        'RemoveUnsafeUnicode'    : True,
        'UnsafeUnicodeCharacters': '',
        'UnsafeUnicodeRanges'    : [
            (0x02B0, 0x02FF),    # Spacing Modifier Letters
            (0x0E50, 0x0E59),    # Thai digits commonly used as kaomoji eyes
            (0x1760, 0x177F),    # Tagbanwa letters sometimes used as decoration
            (0x1D00, 0x1DBF)     # Phonetic Extensions
        ],
        'UnicodeReplacement'     : ' '
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

    try:
        for Rule in Options.ForceReplace:
            if isinstance(Rule, (list, tuple)) and len(Rule) == 2:
                if isinstance(Rule[0], str) and isinstance(Rule[1], str):
                    Path = Path.replace(Rule[0], Rule[1])

        if Options.ConvertMacSpecialChars:
            # Synology/Samba VFS store Mac-special Characters as CATIA Private-Use Code Points.
            MacSpecialChars = {
                '\uf020': '"',
                '\uf021': '*',
                '\uf022': '/',
                '\uf023': ':',
                '\uf024': '<',
                '\uf025': '>',
                '\uf026': '?',
                '\uf027': '\\',
                '\uf028': '|'
            }
            for Search, Replace in MacSpecialChars.items():
                Path = Path.replace(Search, Replace)

        if Options.NormalizeUnicode:
            Path = unicodedata.normalize('NFKC', Path)

        if Options.RemoveUnsafeUnicode:
            UnsafeUnicodeCharacters = set(Options.UnsafeUnicodeCharacters) if isinstance(Options.UnsafeUnicodeCharacters, str) else set()
            UnsafeUnicodeRanges = Options.UnsafeUnicodeRanges if isinstance(Options.UnsafeUnicodeRanges, list) else []

            def _IsVariationSelector(Char: str) -> bool:
                CodePoint = ord(Char)
                return 0xFE00 <= CodePoint <= 0xFE0F or 0xE0100 <= CodePoint <= 0xE01EF

            def _IsInUnsafeUnicodeRanges(Char: str) -> bool:
                CodePoint = ord(Char)
                for Range in UnsafeUnicodeRanges:
                    if isinstance(Range, (list, tuple)) and len(Range) == 2:
                        Start, End = Range
                        if isinstance(Start, int) and isinstance(End, int) and Start <= CodePoint <= End:
                            return True
                return False

            def _IsEmojiCodePoint(Char: str) -> bool:
                CodePoint = ord(Char)
                return 0x2600 <= CodePoint <= 0x27BF or 0x1F000 <= CodePoint <= 0x1FAFF

            def _IsUnsafeUnicodeChar(Char: str) -> bool:
                Category = unicodedata.category(Char)
                CodePoint = ord(Char)

                if Char in UnsafeUnicodeCharacters:
                    return True
                if _IsInUnsafeUnicodeRanges(Char):
                    return True
                if Category in ('Cc', 'Cs', 'Co'):
                    return True
                if Category == 'Cf' and CodePoint != 0x200D:
                    return True
                if Category[0] == 'M' and not _IsVariationSelector(Char):
                    return True
                if Category[0] == 'S' and CodePoint > 0x7F and not _IsEmojiCodePoint(Char):
                    return True
                return False

            Replacement = Options.UnicodeReplacement if isinstance(Options.UnicodeReplacement, str) else ' '
            Path = ''.join(Replacement if _IsUnsafeUnicodeChar(Char) else Char for Char in Path)

        Response['Result'] = re.sub(r'\s+', ' ', re.sub(r'[\\/:*?"<>|\r\n\t]', ' ', Path)).lstrip()[:Options.MaxLength].rstrip()
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
          from  Init import DotAccessDict, MergeDictionaries; from  Log import MakeErrorMessage
    else: from .Init import DotAccessDict, MergeDictionaries; from .Log import MakeErrorMessage

    DftOpts = {
        'Format': '{{Size}} {{Unit}}',
        'Place_After_Decimal_Point': 2
    }
    Options = MergeDictionaries(DftOpts, Options)

    Response = DotAccessDict({
        'Ec': 0, 'Em': '', 'Result': None
    })

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

        for _Unit in Units:
            Sizes[_Unit] = SizeInBytes / (1024 ** Weights[_Unit])

        AutoUnit = [_Unit for _Unit in Units[1:] if Sizes[_Unit] >= 1]
        AutoUnit = AutoUnit[-1] if AutoUnit else 'B'
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Result = Options.Format.replace('{{Size}}', f'{Sizes[AutoUnit]:.{Options.Place_After_Decimal_Point}f}').replace('{{Unit}}', AutoUnit)

        for _Unit in Units:
            Result = Result.replace(
                '{{Size:%s}}' % _Unit, f'{Sizes[_Unit]:.{Options.Place_After_Decimal_Point}f}'
            ).replace('{{Unit:%s}}' % _Unit, _Unit)

        Response['Result'] = Result
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response
    
    return Response
