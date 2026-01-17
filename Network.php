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

            function FlattenIPs(&$Tar, $Src) {
                if (is_array($Src)) {
                    foreach ($Src as $Item) {
                        FlattenIPs($Tar, $Item);
                    }
                } else {
                    $Tar[] = $Src;
                }
            }

            $IP = [];
            FlattenIPs($IP, $Pool);
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
    throw new Exception("Not Implemented");
}

?>
