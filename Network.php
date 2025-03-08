<?php

require_once "Init.php";
require_once "Log.php";

/**
 * Query the DNS of a Host at Specific Region (Country in the World, or City of China), via HTTP DNS.
 */
function QueryDns(string $Host, string $Type = 'A', bool $Global = null, array $Region = null, array $Options = null): string {
    $DftOpts = [
        'User-Agent' => 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Provider'   => 'https://dns.alidns.com/resolve', // 'https://dns.alidns.com/resolve' By Alibaba Cloud Public DNS
                                                          // 'https://doh.pub/resolve'        By DNSPod Public DNS
                                                          // 'https://dns.google/resolve'     By Google Public DNS
        'Timeout'    => 5
    ];
    $Options = MergeDictionaries($DftOpts, $Options);

    try {
        $Type = [
            'A'  =>  1, 'NS'  =>  2, 'CNAME' =>  5, 'SOA' =>  6, 'PTR' =>  12,
            'MX' => 15, 'TXT' => 16, 'AAAA'  => 28, 'SRV' => 33, 'ANY' => 255
        ][strtoupper($Type)];

        $Host = preg_replace('/^https?:\/\//', '', rtrim($Host, '/'));
    } catch (Exception $Error) {
        return '';
    }

    try {
        if (is_null($Global)) {
            $IP = '';
        } else {
            $FilePath = __DIR__ . '/Extra/' . ($Global ? 'Global_IPs.json' : 'CN_IPs.json');
            $IPs = json_decode(file_get_contents($FilePath), true);

            function FetchIPs($Zone, $IPs) {
                $Zone = explode('.', $Zone);
                $Temp = $IPs;
                while ($Zone) {
                    $Key = array_shift($Zone);
                    if (isset($Temp[$Key])) {
                        $Temp = $Temp[$Key];
                    } else {
                        return [];
                    }
                }
                return $Temp;
            }

            $Pool = [];
            $Region = $Region ? (is_array($Region) ? $Region : [$Region]) : [];
            foreach ($Region as $Rule) {
                if (strpos($Rule, '-') === 0) {
                    FetchIPs(substr($Rule, 1), $IPs);
                } else {
                    $Pool[] = FetchIPs($Rule, $IPs);
                }
            }
            if (empty($Pool)) {
                $Pool = $IPs;
            }

            function MergeIPs(&$Tar, $Src) {
                if (is_array($Src)) {
                    foreach ($Src as $Item) {
                        MergeIPs($Tar, $Item);
                    }
                } else {
                    $Tar[] = $Src;
                }
            }

            $IP = [];
            MergeIPs($IP, $Pool);
            $IP = $IP[array_rand($IP)];
        }
    } catch (Exception $Error) {
        return '';
    }

    try {
        $Url = $Options['Provider'] . "?name=$Host&type=$Type";
        if ($IP) {
            $Url .= "&edns_client_subnet=$IP";
        }
        $Hed = [
            'User-Agent' => $Options['User-Agent']
        ];
        $Rsp = json_decode(file_get_contents($Url, false, stream_context_create([
            'http' => [
                'header'  => "User-Agent: " . $Hed['User-Agent'],
                'timeout' => $Options['Timeout']
            ]
        ])), true);

        if ($Rsp['Status'] != 0) {
            throw new Exception("HTTP DNS Query Failed, Status is {$Rsp['Status']}, Response is " . json_encode($Rsp));
        } else {
            $Recode = array_column(array_filter($Rsp['Answer'], function($Item) use ($Type) {
                return $Item['type'] == $Type;
            }), 'data');
        }
    } catch (Exception $Error) {
        return '';
    }

    return $Recode ? $Recode[array_rand($Recode)] : '';
}

/**
 * Query the Location of an IP Address.
 */
