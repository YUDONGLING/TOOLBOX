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
        foreach ($Options["ForceReplace"] as $Rule) {
            if (count($Rule) == 2) {
                $Path = str_replace($Rule[0], $Rule[1], $Path);
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

    $Units   = ["B",       "KB",       "MB",       "GB",       "TB",       "PB"      ];
    $Weights = ["B" =>  0, "KB" =>  1, "MB" =>  2, "GB" =>  3, "TB" =>  4, "PB" =>  5];
    $Sizes   = ["B" => -1, "KB" => -1, "MB" => -1, "GB" => -1, "TB" => -1, "PB" => -1];

    try {
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

        $AutoUnit = end(array_filter($Units, function($Unit) use ($Sizes) {
            return $Sizes[$Unit] >= 1;
        }));
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