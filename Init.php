<?php

/**
 * Call a Function Asynchronously.
 * Return an `Concurrent.Future` Object, with Customized Method `waitResult()` to Close the ThreadPoolExecutor and Return the Result.
 */
function AsyncCall(callable $Function, ...$Args): object {
    throw new Exception("Not Implemented");
}

/**
 * Merge two Dictionaries Recursively.
 */
function MergeDictionaries(array $Base, array $Override): array {
    if (!is_array($Base)) {
        throw new TypeError("Base Must Be A Type Of Dictionary");
    }
    if (!is_array($Override)) {
        return $Base; # throw new TypeError("Override Must Be A Type Of Dictionary");
    }

    $Cfg = $Base;

    foreach ($Override as $_Key => $_Value) {
        if (array_key_exists($_Key, $Cfg)) {
            if (is_array($Cfg[$_Key]) && is_array($_Value)) {
                $Cfg[$_Key] = MergeDictionaries($Cfg[$_Key], $_Value);
            } else {
                $Cfg[$_Key] = $_Value;
            }
        } else {
            $Cfg[$_Key] = $_Value;
        }
    }

    return $Cfg;
}

/**
 * Read Configuration from a JSON File.
 */
function ReadConfig(string $Path = "ExeConfig.json"): array {
    if (file_exists($Path)) {
        $Fp = fopen($Path, "r");
        if ($Fp === false) {
            throw new Exception("Unable To Open File: $Path");
        }
        if (flock($Fp, LOCK_SH)) {
            $Content = "";
            while (!feof($Fp)) {
                $Content .= fread($Fp, 8192);
            }
            flock($Fp, LOCK_UN);
        } else {
            throw new Exception("Unable To Lock File: $Path");
        }
        fclose($Fp);
        $Data = json_decode($Content, true);
        if ($Data === null && json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception("JSON Decode Error: " . json_last_error_msg());
        }
        return $Data;
    }
    throw new Exception("File Does Not Exist: $Path");
}

/**
 * Encrypt Configuration and Save to a JSON File.
 */
function EncryptConfig(string $Path = "ExeConfig.json"): void {
    throw new Exception("Not Implemented"); # return SetConfig([], $Path);
}

/**
 * Write Configuration to a JSON file.
 * 
 * Use `Merge = true` to Merge the Configuration with Existing Config File.
 * Use `Force = true` to Overwrite the Existing Config File (if Merge is Disabled).
 */
function SetConfig(array $Cfg, string $Path = "ExeConfig.json", bool $Merge = true, bool $Force = false): void {
    if (file_exists($Path)) {
        if ($Merge) {
            $Cfg = MergeDictionaries(ReadConfig($Path), $Cfg);
        } elseif (!$Force) {
            throw new Exception("File Already Exists. Add Force = True to Overwrite");
        }
    } else {
        if (dirname($Path) && !file_exists(dirname($Path))) {
            mkdir(dirname($Path), 0777, true);
        }
    }

    $Content = json_encode($Cfg, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    $Fp = fopen($Path, "w");
    if ($Fp === false) {
        throw new Exception("Unable To Open File: $Path");
    }
    if (flock($Fp, LOCK_EX)) {
        fwrite($Fp, $Content);
        fflush($Fp);
        flock($Fp, LOCK_UN);
    } else {
        throw new Exception("Unable To Lock File: $Path");
    }
    fclose($Fp);
}

/**
 * Decrypt Environment Variable from a JSON File.
 */
function ReadEnvironVar(string $Path = "EnvironVariable.json"): array {
    function __Decrypt__($Data, $Fernet) {
        if (is_string($Data)) {
            return $Fernet->decrypt($Data);
        } elseif (is_array($Data)) {
            foreach ($Data as $Key => $Value) {
                if ($Key === "AesKey" || $Key === "Type") continue;
                $Data[$Key] = __Decrypt__($Value, $Fernet);
            }
        }
        return $Data;
    }

    $Root = pathinfo($Path, PATHINFO_FILENAME);
    $Extension = pathinfo($Path, PATHINFO_EXTENSION);
    $RawEnvPath = (substr($Root, -4) === "_AES" ? substr($Root, 0, -4) : $Root) . "." . $Extension;
    $AesEnvPath = (substr($Root, -4) !== "_AES" ? $Root . "_AES" : $Root) . "." . $Extension;

    if (file_exists($RawEnvPath)) {
        return ReadConfig($RawEnvPath);
    }

    if (file_exists($AesEnvPath)) {
        $Fernet = new \phpseclib3\Crypt\AES("cbc");
        $AesKey = getenv("AES_KEY");
        if ($AesKey === false) {
            throw new Exception("AES_KEY Environment Variable Not Set");
        }
        $Fernet->setKey(hex2bin($AesKey));
        return __Decrypt__(ReadConfig($AesEnvPath), $Fernet);
    }
    throw new Exception("File Does Not Exist: $Path");
}

/**
 * Encrypt Environment Variable and Save to a JSON File.
 */
function EncryptEnvironVar(string $Path = "EnvironVariable.json"): void {
    SetEnvironVar([], $Path);
}

/**
 * Write Environment Variable to a JSON File.
 * 
 * Use `Merge = true` to Merge the Environment Variable with Existing File.
 * Use `Force = true` to Overwrite the Existing File (if Merge is Disabled).
 */
function SetEnvironVar(array $Env, string $Path = "EnvironVariable.json", bool $Merge = true, bool $Force = false): void {
    function __Encrypt__($Data, $Fernet) {
        if (is_string($Data)) {
            return $Fernet->encrypt($Data);
        } elseif (is_array($Data)) {
            foreach ($Data as $Key => $Value) {
                if ($Key === "AesKey" || $Key === "Type") continue;
                $Data[$Key] = __Encrypt__($Value, $Fernet);
            }
        }
        return $Data;
    }

    $Root = pathinfo($Path, PATHINFO_FILENAME);
    $Extension = pathinfo($Path, PATHINFO_EXTENSION);
    $RawEnvPath = (substr($Root, -4) === "_AES" ? substr($Root, 0, -4) : $Root) . "." . $Extension;
    $AesEnvPath = (substr($Root, -4) !== "_AES" ? $Root . "_AES" : $Root) . "." . $Extension;

    if (file_exists($RawEnvPath)) {
        if ($Merge) {
            $Env = MergeDictionaries(ReadConfig($RawEnvPath), $Env);
        } elseif (!$Force) {
            throw new Exception("File Already Exists. Add Force = True to Overwrite");
        }
    }

    $Fernet = new \phpseclib3\Crypt\AES("cbc");
    if (!isset($Env["AesKey"])) {
        $AesKey = bin2hex(random_bytes(16));
        $Env["AesKey"] = $AesKey;
    } else {
        $AesKey = $Env["AesKey"];
    }
    $Fernet->setKey(hex2bin($AesKey));

    SetConfig($Env, $RawEnvPath, false, true);
    SetConfig(__Encrypt__($Env, $Fernet), $AesEnvPath, false, true);
}

?>