function QueryIpLocation(string $Ip, array $Options = null): string {
    $DftOpts = [
        'User-Agent'  => 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Provider_V4' => 'UaInfo', // Bt, Zx, Ldd, Ipa, Ips, UaInfo
        'Provider_V6' => 'Zx',     // Zx, Ips
        'Timeout'     => 5
    ];
    $Options = MergeDictionaries($DftOpts, $Options);

    $Provider = null;
    if (strpos($Ip, '.') !== false && preg_match('/^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$/', $Ip)) {
        $Provider = $Options['Provider_V4'];
    };
    if (strpos($Ip, ':') !== false && preg_match('/^([\da-fA-F]{1,4}:){6}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^::([\da-fA-F]{1,4}:){0,4}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:):([\da-fA-F]{1,4}:){0,3}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){2}:([\da-fA-F]{1,4}:){0,2}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){3}:([\da-fA-F]{1,4}:){0,1}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){4}:((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$|^([\da-fA-F]{1,4}:){7}[\da-fA-F]{1,4}$|^:((:[\da-fA-F]{1,4}){1,6}|:)$|^[\da-fA-F]{1,4}:((:[\da-fA-F]{1,4}){1,5}|:)$|^([\da-fA-F]{1,4}:){2}((:[\da-fA-F]{1,4}){1,4}|:)$|^([\da-fA-F]{1,4}:){3}((:[\da-fA-F]{1,4}){1,3}|:)$|^([\da-fA-F]{1,4}:){4}((:[\da-fA-F]{1,4}){1,2}|:)$|^([\da-fA-F]{1,4}:){5}:([\da-fA-F]{1,4})?$|^([\da-fA-F]{1,4}:){6}:$/', $Ip)) {
        $Provider = $Options['Provider_V6'];
    };
    if (!in_array($Provider, ['Bt', 'Zx', 'Ldd', 'Ipa', 'Ips', 'UaInfo'])) {
        return '未知 未知';
    }

    $Location = [''] * 6;
    if ($Provider == 'Bt')     $Location = __QueryIpLocation_Bt    ($Ip, $Options);
    if ($Provider == 'Zx')     $Location = __QueryIpLocation_Zx    ($Ip, $Options);
    if ($Provider == 'Ldd')    $Location = __QueryIpLocation_Ldd   ($Ip, $Options);
    if ($Provider == 'Ipa')    $Location = __QueryIpLocation_Ipa   ($Ip, $Options);
    if ($Provider == 'Ips')    $Location = __QueryIpLocation_Ips   ($Ip, $Options);
    if ($Provider == 'UaInfo') $Location = __QueryIpLocation_UaInfo($Ip, $Options);
    if ($Location == [''] * 6) return '未知 未知';

    $Location = array_map(function($_) { return strval('' === $_ ? '' : $_); }, $Location);
    if ($Location[0] == '中国') {
        // 省份 Province
        $Location[1] = preg_replace('/(维吾尔自治区|回族自治区|壮族自治区|自治区|特别行政区|省|市)$/', '', $Location[1]);
        $Location[1] = ltrim($Location[1], '中国');

        // 城市 City
        $Location[2] = preg_replace('/(布依族苗族自治州|傣族景颇族自治州|哈尼族彝族自治州|蒙古族藏族自治州|土家族苗族自治州|柯尔克孜自治州|苗族侗族自治州|藏族羌族自治州|壮族苗族自治州|朝鲜族自治州|哈萨克自治州|傈僳族自治州|白族自治州|傣族自治州|回族自治州|蒙古自治州|彝族自治州|藏族自治州|地区|新区|盟|市|区)$/', '', $Location[2]);
        $Location[2] = in_array($Location[1], ['北京', '上海', '天津', '重庆', '香港', '澳门', '台湾']) && $Location[1] == $Location[2] ? '' : $Location[2];

        // 区县 Area
        $Location[3] = (strlen($Location[3]) > 2 && !preg_match('/(管理区|回族区|聚集区|开发区|示范区|食品区|实验区|自治县|矿区|新区|园区|族区)$/', $Location[3])) ? preg_replace('/(管理区管委会|行政委员会|风景名胜区|林区|市|县|区)$/', '', $Location[3]) : $Location[3];

        // 网络 Network Provider
        $___Provider = strtoupper($Location[5]);
        if (strpos($___Provider, '广电') !== false || strpos($___Provider, 'CABLE'  ) !== false || strpos($___Provider, 'BROADCAST') !== false) $Location[5] = '广电';
        if (strpos($___Provider, '电信') !== false || strpos($___Provider, 'TELECOM') !== false || strpos($___Provider, 'CHINANET' ) !== false) $Location[5] = '电信';
        if (strpos($___Provider, '联通') !== false || strpos($___Provider, 'UNICOM' ) !== false || strpos($___Provider, 'CHINA169' ) !== false) $Location[5] = '联通';
        if (strpos($___Provider, '移动') !== false || strpos($___Provider, 'MOBILE' ) !== false || strpos($___Provider, 'CMNET'    ) !== false) $Location[5] = '移动';
        if (strpos($___Provider, '铁通') !== false || strpos($___Provider, 'TIETONG') !== false || strpos($___Provider, 'RAILWAT'  ) !== false) $Location[5] = '铁通';
        if (strpos($___Provider, '教育') !== false || strpos($___Provider, 'CERNET' ) !== false || strpos($___Provider, 'EDUCATION') !== false) $Location[5] = '教育网';
    }

    return trim(preg_replace('/\s+/', ' ', implode(' ', $Location)));
}

