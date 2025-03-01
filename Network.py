def QueryDns(Host: str, Type: str = 'A', Global: bool = None, Region: str | dict = None, Options: dict = None) -> str:
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
            'A' :  1, 'NS' : 2 , 'CNAME':  5, 'SOA': 6 , 'PTR':  12,
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

            def MergeIPs(Tar, Src):
                if isinstance(Src, list):
                    for _ in Src: MergeIPs(Tar, _)
                elif isinstance(Src, dict):
                    for _, _IPs in Src.items(): MergeIPs(Tar, _IPs)
                else: Tar.append(Src)

            IP = []; MergeIPs(IP, Pool)
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
