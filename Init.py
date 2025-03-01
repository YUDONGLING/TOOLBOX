def MergeDictionaries(Base: dict, Override: dict) -> dict:
    '''
    Merge two Dictionaries Recursively.
    '''
    import copy

    if type(Base)     != dict: raise  TypeError('BASE MUST BE A TYPE OF DICTIONARY'.title())
    if type(Override) != dict: return Base # raise TypeError('OVERRIDE MUST BE A TYPE OF DICTIONARY'.title())

    Cfg = copy.deepcopy(Base)

    for _Key, _Value in Override.items():
        if _Key in Cfg:
            if type(Cfg[_Key]) == type(_Value) == dict:
                Cfg[_Key] = MergeDictionaries(Cfg[_Key], _Value)
            else:
                Cfg[_Key] = _Value
        else:
            Cfg[_Key] = _Value

    return Cfg


def ReadConfig(Path: str = 'ExeConfig.json') -> dict:
    '''
    Read Configuration from a JSON File.
    '''
    import os
    import json
    import portalocker

    if os.path.exists(Path):
        with portalocker.Lock(Path, 'r') as File:
            return json.loads(File.read())

    raise FileNotFoundError('FILE DOES NOT EXIST'.title())


def EncryptConfig(Path: str = 'ExeConfig.json') -> None:
    '''
    Encrypt Configuration and Save to a JSON File.
    '''
    raise NotImplementedError() # return SetConfig({}, Path)


def SetConfig(Cfg: dict, Path: str = 'ExeConfig.json', **Kwargs) -> None:
    '''
    Write Configuration to a JSON File. \n
    Use `Merge = True` to Merge the Configuration with Existing Config File.
    Use `Force = True` to Overwrite the Existing Config File (if Merge is Disabled).
    '''
    import os
    import json

    if os.path.exists(Path):
        if Kwargs.get('Merge', True):
            Cfg = MergeDictionaries(ReadConfig(Path), Cfg)
        elif not Kwargs.get('Force', False):
            raise FileExistsError('FILE ALREADY EXISTS, ADD FORCE = TRUE TO OVERWRITE'.title())
    elif os.path.dirname(Path):
        os.makedirs(os.path.dirname(Path), exist_ok = True)

    import portalocker

    with portalocker.Lock(Path, 'w') as File:
        File.write(json.dumps(Cfg, indent = 4, ensure_ascii = False))


def ReadEnvironVar(Path: str = 'EnvironVariable.json' or 'EnvironVariable_AES.json') -> dict:
    '''
    Decrypt Environment Variable from a JSON File.
    '''
    import os

    def __Decrypt__(Data, Fernet):
        if isinstance(Data, str):
            Data = Fernet.decrypt(Data.encode()).decode()
        elif isinstance(Data, list):
            Data = [__Decrypt__(_, Fernet) for _ in Data]
        elif isinstance(Data, dict):
            for Key, Value in Data.items():
                if Key in ['AesKey', 'Type']: continue
                Data[Key] = __Decrypt__(Value, Fernet)
        return Data

    Root, Extension = os.path.splitext(Path)

    RawEnvPath = (Root.removesuffix('_AES') + Extension) if Root.endswith('_AES') else Path
    if os.path.exists(RawEnvPath):
        return ReadConfig(RawEnvPath)

    AesEnvPath = (Root + '_AES' + Extension) if not Root.endswith('_AES') else Path
    if os.path.exists(AesEnvPath):
        from cryptography.fernet import Fernet
        return __Decrypt__(ReadConfig(AesEnvPath), Fernet(os.environ.get('AES_KEY', '').encode()))

    raise FileNotFoundError('FILE DOES NOT EXIST'.title())


def EncryptEnvironVar(Path: str = 'EnvironVariable.json' or 'EnvironVariable_AES.json') -> None:
    '''
    Encrypt Environment Variable and Save to a JSON File.
    '''
    return SetEnvironVar({}, Path)


def SetEnvironVar(Env: dict, Path: str = 'EnvironVariable.json' or 'EnvironVariable_AES.json', **Kwargs) -> None:
    '''
    Write Environment Variable to a JSON File. \n
    Use `Merge = True` to Merge the Environment Variable with Existing File.
    Use `Force = True` to Overwrite the Existing File (if Merge is Disabled).
    '''
    import os

    def __Encrypt__(Data, Fernet):
        if isinstance(Data, str):
            Data = Fernet.encrypt(Data.encode()).decode()
        elif isinstance(Data, list):
            Data = [__Encrypt__(_, Fernet) for _ in Data]
        elif isinstance(Data, dict):
            for Key, Value in Data.items():
                if Key in ['AesKey', 'Type']: continue
                Data[Key] = __Encrypt__(Value, Fernet)
        return Data

    Root, Extension = os.path.splitext(Path)
    RawEnvPath = (Root.removesuffix('_AES') + Extension) if Root.endswith('_AES') else Path
    AesEnvPath = (Root + '_AES' + Extension) if not Root.endswith('_AES') else Path

    if os.path.exists(RawEnvPath):
        if Kwargs.get('Merge', True):
            Env = MergeDictionaries(ReadConfig(RawEnvPath), Env)
        elif not Kwargs.get('Force', False):
            raise FileExistsError('FILE ALREADY EXISTS, ADD FORCE = TRUE TO OVERWRITE'.title())

    from cryptography.fernet import Fernet

    if Env.get('AesKey', None) is None:
        AesKey = Fernet.generate_key(); Env['AesKey'] = AesKey.decode()
    else:
        AesKey = Env['AesKey'].encode()

    SetConfig(Env, RawEnvPath, Merge = False, Force = True)
    SetConfig(__Encrypt__(Env, Fernet(AesKey)), AesEnvPath, Merge = False, Force = True)