function __QueryIpLocation_Bt(string $Ip, array $Options): array {
    try {
        $Url = substr(base64_decode('LWh0dHBzOi8vd3d3LmJ0LmNuL2FwaS9wYW5lbC9nZXRfaXBfaW5mbz9pcD0='), 1) . $Ip;
        $Hed = [
            'User-Agent' => 'BT-Panel'
        ];
        $Rsp = json_decode(file_get_contents($Url, false, stream_context_create([
            'http' => [
                'header'  => implode("\r\n", array_map(function($k, $v) { return "$k: $v"; }, array_keys($Hed), $Hed)),
                'timeout' => $Options['Timeout']
            ]
        ])), true)[$Ip];

        return [$Rsp['country'], $Rsp['province'], $Rsp['city'], $Rsp['region'], '', $Rsp['carrier']];
    } catch (Exception $Error) {
        return [''] * 6;
    }
}

function __QueryIpLocation_Zx(string $Ip, array $Options): array {
    try {
        $Url = substr(base64_decode('LWh0dHBzOi8vaXAuenhpbmMub3JnL2FwaS5waHA/dHlwZT1qc29uJmlwPQ=='), 1) . $Ip;
        $Hed = [
            'Accept'           => '*/*',
            'Accept-Language'  => 'zh-CN,zh;q=0.9',
            'Cache-Control'    => 'no-cache',
            'DNT'              => '1',
            'Pragma'           => 'no-cache',
            'Priority'         => 'u=1, i',
            'Referer'          => substr(base64_decode('LWh0dHBzOi8vaXAuenhpbmMub3JnL2lwcXVlcnkv'), 1),
            'User-Agent'       => $Options['User-Agent'],
            'X-Requested-With' => 'XMLHttpRequest'
        ];
        $Rsp = json_decode(file_get_contents($Url, false, stream_context_create([
            'http' => [
                'header'  => implode("\r\n", array_map(function($k, $v) { return "$k: $v"; }, array_keys($Hed), $Hed)),
                'timeout' => $Options['Timeout']
            ]
        ])), true)['data'];

        return array_merge(array_slice(array_merge(explode(' ', preg_replace('/\s+/', ' ', str_replace(['–', "\t"], ' ', $Rsp['country']))), [''] * 5), 0, 5), [$Rsp['local']]);
    } catch (Exception $Error) {
        return [''] * 6;
    }
}

function __QueryIpLocation_Ldd(string $Ip, array $Options): array {
    try {
        $Url = substr(base64_decode('LWh0dHBzOi8vb3BlbmFwaS5sZGRnby5uZXQvYmFzZS9nc2VydmljZS9hcGkvdjEvR2V0SXBBZGRyZXNz'.encode()), 1);
        $Hed = [
            'Accept'          => '*/*',
            'Accept-Language' => 'zh-CN,zh;q=0.9',
            'Cache-Control'   => 'no-cache',
            'Content-Type'    => 'application/json;charset=UTF-8',
            'DNT'             => '1',
            'Origin'          => substr(base64_decode('LWh0dHBzOi8vd3d3LmxkZGdvLm5ldA=='.encode()), 1),
            'Pragma'          => 'no-cache',
            'Priority'        => 'u=1, i',
            'Referer'         => substr(base64_decode('LWh0dHBzOi8vd3d3LmxkZGdvLm5ldC8='.encode()), 1),
            'Sec-Fetch-Dest'  => 'empty',
            'Sec-Fetch-Mode'  => 'cors',
            'Sec-Fetch-Site'  => 'same-site',
            'User-Agent'      => $Options['User-Agent']
        ];
        $Dat = [
            'ip' => $Ip
        ];
        $Rsp = json_decode(file_get_contents($Url, false, stream_context_create([
            'http' => [
                'method'  => 'POST',
                'header'  => implode("\r\n", array_map(function($k, $v) { return "$k: $v"; }, array_keys($Hed), $Hed)),
                'content' => json_encode($Dat),
                'timeout' => $Options['Timeout']
            ]
        ])), true)['data'];

        return [$Rsp['nation'], $Rsp['province'], $Rsp['city'], $Rsp['area'], $Rsp['address'], $Rsp['type']];
    } catch (Exception $Error) {
        return [''] * 6;
    }
}

