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
