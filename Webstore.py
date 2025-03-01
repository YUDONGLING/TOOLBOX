def GetKv(Space: str, Item: str | list, OpenAPI: bool = True, Options: dict = None) -> dict:
    '''
    Get Key-Value Pair(s) from Aliyun DCDN KV Storage.

    # SAMPLE REQUEST BODY
    {
        'action'   :  'GET',
        'namespace':  'SAMPLE-STORAGE',
        'payload'  : ['KEY1', 'KEY2', 'KEY3', ...]
    }
    '''
    if not __package__:
          from  Init import MergeDictionaries
    else: from .Init import MergeDictionaries

    DftOpts = {
        'Region'  : '',
        'AK'      : '',
        'SK'      : '',
        'STSToken': None
    }
    Options = MergeDictionaries(DftOpts, Options)
    Payload = Item if isinstance(Item, list) else [Item]

    return __Kv_Api('GET', Space, Payload, Options) if OpenAPI else __Kv_Web('GET', Space, Payload, Options)


def PutKv(Space: str, Item: dict | list, OpenAPI: bool = True, Options: dict = None) -> dict:
    '''
    Put Key-Value Pair(s) to Aliyun DCDN KV Storage.

    # SAMPLE REQUEST BODY
    {
        'action'   :  'PUT',
        'namespace':  'SAMPLE-STORAGE',
        'payload'  : [
            { key: 'KEY1', value: 'VALUE1'                     },
            { key: 'KEY2', value: 'VALUE2', ttl   :          0 },
            { key: 'KEY3', value: 'VALUE3', expire: 1700000000 },
            ...
        ]
    }
    '''
    if not __package__:
          from  Init import MergeDictionaries
    else: from .Init import MergeDictionaries

    DftOpts = {
        'Region'  : '',
        'AK'      : '',
        'SK'      : '',
        'STSToken': None
    }
    Options = MergeDictionaries(DftOpts, Options)
    Payload = [{_Key.lower(): _Value for _Key, _Value in _.items()} for _ in (Item if isinstance(Item, list) else [Item])]

    return __Kv_Api('PUT', Space, Payload, Options) if OpenAPI else __Kv_Web('PUT', Space, Payload, Options)


def DeleteKv(Space: str, Item: str | list, OpenAPI: bool = True, Options: dict = None) -> dict:
    '''
    Delete Key-Value Pair(s) from Aliyun DCDN KV Storage.

    # SAMPLE REQUEST BODY
    {
        'action'   :  'DELETE',
        'namespace':  'SAMPLE-STORAGE',
        'payload'  : ['KEY1', 'KEY2', 'KEY3', ...]
    }
    '''
    if not __package__:
          from  Init import MergeDictionaries
    else: from .Init import MergeDictionaries

    DftOpts = {
        'Region'  : '',
        'Space'   : '',
        'AK'      : '',
        'SK'      : '',
        'STSToken': None
    }
    Options = MergeDictionaries(DftOpts, Options)
    Payload = Item if isinstance(Item, list) else [Item]

    return __Kv_Api('DELETE', Space, Payload, Options) if OpenAPI else __Kv_Web('DELETE', Space, Payload, Options)


