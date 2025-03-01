<?php

require_once "Init.php";
require_once "Log.php";

/**
 * Convert a MD5 Hash to a UUID-like String.
 */
function HashUUID(string $Path_Or_Data, string $Separator = "-"): string {
    if (is_file($Path_Or_Data)) {
        $Md5 = md5_file($Path_Or_Data);
    } else {
        $Md5 = md5($Path_Or_Data);
    }

    return implode($Separator, [
        substr($Md5,  0, 8),
        substr($Md5,  8, 4),
        substr($Md5, 12, 4),
        substr($Md5, 16, 4),
        substr($Md5, 20)
    ]);
}

/**
 * Convert a Timestamp to a UUID-like String.
 */
function TimeUUID(int $Time = null, array $Seed = null, string $Separator = "-"): string {
    $Time = str_pad($Time ?? time(), 10, "0", STR_PAD_LEFT);
    $Seed = $Seed ?? [rand(0, 15), rand(0, 15)];
    $Seed = [$Seed[0] % 16, $Seed[1] % 16];

    $Hexa = "";
    foreach (str_split($Time) as $Char) {
        $Hexa .= sprintf("%03x", ord($Char) * ($Seed[0] % 8 + 1) * ($Seed[1] % 8 + 1));
    }
    $Hexa .= sprintf("%1x", $Seed[0]) . sprintf("%1x", $Seed[1]);

    return implode($Separator, [
        substr($Hexa,  0, 8),
        substr($Hexa,  8, 4),
        substr($Hexa, 12, 4),
        substr($Hexa, 16, 4),
        substr($Hexa, 20)
    ]);
}

/**
 * Sort Files in a Directory by TimeUUID.
 */
function TimeUUID_Sort(string $Path, string $Separator = null): array {
    $Response = [
        "Ec"    => 0,
        "Em"    => "",
        "Files" => []
    ];

    try {
        $Files = scandir($Path);
    } catch (Exception $Error) {
        $Response["Ec"] = 50001; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    try {
        $Metas = [];
        foreach ($Files as $File) {
            $Decoded = TimeUUID_Decode($File, $Separator);
            if ($Decoded["Ec"] == 0) {
                $Metas[] = [
                    "Time" => $Decoded["Time"],
                    "Name" => $File,
                    "Path" => $Path . DIRECTORY_SEPARATOR . $File
                ];
            }
        }
    } catch (Exception $Error) {
        $Response["Ec"] = 50002; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    try {
        usort($Metas, function($a, $b) {
            return $a["Time"] <=> $b["Time"];
        });
        $Response["Files"] = $Metas;
    } catch (Exception $Error) {
        $Response["Ec"] = 50003; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    return $Response;
}

/**
 * Decode a UUID-like String to a Timestamp.
 */
function TimeUUID_Decode(string $UUID, string $Separator = null): array {
    $Response = [
        "Ec"   => 0,
        "Em"   => "",
        "Time" => -1
    ];

    try {
        if ($Separator === null) {
            $Separator_Len = (strlen($UUID) - 32) / 4;
            $Separator     = $Separator_Len > 0 ? substr($UUID, 8, $Separator_Len) : "";
        }
    } catch (Exception $Error) {
        $Response["Ec"] = 50001; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    try {
        $UUID = str_replace($Separator, "", $UUID);
        $Seed = [hexdec($UUID[-2]), hexdec($UUID[-1])];
    } catch (Exception $Error) {
        $Response["Ec"] = 50002; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    try {
        $Time = "";
        for ($i = 0; $i < strlen($UUID) - 2; $i += 3) {
            $Hexa  = hexdec(substr($UUID, $i, 3));
            $Time .= chr($Hexa / (($Seed[0] % 8 + 1) * ($Seed[1] % 8 + 1)));
        }
        $Response["Time"] = (int)$Time;
    } catch (Exception $Error) {
        $Response["Ec"] = 50003; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    return $Response;
}

?>