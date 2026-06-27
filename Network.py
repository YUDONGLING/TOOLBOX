def QueryDns(Host: str, Type: str = 'A', Global: bool = None, Region: str | list = None, Options: dict = None) -> str:
    '''
    Query the DNS of a Host at Specific Region (Country in the World, or City of China), via HTTP DNS.
    '''
    import os
    import json
    import random
    import requests
    import urllib.parse

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

        Host = urllib.parse.urlsplit(Host if '://' in Host else f'//{Host}').hostname or ''
        if not Host:
            raise ValueError('Invalid Host')
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

            if not IP: return ''
            IP = random.choice(IP)
    except Exception as Error:
        return ''

    try:
        Url = f'{Options["Provider"]}?name={Host}&type={Type}'; Url += f'&edns_client_subnet={IP}' if IP else ''
        Hed = {
            'User-Agent': Options['User-Agent']
        }
        Rsp = requests.get(Url, headers = Hed, timeout = Options.Timeout).json()

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
    
    Bt       : IPv4 (国内 区县级, 国外 国家级)
    Zx       : IPv4 (国内 城市级, 国外 国家级), IPv6 (国内 城市级, 国外 省份级)
    Btv      : IPv4 (国内 城市级, 国外 省份级), IPv6 (国内 城市级, 国外 省份级)
    Ipa      : IPv4 (国内 城市级, 国外 城市级), IPv6 (国内 城市级, 国外 城市级)
    Ips      : IPv4 (国内 城市级, 国外 城市级), IPv6 (国内 省份级, 国外 省份级)
    Red      : IPv4 (国内 城市级, 国外 城市级), IPv6 (国内 城市级, 国外 城市级)
    Dashi    : IPv4 (国内 城市级, 国外 城市级), IPv6 (国内 城市级, 国外 城市级)
    CnSpeed  : IPv4 (国内 城市级, 国外 城市级), IPv6 (国内 城市级, 国外 城市级)
    Lecloud  : IPv4 (国内 城市级, 国外 城市级)
    Pconline : IPv4 (国内 城市级, 国外 国家级)
    '''
    import re

    if not __package__:
          from  Init import MergeDictionaries
    else: from .Init import MergeDictionaries

    DftOpts = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Provider_V4': 'Bt',     # Bt, Zx, Btv, Ipa, Ips, Red, Dashi, CnSpeed, Lecloud, Pconline
        'Provider_V6': 'Dashi',  #     Zx, Btv, Ipa, Ips, Red, Dashi, CnSpeed
        'Timeout'    : 5
    }
    Options = MergeDictionaries(DftOpts, Options)

    Provider = None
    if '.' in Ip and re.match(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$', Ip): Provider = Options.Provider_V4
    if ':' in Ip and re.match(r'^([\da-fA-F]{1,4}:){6}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^::([\da-fA-F]{1,4}:){0,4}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:):([\da-fA-F]{1,4}:){0,3}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){2}:([\da-fA-F]{1,4}:){0,2}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){3}:([\da-fA-F]{1,4}:){0,1}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){4}:((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){7}[\da-fA-F]{1,4}$|^:((:[\da-fA-F]{1,4}){1,6}|:)$|^[\da-fA-F]{1,4}:((:[\da-fA-F]{1,4}){1,5}|:)$|^([\da-fA-F]{1,4}:){2}((:[\da-fA-F]{1,4}){1,4}|:)$|^([\da-fA-F]{1,4}:){3}((:[\da-fA-F]{1,4}){1,3}|:)$|^([\da-fA-F]{1,4}:){4}((:[\da-fA-F]{1,4}){1,2}|:)$|^([\da-fA-F]{1,4}:){5}:([\da-fA-F]{1,4})?$|^([\da-fA-F]{1,4}:){6}:$', Ip): Provider = Options.Provider_V6
    if Provider not in ['Bt', 'Zx', 'Btv', 'Ipa', 'Ips', 'Red', 'Dashi', 'CnSpeed', 'Lecloud', 'Pconline']: return '未知 未知'

    Location = [''] * 6 # 国家, 省份, 城市, 区县, 地址, 网络
    if Provider == 'Bt'       : Location = __QueryIpLocation_Bt      (Ip, Options)
    if Provider == 'Zx'       : Location = __QueryIpLocation_Zx      (Ip, Options)
    if Provider == 'Btv'      : Location = __QueryIpLocation_Btv     (Ip, Options)
    if Provider == 'Ipa'      : Location = __QueryIpLocation_Ipa     (Ip, Options)
    if Provider == 'Ips'      : Location = __QueryIpLocation_Ips     (Ip, Options)
    if Provider == 'Red'      : Location = __QueryIpLocation_Red     (Ip, Options)
    if Provider == 'Dashi'    : Location = __QueryIpLocation_Dashi   (Ip, Options)
    if Provider == 'CnSpeed'  : Location = __QueryIpLocation_CnSpeed (Ip, Options)
    if Provider == 'Lecloud'  : Location = __QueryIpLocation_Lecloud (Ip, Options)
    if Provider == 'Pconline' : Location = __QueryIpLocation_Pconline(Ip, Options)
    if Location == [''] * 6: return '未知 未知'

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
        Network = Location[5].upper()
        for Name, Pattern in {
            'UCloud': r'优刻得|UCLOUD|U-CLOUD',
            '安畅网络': r'安畅|ANCHNET',
            '长城宽带': r'长城宽带|GWBN|GREAT\s*WALL\s*BROADBAND',
            '帝联科技': r'帝联|DNION',
            '光环新网': r'光环新网|SINNET',
            '华云数据': r'华云|HUAYUN',
            '世纪互联': r'世纪互联|21VIANET|VNET',
            '首都在线': r'首都在线|CAPITAL\s*ONLINE',
            '网宿科技': r'网宿|WANGSU|CHINA\s*NETCENTER|QUANTIL|WSCDN',
            '西部数码': r'西部数码|WEST\.?CN',
            '知道创宇': r'知道创宇|KNOWNSEC|加速乐|JIASULE',
            '阿里云': r'阿里|ALIBABA|ALIYUN|ALICLOUD|TAOBAO',
            '百度云': r'百度|BAIDU',
            '白山云': r'白山|BAISHAN',
            '多吉云': r'多吉|DOGE\s*CLOUD',
            '华为云': r'华为|HUAWEI',
            '教育网': r'教育|CERNET|EDUCATION',
            '金山云': r'金山|KINGSOFT|KSYUN',
            '京东云': r'京东|JINGDONG|JD\.COM|JD\s*CLOUD',
            '联通云': r'联通云|WO\s*CLOUD|UNICOM\s*CLOUD',
            '美团云': r'美团|MEITUAN',
            '鹏博士': r'鹏博士|DR\s*PENG',
            '奇虎云': r'奇虎|QIHOO|360云|360\s*CLOUD',
            '七牛云': r'七牛|QINIU',
            '腾讯云': r'腾讯|TENCENT|QCLOUD|\bQQ\b|WECHAT',
            '天翼云': r'天翼云|CTYUN|CHINA\s*TELECOM\s*CLOUD',
            '网易云': r'网易|NETEASE',
            '小米云': r'小米|XIAOMI|MI\s*CLOUD',
            '新浪云': r'新浪|SINA|SAE',
            '移动云': r'移动云|CHINA\s*MOBILE\s*CLOUD|CMCC\s*CLOUD',
            '又拍云': r'又拍|UPYUN',
            '字节云': r'火山|VOLC|VULCAN|BYTE\s*DANCE|TOUTIAO|DOUYIN',
            '电信': r'电信|CHINA\s*TELECOM|CHINANET|CTGNET|CN2|163NET',
            '广电': r'广电|中国广播电视|CBN|CABLE|BROADCAST',
            '蓝汛': r'蓝汛|CHINACACHE',
            '联通': r'联通|网通|UNICOM|CHINA169|CNCGROUP|NETCOM',
            '青云': r'青云|优帆科技|QINGCLOUD|YUNIFY',
            '铁通': r'铁通|TIETONG|RAILWAY|RAILCOM',
            '移动': r'移动|MOBILE|CMNET|CMCC|CMI',
        }.items():
            if re.search(Pattern, Network):
                Location[5] = Name; break

    else:
        # 区县和城市重复时, 区县置空
        if Location[3] == Location[2]: Location[3] = ''
        # 城市和省份重复时, 城市置空
        if Location[2] == Location[1]: Location[2] = ''
        # 省份和国家重复时, 省份置空
        if Location[1] == Location[0]: Location[1] = ''

    return _CleanLocName(' '.join(Location))


def _CleanLocName(Text: str) -> str:
    import re
    return re.sub(r'\s+', ' ', str('' if Text is None else Text).replace('UNKNOWN', '').replace('CZ88.NET', '')).strip()


def _MergeLocNames(*Texts: str) -> str:
    import re

    Names = []
    Norms = []
    for Text in Texts:
        Text = _CleanLocName(Text)
        if not Text: continue

        Norm = re.sub(r'\s+', '', Text).upper()
        Add = True
        Replace = None
        Remove = []
        for Idx, _ in enumerate(Norms):
            if Norm == _ or Norm in _:
                Add = False
                break
            if _ in Norm:
                if Replace is None:
                    Replace = Idx
                else:
                    Remove.append(Idx)
        if not Add: continue
        if Replace is not None:
            Names[Replace] = Text
            Norms[Replace] = Norm
            for Idx in reversed(Remove):
                del Names[Idx]
                del Norms[Idx]
            continue
        for Idx in reversed(Remove):
            del Names[Idx]
            del Norms[Idx]

        Names.append(Text)
        Norms.append(Norm)

    return ' '.join(Names)


def __QueryIpLocation_Bt(Ip: str, Options: dict) -> list:
    import base64
    import requests

    try:
        Url = base64.b64decode('LWh0dHBzOi8vd3d3LmJ0LmNuL2FwaS9wYW5lbC9nZXRfaXBfaW5mbz9pcD0='.encode()).decode()[1:] + Ip
        Hed = {
            'User-Agent'     : 'BT-Panel',
            'X-Forwarded-For': Ip
        }
        Rsp = requests.get(Url, headers= Hed, timeout = Options.Timeout).json()[Ip]

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
        Rsp = requests.get(Url, headers = Hed, timeout = Options.Timeout).json()['data']

        if Rsp.get('ip', {}).get('query') != Ip:
            raise ValueError('Response IP Mismatch')

        return (re.sub(r'\s+', ' ', Rsp['country'].replace('–', ' ').replace('\t', ' ')).split(' ') + [''] * 5)[:5] + [Rsp['local']]
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Btv(Ip: str, Options: dict) -> list:
    import base64
    import requests

    try:
      # Url = base64.b64decode('LWh0dHBzOi8vYXBpLmxpdmUuYmlsaWJpbGkuY29tL2NsaWVudC92MS9JcC9nZXRJbmZvTmV3P2lwPQ=='.encode()).decode()[1:] + Ip
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
        Rsp = requests.get(Url, headers = Hed, timeout = Options.Timeout).json()['data']

        if Rsp.get('addr') != Ip:
            raise ValueError('Response IP Mismatch')

        return [Rsp['country'], Rsp['province'], Rsp['city'], '', '', Rsp['isp'].upper()]
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Ipa(Ip: str, Options: dict) -> list:
    import base64
    import requests

    try:
        Url = base64.b64decode('LWh0dHA6Ly9kZW1vLmlwLWFwaS5jb20vanNvbi8='.encode()).decode()[1:] + Ip + base64.b64decode('LT9maWVsZHM9Y291bnRyeSxyZWdpb25OYW1lLGNpdHksaXNwLGFzLG9yZyxxdWVyeSZsYW5nPXpoLUNO'.encode()).decode()[1:]
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
        Rsp = requests.get(Url, headers = Hed, timeout = Options.Timeout).json()

        if 'query' in Rsp and Rsp.get('query') != Ip:
            raise ValueError('Response IP Mismatch')

        return [Rsp['country'], Rsp['regionName'], Rsp['city'], '', '', _MergeLocNames(Rsp['isp'], Rsp['as'], Rsp['org']) if Rsp['country'] == '中国' else Rsp['isp']]
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
        Rsp = requests.get(Url, headers = Hed, timeout = Options.Timeout, allow_redirects = False).text

        if Ip not in Rsp:
            raise ValueError('Response IP Mismatch')

        __1 = re.search(r'<td class="th">归属地</td>[\s\S]*?<span>(.*?)</span>', Rsp); __1 = re.sub(r'<a.*?>(.*?)</a>|\s+', lambda m: m.group(1) if m.group(1) else ' ', __1.group(1)) if __1 else ''
        __2 = re.search(r'<td class="th">运营商</td>[\s\S]*?<span>(.*?)</span>', Rsp)

        return (__1.split(' ') + [''] * 5)[:5] + [__2.group(1) if __2 else '']
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Red(Ip: str, Options: dict) -> list:
    import base64
    import requests

    try:
      # Url = base64.b64decode('LWh0dHBzOi8vZ3NsYi54aWFvaG9uZ3NodS5jb20vYXBpL2h0dHBkbnMvdjEvZG9tYWlucz9kb21haW5zPXd3dy54aWFvaG9uZ3NodS5jb20='.encode()).decode()[1:]
        Url = base64.b64decode('LWh0dHBzOi8vZ3NsYi54aWFvaG9uZ3NodS5jb20vYXBpL2dzbGIvdjEvZG9tYWluTmV3P2RvbWFpbnM9d3d3LnhpYW9ob25nc2h1LmNvbQ=='.encode()).decode()[1:]
        Hed = {
            'Accept'         : '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control'  : 'no-cache',
            'Connection'     : 'Keep-Alive',
            'Pragma'         : 'no-cache',
            'Referer'        : base64.b64decode('LWh0dHBzOi8vYXBwLnhocy5jbi8='.encode()).decode()[1:],
            'User-Agent'     : base64.b64decode('LWRpc2NvdmVyLzkuMjIuMSAoaVBob25lOyBpT1MgMjYuMy4xOyBTY2FsZS8zLjAwKSBSZXNvbHV0aW9uLzEyOTAqMjc5NiBWZXJzaW9uLzkuMjIuMSBCdWlsZC85MjIxODAxIERldmljZS8oQXBwbGUgSW5jLjtpUGhvbmUxNiwyKSBOZXRUeXBlL0NlbGxOZXR3b3Jr'.encode()).decode()[1:],
            base64.b64decode('LVgtTmV0LUNvcmU='.encode()).decode()[1:]: 'crn',
            base64.b64decode('LVhocy1SZWFsLUlw'.encode()).decode()[1:]: Ip
        }
        Rsp = requests.get(Url, headers = Hed, timeout = Options.Timeout).json()['client_info']

        if Rsp.get('ip') != Ip:
            raise ValueError('Response IP Mismatch')

        return [Rsp['country'], Rsp['province'], Rsp['city'], '', '', _MergeLocNames(Rsp['isp'], Rsp['owner_domain'])]
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
        Rsp = requests.get(Url, headers = Hed, timeout = Options.Timeout).json()['result']

        if Rsp.get('ip') != Ip:
            raise ValueError('Response IP Mismatch')

        return [Rsp['country'].replace('UNKNOWN', ''), Rsp['province'].replace('UNKNOWN', ''), Rsp['city'].replace('UNKNOWN', ''), '', '', _MergeLocNames(Rsp['isp'], Rsp['org']) if Rsp['country'] == '中国' else Rsp['isp'].replace('UNKNOWN', '')]
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_CnSpeed(Ip: str, Options: dict) -> list:
    import json
    import base64
    import requests

    try:
        Url = base64.b64decode('LWh0dHBzOi8vZGxjdjIuY25zcGVlZHRlc3QuY246ODQ0My9kYXRhU2VydmVyL2dldElwTG9jUy5waHA='.encode()).decode()[1:]
        Hed = {
            'Accept'         : '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control'  : 'no-cache',
            'Pragma'         : 'no-cache',
            'User-Agent'     : Options['User-Agent'],
            'X-Forwarded-For': Ip
        }
        Rsp = requests.get(Url, headers = Hed, timeout = Options.Timeout).text.strip().split('|')

        if len(Rsp) < 2 or Rsp[0] != Ip:
            raise ValueError('Response IP Mismatch')

        Rsp = (json.loads(Rsp[1]) + [''] * 5)[:5]
        return Rsp[:4] + ['', Rsp[4]]
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Lecloud(Ip: str, Options: dict) -> list:
    import re
    import base64
    import requests

    try:
        Url = base64.b64decode('LWh0dHA6Ly9wbGF5LmczcHJveHkubGVjbG91ZC5jb20vdm9kL3YyLw=='.encode()).decode()[1:]
        Hed = {
            'Accept'         : '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control'  : 'no-cache',
            'Pragma'         : 'no-cache',
            'User-Agent'     : Options['User-Agent'],
            'X-Forwarded-For': Ip,
            'X-Real-IP'      : Ip,
            'Client-IP'      : Ip
        }
        Rsp = requests.get(Url, headers = Hed, timeout = Options.Timeout).text

        __1 = re.search(r'Your IP:([^\[]+)\[', Rsp)
        __2 = re.search(r'Remote IP:([^\[]+)\[', Rsp)
        if not __1 or not __2 or __1.group(1) != Ip or __2.group(1) != Ip: raise ValueError('Response IP Mismatch')

        __3 = re.search(r'<h3>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/([^<]+)</h3>', Rsp)
        if not __3: raise ValueError('Location Is Empty')
        Rsp = [_.replace('未知运营商', '').replace('未知', '').strip() for _ in (__3.group(1).split('-') + [''] * 4)[:4]]

        return [Rsp[0], Rsp[1], Rsp[2], '', '', Rsp[3]]
    except Exception as Error:
        return [''] * 6


def __QueryIpLocation_Pconline(Ip: str, Options: dict) -> list:
    import re
    import base64
    import requests
    import urllib.parse

    try:
        Url = base64.b64decode('LWh0dHBzOi8vd2hvaXMucGNvbmxpbmUuY29tLmNuL2lwSnNvbi5qc3A/anNvbj10cnVlJmlwPQ=='.encode()).decode()[1:] + urllib.parse.quote(Ip, safe = '')
        Hed = {
            'Accept'         : '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control'  : 'no-cache',
            'Pragma'         : 'no-cache',
            'User-Agent'     : Options['User-Agent'],
            'X-Forwarded-For': Ip,
            'X-Real-IP'      : Ip
        }
        Rsp = requests.get(Url, headers = Hed, timeout = Options.Timeout)
        Rsp.encoding = 'GBK'
        Rsp = Rsp.json()

        if Rsp.get('ip') != Ip:
            raise ValueError('Response IP Mismatch')

        Addr = re.sub(r'\s+', ' ', Rsp.get('addr', '')).strip()
        if Rsp.get('pro') or Rsp.get('city') or Rsp.get('region'):
            Isp = Addr
            for Item in [Rsp.get('pro'), Rsp.get('city'), Rsp.get('region')]:
                Isp = Isp.replace(Item or '', '')
            return ['中国', Rsp.get('pro', ''), Rsp.get('city', ''), Rsp.get('region', ''), '', '中国移动通信集团公司' if Isp.strip() == '移通' else Isp]

        return [Addr, '', '', '', '', '']
    except Exception as Error:
        return [''] * 6
