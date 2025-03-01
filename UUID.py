def HashUUID(Path_Or_Data: str, Separator: str = '-') -> str:
    '''
    Convert a MD5 Hash to a UUID-like String.
    '''
    import os
    import hashlib

    if os.path.isfile(Path_Or_Data):
        with open(Path_Or_Data, 'rb') as File:
            Md5 = hashlib.md5(File.read()).hexdigest()
    else:
        Md5 = hashlib.md5(Path_Or_Data.encode()).hexdigest()

    return Separator.join([Md5[:8], Md5[8:12], Md5[12:16], Md5[16:20], Md5[20:]])


def TimeUUID(Time: int = None, Seed: tuple[int, int] = None, Separator: str = '-') -> str:
    '''
    Convert a Timestamp to a UUID-like String.
    '''
    import time
    import random

    Time = str(int(time.time()) if Time is None else int(Time)).zfill(10)
    Seed = (random.randint(0, 15), random.randint(0, 15)) if Seed is None else (Seed[0] % 16, Seed[1] % 16)
    Hexa = ''.join([f'{ord(Char) * (Seed[0] % 8 + 1) * (Seed[1] % 8 + 1):03x}' for Char in Time]) + f'{Seed[0]:1x}' + f'{Seed[1]:1x}'

    return Separator.join([Hexa[:8], Hexa[8:12], Hexa[12:16], Hexa[16:20], Hexa[20:]])


def TimeUUID_Sort(Path: str, Seperator: str = None) -> dict:
    '''
    Sort Files in a Directory by TimeUUID.
    '''
    import os

    if not __package__:
          from  Log import MakeErrorMessage
    else: from .Log import MakeErrorMessage

    Response = {
        'Ec': 0, 'Em': '', 'Files': []
    }

    try:
        Files = os.listdir(Path)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Metas = []
        for File in Files:
            _ = TimeUUID_Decode(File, Seperator)
            if _['Ec'] == 0: Metas.append({'Time': _['Time'], 'Name': File, 'Path': os.path.join(Path, File)})
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response
    
    try:
        Response['Files'] = sorted(Metas, key = lambda Info: Info['Time'])
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response
    
    return Response


def TimeUUID_Decode(UUID: str, Seperator: str = None) -> dict:
    '''
    Decode a UUID-like String to a Timestamp.
    '''
    if not __package__:
          from  Log import MakeErrorMessage
    else: from .Log import MakeErrorMessage

    Response = {
        'Ec': 0, 'Em': '', 'Time': -1
    }

    try:
        if Seperator is None:
            Seperator_Len = (len(UUID) - 32) // 4
            Seperator     = UUID[8: 8 + Seperator_Len] if Seperator_Len > 0 else ''
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        UUID = UUID.replace(Seperator, '')
        Seed = (int(UUID[-2], 16), int(UUID[-1], 16))
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Time = ''
        for _ in range(0, len(UUID) - 2, 3):
            Hexa  = int(UUID[_: _ + 3], 16)
            Time += chr(Hexa // ((Seed[0] % 8 + 1) * (Seed[1] % 8 + 1)))
        Response['Time'] = int(Time)
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response
