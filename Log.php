<?php

/**
 * Make Log File with Content, Support Magic Variables for Path.
 *
 * Table of Magic Variables:
 * Year         `{{YYYY}}`|`{{YY}}` ; Month            `{{MM}}`  ; Day         `{{DD}}` ;
 * Hour         `{{HH}}`            ; Minute           `{{MI}}`  ; Second      `{{SS}}` ;
 * Time Zone    `{{TZ}}`            ; Time Zone String `{{TZS}}` .
 */
function MakeLog(string $Content, string $Path = "Log/{{YYYY}}-{{MM}}-{{DD}}.txt"): array {
    $Response = [
        "Ec"   => 0,
        "Em"   => "",
        "Path" => ""
    ];

    $TimeConst = time();

    $Path = str_replace("{{YYYY}}", date("Y", $TimeConst), $Path);  // 年, Eg: 2021
    $Path = str_replace("{{YY}}"  , date("y", $TimeConst), $Path);  // 年, Eg: 21
    $Path = str_replace("{{MM}}"  , date("m", $TimeConst), $Path);  // 月, Eg: 01
    $Path = str_replace("{{DD}}"  , date("d", $TimeConst), $Path);  // 日, Eg: 01
    $Path = str_replace("{{HH}}"  , date("H", $TimeConst), $Path);  // 时, Eg: 00
    $Path = str_replace("{{MI}}"  , date("i", $TimeConst), $Path);  // 分, Eg: 00
    $Path = str_replace("{{SS}}"  , date("s", $TimeConst), $Path);  // 秒, Eg: 00
    $Path = str_replace("{{TZ}}"  , date("O", $TimeConst), $Path);  // 时区, Eg: +0800
    $Path = str_replace("{{TZS}}" , date("T", $TimeConst), $Path);  // 时区, Eg: CST

    try {
        if (dirname($Path) && !file_exists(dirname($Path))) {
            mkdir(dirname($Path), 0777, true);
        }
    } catch (Exception $Error) {
        $Response["Ec"] = 50001; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    try {
        $Fp = fopen($Path, "a");
        if ($Fp === false) {
            throw new Exception("Unable To Open File: $Path");
        }
        if (flock($Fp, LOCK_EX)) {
            fwrite($Fp, sprintf("[%s] %s\n", date("Y-m-d H:i:s", $TimeConst), $Content));
            fflush($Fp);
            flock($Fp, LOCK_UN);
        } else {
            throw new Exception("Unable To Lock File: $Path");
        }
        fclose($Fp);
        $Response["Path"] = $Path;
    } catch (Exception $Error) {
        $Response["Ec"] = 50002; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    return $Response;
}

/**
 * Make Error Message, Include File, Line Number and Function Name, for Debugging.
 */
function MakeErrorMessage(Exception $Error): string {
    if ($Error->getFile() && $Error->getLine()) {
        $Modu = basename($Error->getFile());
        $Func = "Function <" . $Error->getTrace()[0]["function"] . ">";
        $Line = $Error->getLine();
    } else {
        $Modu = "N/A";
        $Func = "N/A";
        $Line = "N/A";
    }

    if (get_class($Error)) {
        $Type = get_class($Error);
    } else {
        $Type = "Error";
    }

    return sprintf("File \"%s\", Line %s, in %s @%s: %s.", $Modu, $Line, $Func, $Type, ucwords(rtrim($Error->getMessage(), ".")));
}

?>