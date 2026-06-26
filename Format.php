<?php

require_once "Init.php";
require_once "Log.php";

/**
 * Check and Safety the Path, Return the Safety Path.
 */
function SafePath(string $Path, ?array $Options = null): array {
    $DftOpts = [
        "MaxLength"    => 50,
        "ForceReplace" => [],
        "ConvertMacSpecialChars"  => true,
        "NormalizeUnicode"        => true,
        "RemoveUnsafeUnicode"     => true,
        "UnsafeUnicodeCharacters" => "",
        "UnsafeUnicodeRanges"     => [
            [0x02B0, 0x02FF],     // Spacing Modifier Letters
            [0x0E50, 0x0E59],     // Thai digits commonly used as kaomoji eyes
            [0x1760, 0x177F],     // Tagbanwa letters sometimes used as decoration
            [0x1D00, 0x1DBF]      // Phonetic Extensions
        ],
        "UnicodeReplacement"      => " "
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

        if ($Options["ConvertMacSpecialChars"]) {
            // Synology/Samba VFS store Mac-special Characters as CATIA Private-Use Code Points.
            $MacSpecialChars = [
                "\u{F020}" => "\"",
                "\u{F021}" => "*",
                "\u{F022}" => "/",
                "\u{F023}" => ":",
                "\u{F024}" => "<",
                "\u{F025}" => ">",
                "\u{F026}" => "?",
                "\u{F027}" => "\\",
                "\u{F028}" => "|"
            ];
            $Path = str_replace(array_keys($MacSpecialChars), array_values($MacSpecialChars), $Path);
        }

        if ($Options["NormalizeUnicode"] && class_exists("Normalizer")) {
            $_Path = Normalizer::normalize($Path, Normalizer::FORM_KC);
            if ($_Path !== false) {
                $Path = $_Path;
            }
        }

        $Path = str_replace(
            ["\u{FF02}", "\u{FF0A}", "\u{FF0F}", "\u{FF1A}", "\u{FF1C}", "\u{FF1E}", "\u{FF1F}", "\u{FF3C}", "\u{FF5C}"],
            ["\"",       "*",        "/",        ":",        "<",        ">",        "?",        "\\",       "|"],
            $Path
        );

        if ($Options["RemoveUnsafeUnicode"]) {
            $Replacement = is_string($Options["UnicodeReplacement"]) ? $Options["UnicodeReplacement"] : " ";
            if (is_string($Options["UnsafeUnicodeCharacters"]) && $Options["UnsafeUnicodeCharacters"] !== "") {
                $UnsafeUnicodeCharacters = preg_split('//u', $Options["UnsafeUnicodeCharacters"], -1, PREG_SPLIT_NO_EMPTY);
                if (is_array($UnsafeUnicodeCharacters)) {
                    $Path = str_replace($UnsafeUnicodeCharacters, $Replacement, $Path);
                }
            }
            if (is_array($Options["UnsafeUnicodeRanges"])) {
                $Ord = function(string $Char): int {
                    if (function_exists("mb_ord")) {
                        return mb_ord($Char, "UTF-8");
                    }
                    if (class_exists("IntlChar")) {
                        return IntlChar::ord($Char);
                    }

                    $Bytes = unpack("C*", $Char);
                    $First = $Bytes[1];
                    if ($First < 0x80) return $First;
                    if (($First & 0xE0) === 0xC0) return (($First & 0x1F) << 6) | ($Bytes[2] & 0x3F);
                    if (($First & 0xF0) === 0xE0) return (($First & 0x0F) << 12) | (($Bytes[2] & 0x3F) << 6) | ($Bytes[3] & 0x3F);
                    if (($First & 0xF8) === 0xF0) return (($First & 0x07) << 18) | (($Bytes[2] & 0x3F) << 12) | (($Bytes[3] & 0x3F) << 6) | ($Bytes[4] & 0x3F);
                    return $First;
                };
                $Path = preg_replace_callback('/./u', function($Match) use ($Options, $Replacement, $Ord) {
                    $CodePoint = $Ord($Match[0]);
                    foreach ($Options["UnsafeUnicodeRanges"] as $_Range) {
                        if (is_array($_Range) && count($_Range) === 2 && is_int($_Range[0]) && is_int($_Range[1])) {
                            if ($_Range[0] <= $CodePoint && $CodePoint <= $_Range[1]) {
                                return $Replacement;
                            }
                        }
                    }
                    return $Match[0];
                }, $Path);
            }
            $Path = preg_replace('/[\p{Cc}\p{Cs}\p{Co}]/u', $Replacement, $Path);
            $Path = preg_replace('/(?!\x{200D})\p{Cf}/u', $Replacement, $Path);
            $Path = preg_replace('/(?![\x{FE00}-\x{FE0F}\x{E0100}-\x{E01EF}])\p{M}/u', $Replacement, $Path);
            $Path = preg_replace('/(?![\x{0000}-\x{007F}\x{2600}-\x{27BF}\x{1F000}-\x{1FAFF}])\p{S}/u', $Replacement, $Path);
        }

        $Path = preg_replace('/\s+/u', " ", preg_replace('/[\\\/:*?"<>|\r\n\t]/u', " ", $Path));
        $Path = ltrim($Path);
        $Path = function_exists("mb_substr") ? mb_substr($Path, 0, $Options["MaxLength"], "UTF-8") : substr($Path, 0, $Options["MaxLength"]);
        $Response["Path"] = rtrim($Path);
    } catch (Throwable $Error) {
        $Response["Ec"] = 50000; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    return $Response;
}

/**
 * Convert the Size to Human Readable Format, Support Magic Variables for Storage Unit.
 */
function ConvertSize(int | float $Size, string $Unit = "B", ?array $Options = null): array {
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
    } catch (Throwable $Error) {
        $Response["Ec"] = 50001; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    try {
        $SizeInBytes = $Size * (1024 ** $Weights[$Unit]);

        foreach ($Units as $Unit) {
            $Sizes[$Unit] = $SizeInBytes / (1024 ** $Weights[$Unit]);
        }

        $AutoUnit = 'B';
        for ($i = count($Units) - 1; $i >= 1; $i--) {
            $Unit = $Units[$i];
            if ($Sizes[$Unit] >= 1) {
                $AutoUnit = $Unit;
                break;
            }
        }
    } catch (Throwable $Error) {
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
    } catch (Throwable $Error) {
        $Response["Ec"] = 50003; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    return $Response;
}

?>
