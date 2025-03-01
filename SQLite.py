def CreateDB(Path: str) -> dict:
    '''
    Create a SQLite Database.
    '''
    import os
    import sqlite3

    if not __package__:
          from  Log import MakeErrorMessage
    else: from .Log import MakeErrorMessage

    Response = {
        'Ec': 0, 'Em': '', 'Path': ''
    }

    try:
        if os.path.dirname(Path):
            os.makedirs(os.path.dirname(Path), exist_ok = True)
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Conn = sqlite3.connect(Path)
        Conn.close()
        Response['Path'] = Path
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response


def ExecuteDB(Path: str, Query: str, Param: tuple = None) -> dict:
    '''
    Execute a SQLite Query.
    '''
    import sqlite3

    if not __package__:
          from  Log import MakeErrorMessage
    else: from .Log import MakeErrorMessage

    Response = {
        'Ec': 0, 'Em': '', 'Data': []
    }

    try:
        Conn   = sqlite3.connect(Path)
        Cursor = Conn.cursor()
        Cursor.execute(Query, Param or ())
    except Exception as Error:
        Response['Ec'] = 50001; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Response['Data'] = Cursor.fetchall()
    except Exception as Error:
        Response['Ec'] = 50002; Response['Em'] = MakeErrorMessage(Error); return Response

    try:
        Conn.commit()
        Conn.close()
    except Exception as Error:
        Response['Ec'] = 50003; Response['Em'] = MakeErrorMessage(Error); return Response

    return Response
