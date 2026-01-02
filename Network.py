def QueryDns(Host: str, Type: str = 'A', Global: bool = None, Region: str | list = None, Options: dict = None) -> str:
    '''
    Query the DNS of a Host at Specific Region (Country in the World, or City of China), via HTTP DNS.
    '''
    import os
    import json
    import random
    import requests

    if not __package__:
          from  Init import MergeDictionaries
    else: from .Init import MergeDictionaries

    DftOpts = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Provider'  : 'https://dns.alidns.com/resolve', # 'https://dns.alidns.com/resolve' By Alibaba Cloud Public DNS
                                                        # 'https://doh.pub/resolve'        By DNSPod Public DNS
                                                        # 'https://dns.google/resolve'     By Google Public DNS
        'Timeout'   : 5
    }
    Options = MergeDictionaries(DftOpts, Options)

    try:
        Type = {
            'A' :  1, 'NS' :  2, 'CNAME':  5, 'SOA':  6, 'PTR':  12,
            'MX': 15, 'TXT': 16, 'AAAA' : 28, 'SRV': 33, 'ANY': 255
        }[Type.upper()]

        Host = Host.removeprefix('//').removeprefix('http://').removeprefix('https://').removesuffix('/')
    except Exception as Error:
        return ''

    try:
        if Global is None:
            IP = ''
        else:
            with open(os.path.join(os.path.dirname(__file__), 'Extra', 'Global_IPs.json' if Global else 'CN_IPs.json'), 'r', encoding = 'utf-8') as File:
                IPs = json.load(File)

            def FetchIPs(Zone, IPs):
                Zone = Zone.split('.'); Temp = IPs
                while Zone:
                    try: Temp = Temp[Zone.pop(0)]
                    except KeyError: return []
                return Temp

            Pool = []; Region = [] if not Region else [Region] if isinstance(Region, str) else Region
            for Rule in [_ for _ in Region if     _.startswith('-')]: FetchIPs(Rule.removeprefix('-'), IPs).clear()
            for Rule in [_ for _ in Region if not _.startswith('-')]: Pool.append(FetchIPs(Rule, IPs))
            if not Pool: Pool = IPs

            def FlattenIPs(Tar, Src):
                if isinstance(Src, list):
                    for _ in Src: FlattenIPs(Tar, _)
                elif isinstance(Src, dict):
                    for _, _IPs in Src.items(): FlattenIPs(Tar, _IPs)
                else: Tar.append(Src)

            IP = []; FlattenIPs(IP, Pool)
            IP = random.choice(IP)
    except Exception as Error:
        return ''

    try:
        Url = f'{Options["Provider"]}?name={Host}&type={Type}'; Url += f'&edns_client_subnet={IP}' if IP else ''
        Hed = {
            'User-Agent': Options['User-Agent']
        }
        Rsp = requests.get(Url, headers = Hed, timeout = Options['Timeout']).json()

        if Rsp['Status'] != 0:
            raise Exception(f'HTTP DNS Query Failed, Status is {Rsp["Status"]}, Response is {Rsp}')
        else:
            Recode = [Item['data'] for Item in Rsp['Answer'] if Item['type'] == Type]
    except Exception as Error:
        return ''

    return random.choice(Recode) if Recode else ''


