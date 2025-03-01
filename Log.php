<?php

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