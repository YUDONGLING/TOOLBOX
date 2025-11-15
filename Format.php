<?php

require_once "Init.php";
require_once "Log.php";

/**
 * Check and Safety the Path, Return the Safety Path.
 */
function SafePath(string $Path, array $Options = null): array {
    $DftOpts = [
        "MaxLength"    => 50,
        "ForceReplace" => []
    ];
    $Options = MergeDictionaries($DftOpts, $Options);

    $Response = [
        "Ec"   => 0,
        "Em"   => "",
        "Path" => ""
    ];

    try {
        foreach ($Options["ForceReplace"] as $_Rule) {
            if (is_array($_Rule) && count($_Rule) == 2) {
                if (is_string($_Rule[0]) && is_string($_Rule[1])) {
                    $Path = str_replace($_Rule[0], $_Rule[1], $Path);
                }
            }
        }
        $Path = preg_replace("/\s+/", " ", preg_replace("/[\\/:*?\"<>|\n]/", " ", $Path));
        $Response["Path"] = trim(substr(ltrim($Path), 0, $Options["MaxLength"]));
    } catch (Exception $Error) {
        $Response["Ec"] = 50000; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    return $Response;
}

/**
 * Convert the Size to Human Readable Format, Support Magic Variables for Storage Unit.
 */
function ConvertSize(int $Size, string $Unit = "B", array $Options = null): array {
    $DftOpts = [
        "Format" => "{{Size}} {{Unit}}",
        "Place_After_Decimal_Point" => 2
    ];
    $Options = MergeDictionaries($DftOpts, $Options);

    $Response = [
        "Ec"     => 0,
        "Em"     => "",
        "Result" => ""
    ];

    $Units   = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
    $Weights = array_combine($Units, range(0, count($Units) - 1));
    $Sizes   = array_fill_keys($Units, -1);

    try {
        if (!is_int($Size) && !is_float($Size)) {
            throw new TypeError("Size Must be Int or Float");
        }
        if ($Size < 0) {
            throw new ValueError("Size Must be Positive");
        }
        if (!in_array($Unit, $Units)) {
            throw new ValueError("Unit Must be in B, KB, MB, GB, TB or PB");
        }
    } catch (Exception $Error) {
        $Response["Ec"] = 50001; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    try {
        $SizeInBytes = $Size * (1024 ** $Weights[$Unit]);

        foreach ($Units as $Unit) {
            $Sizes[$Unit] = $SizeInBytes / (1024 ** $Weights[$Unit]);
        }

        AutoUnit = 'B';
        for ($i = count($Units) - 1; $i >= 1; $i--) {
            $Unit = $Units[$i];
            if ($Sizes[$Unit] >= 1) {
                AutoUnit = $Unit;
                break;
            }
        }
    } catch (Exception $Error) {
        $Response["Ec"] = 50002; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    try {
        $Result = str_replace("{{Size}}", number_format($Sizes[$AutoUnit], $Options["Place_After_Decimal_Point"]), $Options["Format"]);
        $Result = str_replace("{{Unit}}", $AutoUnit, $Result);

        foreach ($Units as $Unit) {
            $Result = str_replace("{{Size:$Unit}}", number_format($Sizes[$Unit], $Options["Place_After_Decimal_Point"]), $Result);
            $Result = str_replace("{{Unit:$Unit}}", $Unit, $Result);
        }

        $Response["Result"] = $Result;
    } catch (Exception $Error) {
        $Response["Ec"] = 50003; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    return $Response;
}

?>