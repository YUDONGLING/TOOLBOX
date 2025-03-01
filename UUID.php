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

?>