def QueryIpLocation(Ip: str, Options: dict = None) -> str:
    '''
    Query the Location of an IP Address.
    
    Bt   : IPv4 (国内 区县级, 国外 国家级)
    Zx   : IPv4 (国内 城市级, 国外 国家级), IPv6 (国内 城市级, 国外 省份级)
    Btv  : IPv4 (国内 城市级, 国外 省份级), IPv6 (国内 城市级, 国外 省份级)
    Ldd  : IPv4 (国内 区县级, 国外 城市级), IPv6 (国内 城市级, 国外 省份级)
    Ipa  : IPv4 (国内 城市级, 国外 城市级), IPv6 (国内 城市级, 国外 城市级)
    Ips  : IPv4 (国内 区县级, 国外 城市级), IPv6 (国内 省份级, 国外 省份级)
    Mei  : IPv4 (国内 楼栋级, 国外 城市级), IPv6 (国内 楼栋级, 国外 城市级)
    Dashi: IPv4 (国内 城市级, 国外 城市级), IPv6 (国内 城市级, 国外 城市级)
    '''
    import re

    if not __package__:
          from  Init import MergeDictionaries
    else: from .Init import MergeDictionaries

    DftOpts = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Provider_V4': 'Bt',     # Bt, Zx, Btv, Ldd, Ipa, Ips, Mei, Dashi
        'Provider_V6': 'Dashi',  #     Zx, Btv, Ldd, Ipa, Ips, Mei, Dashi
        'Timeout'    : 5
    }
    Options = MergeDictionaries(DftOpts, Options)

    Provider = None
    if '.' in Ip and re.match(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$', Ip): Provider = Options['Provider_V4']
    if ':' in Ip and re.match(r'^([\da-fA-F]{1,4}:){6}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^::([\da-fA-F]{1,4}:){0,4}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:):([\da-fA-F]{1,4}:){0,3}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){2}:([\da-fA-F]{1,4}:){0,2}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){3}:([\da-fA-F]{1,4}:){0,1}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){4}:((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){7}[\da-fA-F]{1,4}$|^:((:[\da-fA-F]{1,4}){1,6}|:)$|^[\da-fA-F]{1,4}:((:[\da-fA-F]{1,4}){1,5}|:)$|^([\da-fA-F]{1,4}:){2}((:[\da-fA-F]{1,4}){1,4}|:)$|^([\da-fA-F]{1,4}:){3}((:[\da-fA-F]{1,4}){1,3}|:)$|^([\da-fA-F]{1,4}:){4}((:[\da-fA-F]{1,4}){1,2}|:)$|^([\da-fA-F]{1,4}:){5}:([\da-fA-F]{1,4})?$|^([\da-fA-F]{1,4}:){6}:$', Ip): Provider = Options['Provider_V6']
    if Provider not in ['Bt', 'Zx', 'Btv', 'Ldd', 'Ipa', 'Ips', 'Mei', 'Dashi']: return '未知 未知'

    Location = [''] * 6     # 国家, 省份, 城市, 区县, 地址, 网络
    if  Provider == 'Bt'    : Location = __QueryIpLocation_Bt   (Ip, Options)
    if  Provider == 'Zx'    : Location = __QueryIpLocation_Zx   (Ip, Options)
    if  Provider == 'Btv'   : Location = __QueryIpLocation_Btv  (Ip, Options)
    if  Provider == 'Ldd'   : Location = __QueryIpLocation_Ldd  (Ip, Options)
    if  Provider == 'Ipa'   : Location = __QueryIpLocation_Ipa  (Ip, Options)
    if  Provider == 'Ips'   : Location = __QueryIpLocation_Ips  (Ip, Options)
    if  Provider == 'Mei'   : Location = __QueryIpLocation_Mei  (Ip, Options)
    if  Provider == 'Dashi' : Location = __QueryIpLocation_Dashi(Ip, Options)
    if  Location == [''] * 6: return '未知 未知'

    Location = [str('' if _ is None else _) for _ in Location]
    if  Location[0] == '中国':
        # 省份 Province
        Location[1] = re.sub(r'(维吾尔自治区|回族自治区|壮族自治区|自治区|特别行政区|省|市)$', '', Location[1]).removeprefix('中国')

        # 城市 City
        Location[2] = re.sub(r'(布依族苗族自治州|傣族景颇族自治州|哈尼族彝族自治州|蒙古族藏族自治州|土家族苗族自治州|柯尔克孜自治州|苗族侗族自治州|藏族羌族自治州|壮族苗族自治州|朝鲜族自治州|哈萨克自治州|傈僳族自治州|白族自治州|傣族自治州|回族自治州|蒙古自治州|彝族自治州|藏族自治州|地区|新区|盟|市|区)$', '', Location[2])
        Location[2] = '' if Location[1] in ['北京', '上海', '天津', '重庆', '香港', '澳门', '台湾'] and Location[1] == Location[2] else Location[2]

        # 区县 Area
        Location[3] = re.sub(r'(管理区管委会|行政委员会|风景名胜区|林区|市|县|区)$', '', Location[3]) if len(Location[3]) > 2 and not re.search(r'(管理区|回族区|聚集区|开发区|示范区|食品区|实验区|自治县|矿区|新区|园区|族区)$', Location[3]) else Location[3]

        # 网络 Network Provider
        if any([_ in Location[5].upper() for _ in ['广电', 'CABLE'  , 'BROADCAST'       ]]): Location[5] = '广电'
        if any([_ in Location[5].upper() for _ in ['电信', 'TELECOM', 'CHINANET'        ]]): Location[5] = '电信'
        if any([_ in Location[5].upper() for _ in ['联通', 'UNICOM' , 'CHINA169'        ]]): Location[5] = '联通'
        if any([_ in Location[5].upper() for _ in ['移动', 'MOBILE' , 'CMNET'           ]]): Location[5] = '移动'
        if any([_ in Location[5].upper() for _ in ['铁通', 'TIETONG', 'RAILWAT'         ]]): Location[5] = '铁通'
        if any([_ in Location[5].upper() for _ in ['教育', 'CERNET' , 'EDUCATION'       ]]): Location[5] = '教育网'
        if any([_ in Location[5].upper() for _ in ['阿里', 'ALIBABA', 'ALIYUN', 'TAOBAO']]): Location[5] = '阿里云'
        if any([_ in Location[5].upper() for _ in ['腾讯', 'TENCENT', 'QQ'    , 'WECHAT']]): Location[5] = '腾讯云'
    else:
        # 区县和城市重复时, 区县置空
        if Location[3] == Location[2]: Location[3] = ''
        # 城市和省份重复时, 城市置空
        if Location[2] == Location[1]: Location[2] = ''
        # 省份和国家重复时, 省份置空
        if Location[1] == Location[0]: Location[1] = ''

    return re.sub(r'\s+', ' ', ' '.join(Location).replace('CZ88.NET', '')).strip()


def __QueryIpLocation_Bt(Ip: str, Options: dict) -> list:
    import base64
    import requests

    try:
        Url = base64.b64decode('LWh0dHBzOi8vd3d3LmJ0LmNuL2FwaS9wYW5lbC9nZXRfaXBfaW5mbz9pcD0='.encode()).decode()[1:] + Ip
        Hed = {
            'User-Agent'     : 'BT-Panel',
            'X-Forwarded-For': Ip
        }
        Rsp = requests.get(Url, headers= Hed, timeout = Options['Timeout']).json()[Ip]

        return [Rsp['country'], Rsp['province'], Rsp['city'], Rsp['region'], '', Rsp['carrier']]
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Zx(Ip: str, Options: dict) -> list:
    import re
    import base64
    import requests

    try:
        Url = base64.b64decode('LWh0dHBzOi8vaXAuenhpbmMub3JnL2FwaS5waHA/dHlwZT1qc29uJmlwPQ=='.encode()).decode()[1:] + Ip
        Hed = {
            'Accept'          : '*/*',
            'Accept-Language' : 'zh-CN,zh;q=0.9',
            'Cache-Control'   : 'no-cache',
            'DNT'             : '1',
            'Pragma'          : 'no-cache',
            'Priority'        : 'u=1, i',
            'Referer'         : base64.b64decode('LWh0dHBzOi8vaXAuenhpbmMub3JnL2lwcXVlcnkv'.encode()).decode()[1:],
            'User-Agent'      : Options['User-Agent'],
            'X-Forwarded-For' : Ip,
            'X-Requested-With': 'XMLHttpRequest'
        }
        Rsp = requests.get(Url, headers = Hed, timeout = Options['Timeout']).json()['data']

        return (re.sub(r'\s+', ' ', Rsp['country'].replace('–', ' ').replace('\t', ' ')).split(' ') + [''] * 5)[:5] + [Rsp['local']]
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Btv(Ip: str, Options: dict) -> list:
    import base64
    import requests

    try:
        Url = base64.b64decode('LWh0dHBzOi8vYXBpLmxpdmUuYmlsaWJpbGkuY29tL2lwX3NlcnZpY2UvdjEvaXBfc2VydmljZS9nZXRfaXBfYWRkcj9pcD0='.encode()).decode()[1:] + Ip
        Hed = {
            'Accept'         : '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control'  : 'no-cache',
            'Content-Type'   : 'application/json;charset=UTF-8',
            'DNT'            : '1',
            'Origin'         : base64.b64decode('LWh0dHBzOi8vbGl2ZS5iaWxpYmlsaS5jb20='.encode()).decode()[1:],
            'Pragma'         : 'no-cache',
            'Priority'       : 'u=1, i',
            'Referer'        : base64.b64decode('LWh0dHBzOi8vbGl2ZS5iaWxpYmlsaS5jb20v'.encode()).decode()[1:],
            'Sec-Fetch-Dest' : 'empty',
            'Sec-Fetch-Mode' : 'cors',
            'Sec-Fetch-Site' : 'same-site',
            'User-Agent'     : Options['User-Agent'],
            'X-Forwarded-For': Ip
        }
        Rsp = requests.get(Url, headers = Hed, timeout = Options['Timeout']).json()['data']

        return [Rsp['country'], Rsp['province'], Rsp['city'], '', '', Rsp['isp'].upper()]
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Ldd(Ip: str, Options: dict) -> list:
    import base64
    import requests

    try:
        Url = base64.b64decode('LWh0dHBzOi8vb3BlbmFwaS5sZGRnby5uZXQvYmFzZS9nc2VydmljZS9hcGkvdjEvR2V0SXBBZGRyZXNz'.encode()).decode()[1:]
        Hed = {
            'Accept'         : '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control'  : 'no-cache',
            'Content-Type'   : 'application/json;charset=UTF-8',
            'DNT'            : '1',
            'Origin'         : base64.b64decode('LWh0dHBzOi8vd3d3LmxkZGdvLm5ldA=='.encode()).decode()[1:],
            'Pragma'         : 'no-cache',
            'Priority'       : 'u=1, i',
            'Referer'        : base64.b64decode('LWh0dHBzOi8vd3d3LmxkZGdvLm5ldC8='.encode()).decode()[1:],
            'Sec-Fetch-Dest' : 'empty',
            'Sec-Fetch-Mode' : 'cors',
            'Sec-Fetch-Site' : 'same-site',
            'User-Agent'     : Options['User-Agent'],
            'X-Forwarded-For': Ip
        }
        Dat = {
            'ip': Ip
        }
        Rsp = requests.post(Url, headers = Hed, json = Dat, timeout = Options['Timeout']).json()['data']

        return [Rsp['nation'], Rsp['province'], Rsp['city'], Rsp['area'], Rsp['address'], Rsp['type']]
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Ipa(Ip: str, Options: dict) -> list:
    import base64
    import requests

    try:
        Url = base64.b64decode('LWh0dHBzOi8vZGVtby5pcC1hcGkuY29tL2pzb24v'.encode()).decode()[1:] + Ip + base64.b64decode('LT9maWVsZHM9Y291bnRyeSxyZWdpb25OYW1lLGNpdHksaXNwLGFzLG9yZyZsYW5nPXpoLUNO'.encode()).decode()[1:]
        Hed = {
            'Accept'         : '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control'  : 'no-cache',
            'Connection'     : 'keep-alive',
            'DNT'            : '1',
            'Origin'         : base64.b64decode('LWh0dHBzOi8vaXAtYXBpLmNvbQ=='.encode()).decode()[1:],
            'Pragma'         : 'no-cache',
            'Referer'        : base64.b64decode('LWh0dHBzOi8vaXAtYXBpLmNvbS8='.encode()).decode()[1:],
            'Sec-Fetch-Dest' : 'empty',
            'Sec-Fetch-Mode' : 'cors',
            'Sec-Fetch-Site' : 'same-site',
            'User-Agent'     : Options['User-Agent'],
            'X-Forwarded-For': Ip
        }
        Rsp = requests.get(Url, headers = Hed, timeout = Options['Timeout']).json()

        return [Rsp['country'], Rsp['regionName'], Rsp['city'], '', '', Rsp['isp'] + Rsp['as'] + Rsp['org'] if Rsp['country'] == '中国' else Rsp['isp']]
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Ips(Ip: str, Options: dict) -> list:
    import re
    import base64
    import requests

    try:
        Url = base64.b64decode('LWh0dHBzOi8vd3d3Lmlwc2h1ZGkuY29tLw=='.encode()).decode()[1:] + Ip + base64.b64decode('LS5odG0='.encode()).decode()[1:]
        Hed = {
            'Accept'                   : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language'          : 'zh-CN,zh;q=0.9',
            'Cache-Control'            : 'no-cache',
            'Connection'               : 'keep-alive',
            'DNT'                      : '1',
            'Pragma'                   : 'no-cache',
            'Sec-Fetch-Dest'           : 'document',
            'Sec-Fetch-Mode'           : 'navigate',
            'Sec-Fetch-Site'           : 'none',
            'Sec-Fetch-User'           : '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent'               : Options['User-Agent'],
            'X-Forwarded-For'          : Ip
        }
        Rsp = requests.get(Url, headers = Hed, timeout = Options['Timeout'], allow_redirects = False).text

        __1 = re.search(r'<td class="th">归属地</td>[\s\S]*?<span>(.*?)</span>', Rsp); __1 = re.sub(r'<a.*?>(.*?)</a>|\s+', lambda m: m.group(1) if m.group(1) else ' ', __1.group(1)) if __1 else ''
        __2 = re.search(r'<td class="th">运营商</td>[\s\S]*?<span>(.*?)</span>', Rsp)

        return (__1.split(' ') + [''] * 5)[:5] + [__2.group(1) if __2 else '']
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Mei(Ip: str, Options: dict) -> list:
    import base64
    import requests

    try:
        Url = base64.b64decode('LWh0dHBzOi8vYXBpbW9iaWxlLm1laXR1YW4uY29tL2xvY2F0ZS92Mi9pcC9sb2M/cmdlbz10cnVlJmlwPQ=='.encode()).decode()[1:] + Ip
        Hed = {
            'Accept'         : '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control'  : 'no-cache',
            'Content-Type'   : 'application/json;charset=UTF-8',
            'DNT'            : '1',
            'Origin'         : base64.b64decode('LWh0dHBzOi8vd2FpbWFpLm1laXR1YW4uY29t'.encode()).decode()[1:],
            'Pragma'         : 'no-cache',
            'Priority'       : 'u=1, i',
            'Referer'        : base64.b64decode('LWh0dHBzOi8vd2FpbWFpLm1laXR1YW4uY29tLw=='.encode()).decode()[1:],
            'Sec-Fetch-Dest' : 'empty',
            'Sec-Fetch-Mode' : 'cors',
            'Sec-Fetch-Site' : 'same-site',
            'User-Agent'     : Options['User-Agent'],
            'X-Forwarded-For': Ip
        }
        Rsp_Locate = requests.get(Url, headers = Hed, timeout = Options['Timeout']).json()['data']
    except Exception as Error:
        return [''] * 6

    try:
        Url = base64.b64decode('LWh0dHBzOi8vYXBpbW9iaWxlLm1laXR1YW4uY29tL2dyb3VwL3YxL2NpdHkvbGF0bG5nLw=='.encode()).decode()[1:] + '%s,%s' % (Rsp_Locate['lat'], Rsp_Locate['lng']) + base64.b64decode('LT90YWc9MA=='.encode()).decode()[1:]
        Rsp_Latlng = requests.get(Url, headers = Hed, timeout = Options['Timeout']).json()['data']
        try:    return [Rsp_Latlng['country'], Rsp_Latlng['province'], Rsp_Latlng['city'], Rsp_Latlng['district'], ('%s (%s)' % (Rsp_Latlng['areaName'].strip(), Rsp_Latlng['detail'].strip())).removesuffix(' ()'), '']
        except: return [Rsp_Locate['rgeo']['country'], Rsp_Locate['rgeo']['province'], Rsp_Locate['rgeo']['city'], Rsp_Locate['rgeo'].get('district', ''), '', '']
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Dashi(Ip: str, Options: dict) -> list:
    import base64
    import requests

    try:
      # Url = base64.b64decode('LWh0dHBzOi8vbWFpbC4xNjMuY29tL2Zndy9tYWlsc3J2LWlwZGV0YWlsL2RldGFpbA=='.encode()).decode()[1:]
        Url = base64.b64decode('LWh0dHBzOi8vZGFzaGkuMTYzLmNvbS9mZ3cvbWFpbHNydi1pcGRldGFpbC9kZXRhaWw='.encode()).decode()[1:]
        Hed = {
            'Accept'                   : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language'          : 'zh-CN,zh;q=0.9',
            'Cache-Control'            : 'no-cache',
            'Connection'               : 'keep-alive',
            'DNT'                      : '1',
            'Pragma'                   : 'no-cache',
            'Sec-Fetch-Dest'           : 'document',
            'Sec-Fetch-Mode'           : 'navigate',
            'Sec-Fetch-Site'           : 'none',
            'Sec-Fetch-User'           : '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent'               : Options['User-Agent'],
            'X-Forwarded-For'          : Ip
        }
        Rsp = requests.get(Url, headers = Hed, timeout = Options['Timeout']).json()['result']

        return [Rsp['country'].replace('UNKNOWN', ''), Rsp['province'].replace('UNKNOWN', ''), Rsp['city'].replace('UNKNOWN', ''), '', '', (Rsp['isp'] + Rsp['org']).replace('UNKNOWN', '') if Rsp['country'] == '中国' else Rsp['isp'].replace('UNKNOWN', '')]
    except Exception as Error:
        return [''] * 6