def __Kv_Api(Action: str, Space: str, Item: list, Options: dict) -> dict:
    '''
    Operate Key-Value Pair(s) Operation for Aliyun DCDN KV Storage via OpenAPI.
    '''
    import json
    import time
    import asyncio

    from alibabacloud_tea_util import models as UtilModels
    from alibabacloud_tea_openapi import models as OpenApiModels
    from alibabacloud_openapi_util.client import Client as OpenApiUtilClient

    if not __package__:
          from  Log import MakeErrorMessage; from  Aliyun import __Client, __EndPoint
    else: from .Log import MakeErrorMessage; from .Aliyun import __Client, __EndPoint

    Response = {
        'Ec': 0, 'Em': '', 'Data': {}
    }

    # 限制并发请求数
    MaxReq = 10; Semaphore = asyncio.Semaphore(MaxReq)

    async def __Get__(PayloadItem, Client, Params, Runtime):
        _Key = str(PayloadItem)

        if len(_Key) > 512:
                return _Key, {'Code': 400, 'Value': None}

        try:
            async with Semaphore:
                Request = OpenApiModels.OpenApiRequest(query = OpenApiUtilClient.query({
                    'Namespace': Space,
                    'Key'      : _Key
                }))
                Result = await Client.call_api_async(Params, Request, Runtime)

            _Exp, _Val = Result['body']['Value'].split('|', 1); _Exp = int(_Exp)

            if _Exp != -1 and _Exp < time.time():
                return _Key, {'Code': 404, 'Value': None}

            try:
                return _Key, {'Code':   0, 'Value': json.loads(_Val)}
            except Exception as Error:
                return _Key, {'Code':   0, 'Value': _Val}
        except Exception as Error:
            if Error.data.get('Code') in ['InvalidAccount.NotFound', 'InvalidNameSpace.NotFound', 'InvalidKey.NotFound']:
                return _Key, {'Code': 404, 'Value': None}
            else:
                return _Key, {'Code': 500, 'Value': None}

    async def __Put__(PayloadItem, Client, Params, Runtime):
        _Key = str(PayloadItem['Key'.lower()])

        if len(_Key) > 512:
            return _Key, {'Code': 400, 'Value': None}

        _Exp = -1

        if PayloadItem.get('TTL'.lower())    and isinstance(PayloadItem['TTL'.lower()], int)    and PayloadItem['TTL'.lower()]    > 0: _Exp = int(time.time() + PayloadItem['TTL'.lower()])
        if PayloadItem.get('Expire'.lower()) and isinstance(PayloadItem['Expire'.lower()], int) and PayloadItem['Expire'.lower()] > 0: _Exp = PayloadItem['Expire'.lower()]

        _Val = PayloadItem['Value'.lower()]

        if     isinstance(_Val, dict) or isinstance(_Val, list): _Val = json.dumps(_Val, ensure_ascii = False)
        if not isinstance(_Val, str): _Val = str(_Val)

        try:
            async with Semaphore:
                Request = OpenApiModels.OpenApiRequest(query = OpenApiUtilClient.query({
                    'Namespace' : Space,
                    'Key'       : _Key
                } if _Exp == -1 else {
                    'Namespace' : Space,
                    'Key'       : _Key,
                    'Expiration': _Exp + 30
                }), body = {'Value': f'{_Exp}|{_Val}'})
                await Client.call_api_async(Params, Request, Runtime)

            return _Key, {'Code':   0, 'Value': None}
        except Exception as Error:
            print(Error)
            return _Key, {'Code': 500, 'Value': None}

    async def __Del__(PayloadItem, Client, Params, Runtime):
        _Key = str(PayloadItem)

        if len(_Key) > 512:
            return _Key, {'Code': 400, 'Value': None}
        
        try:
            async with Semaphore:
                Request = OpenApiModels.OpenApiRequest(query = OpenApiUtilClient.query({
                    'Namespace': Space,
                    'Key'      : _Key
                }))
                await Client.call_api_async(Params, Request, Runtime)

            if True:
                return _Key, {'Code':   0, 'Value': None}
        except Exception as Error:
            if Error.data.get('Code') in ['InvalidAccount.NotFound', 'InvalidNameSpace.NotFound', 'InvalidKey.NotFound']:
                return _Key, {'Code': 404, 'Value': None}
            else:
                return _Key, {'Code': 500, 'Value': None}

    async def __Main__():
        try:
            Client  = __Client(AK = Options['AK'], SK = Options['SK'], STSToken = Options['STSToken'], EndPoint = __EndPoint('Dcdn', Options['Region']))
            Params  = OpenApiModels.Params(
                action        = {'GET': 'GetDcdnKv', 'PUT': 'PutDcdnKv', 'DELETE': 'DeleteDcdnKv'}[Action],
                version       =  '2018-01-15',
                protocol      =  'HTTP',
                method        = {'GET': 'GET', 'PUT': 'POST', 'DELETE': 'POST'}[Action],
                auth_type     =  'AK',
                style         =  'RPC',
                pathname      =  '/',
                req_body_type = {'GET': 'json', 'PUT': 'formData', 'DELETE': 'json'}[Action],
                body_type     =  'json'
            )
            Runtime = UtilModels.RuntimeOptions(autoretry = True, max_attempts = 3, read_timeout = 10000, connect_timeout = 10000)
        except Exception as Error:
            Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error); return Response

        if Action == 'GET'   : Result = await asyncio.gather(*[__Get__(_, Client, Params, Runtime) for _ in Item])
        if Action == 'PUT'   : Result = await asyncio.gather(*[__Put__(_, Client, Params, Runtime) for _ in Item])
        if Action == 'DELETE': Result = await asyncio.gather(*[__Del__(_, Client, Params, Runtime) for _ in Item])

        Response['Data'] = {_Key: _Val for _Key, _Val in Result}
        return Response

    return asyncio.run(__Main__())


def __Kv_Web(Action: str, Space: str, Item: list, Options: dict) -> dict:
    '''
    Operate Key-Value Pair(s) Operation for Aliyun DCDN KV Storage via EdgeRoutine.
    '''
    import json
    import base64
    import requests

    if not __package__:
          from  Log import MakeErrorMessage
    else: from .Log import MakeErrorMessage

    Response = {
        'Ec': 0, 'Em': '', 'Data': {}
    }

    try:
        Url = base64.b64decode('LWh0dHA6Ly9zdG9yYWdlLmVkZ2Utcm91dGluZS55dWRvbmdsaW5nLm5ldC53LmNkbmdzbGIuY29tLw=='.encode()).decode()[1:]
        Hed = {
            'content-type': 'application/json',
            'host'        : base64.b64decode('LXN0b3JhZ2UuZWRnZS1yb3V0aW5lLnl1ZG9uZ2xpbmcubmV0'.encode()).decode()[1:]
        }
        Dat = {
            'action'   : Action,
            'namespace': Space,
            'payload'  : Item
        }
        Rsp = requests.post(Url, headers = Hed, data = json.dumps(Dat), timeout = 5).json()

        for Key, Value in Rsp['Data'.lower()].items():
            try:
                Response['Data'][Key] = {
                    'Code' :            Value['Code' .lower()],
                    'Value': json.loads(Value['Value'.lower()])
                }
            except Exception as Error:
                Response['Data'][Key] = {
                    'Code' : Value['Code' .lower()],
                    'Value': Value['Value'.lower()]
                }

        Response['Ec'] = Rsp['Ec'.lower()]
        Response['Em'] = Rsp['Em'.lower()]
    except Exception as Error:
        Response['Ec'] = 50000; Response['Em'] = MakeErrorMessage(Error)

    return Response