function __QueryIpLocation_Ipa(string $Ip, array $Options): array {
    try {
        $Url = substr(base64_decode('LWh0dHBzOi8vZGVtby5pcC1hcGkuY29tL2pzb24v'), 1) . $Ip . substr(base64_decode('LT9maWVsZHM9Y291bnRyeSxyZWdpb25OYW1lLGNpdHksaXNwLGFzLG9yZyZsYW5nPXpoLUNO'), 1);
        $Hed = [
            'Accept'          => '*/*',
            'Accept-Language' => 'zh-CN,zh;q=0.9',
            'Cache-Control'   => 'no-cache',
            'Connection'      => 'keep-alive',
            'DNT'             => '1',
            'Origin'          => substr(base64_decode('LWh0dHBzOi8vaXAtYXBpLmNvbQ=='), 1),
            'Pragma'          => 'no-cache',
            'Referer'         => substr(base64_decode('LWh0dHBzOi8vaXAtYXBpLmNvbS8='), 1),
            'Sec-Fetch-Dest'  => 'empty',
            'Sec-Fetch-Mode'  => 'cors',
            'Sec-Fetch-Site'  => 'same-site',
            'User-Agent'      => $Options['User-Agent']
        ];
        $Rsp = json_decode(file_get_contents($Url, false, stream_context_create([
            'http' => [
                'header'  => implode("\r\n", array_map(function($k, $v) { return "$k: $v"; }, array_keys($Hed), $Hed)),
                'timeout' => $Options['Timeout']
            ]
        ])), true);

        return [$Rsp['country'], $Rsp['regionName'], $Rsp['city'], '', '', $Rsp['country'] == '中国' ? $Rsp['isp'] . $Rsp['as'] . $Rsp['org'] : $Rsp['isp']];
    } catch (Exception $Error) {
        return [''] * 6;
    }
}

function __QueryIpLocation_Ips(string $Ip, array $Options): array {
    try {
        $Url = substr(base64_decode('LWh0dHBzOi8vd3d3Lmlwc2h1ZGkuY29tLw=='), 1) . $Ip . substr(base64_decode('LS5odG0='.encode()), 1);
        $Hed = [
            'Accept'                   => 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language'          => 'zh-CN,zh;q=0.9',
            'Cache-Control'            => 'no-cache',
            'Connection'               => 'keep-alive',
            'DNT'                      => '1',
            'Pragma'                   => 'no-cache',
            'Sec-Fetch-Dest'           => 'document',
            'Sec-Fetch-Mode'           => 'navigate',
            'Sec-Fetch-Site'           => 'none',
            'Sec-Fetch-User'           => '?1',
            'Upgrade-Insecure-Requests'=> '1',
            'User-Agent'               => $Options['User-Agent']
        ];
        $Rsp = file_get_contents($Url, false, stream_context_create([
            'http' => [
                'header'  => implode("\r\n", array_map(function($k, $v) { return "$k: $v"; }, array_keys($Hed), $Hed)),
                'timeout' => $Options['Timeout']
            ]
        ]));

        preg_match('/<td class="th">归属地<\/td>[\s\S]*?<span>(.*?)<\/span>/', $Rsp, $match1);
        $__1 = isset($match1[1]) ? preg_replace('/<a.*?>(.*?)<\/a>|\s+/', function($m) { return $m[1] ?? ' '; }, $match1[1]) : '';
        preg_match('/<td class="th">运营商<\/td>[\s\S]*?<span>(.*?)<\/span>/', $Rsp, $match2);
        $__2 = $match2[1] ?? '';

        return array_merge(array_slice(array_merge(explode(' ', preg_replace('/\s+/', ' ', $__1)), [''] * 5), 0, 5), [$__2]);
    } catch (Exception $Error) {
        return [''] * 6;
    }
}

function __QueryIpLocation_UaInfo(string $Ip, array $Options): array {
    try {
        $Url = substr(base64_decode('LWh0dHBzOi8vaXAudXNlcmFnZW50aW5mby5jb20vanNvbnA/aXA9'), 1) . $Ip;
        $Hed = [
            'User-Agent' => $Options['User-Agent']
        ];
        $Rsp = json_decode(rtrim(ltrim(file_get_contents($Url, false, stream_context_create([
            'http' => [
                'header'  => implode("\r\n", array_map(function($k, $v) { return "$k: $v"; }, array_keys($Hed), $Hed)),
                'timeout' => $Options['Timeout']
            ]
        ])), 'callback('), ');'), true);

        return [$Rsp['country'], $Rsp['province'], $Rsp['city'], $Rsp['area'], '', $Rsp['isp']];
    } catch (Exception $Error) {
        return [''] * 6;
    }
}

?>
