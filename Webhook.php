<?php

require_once "Init.php";
require_once "Log.php";

/**
 * Send Message to Lark Chat Group.
 */
function Lark(string $Token, string $Topic = "", array $Message = null): array {
    throw new Exception("Not Implemented");
}

/**
 * Send Message to Slack Chat Group.
 */
function Slack(string $Token, string $Topic = "", array $Message = null): array {
    throw new Exception("Not Implemented");
}

/**
 * Send Message to Enterprise WeChat Chat Group. `Token` Should Likes `{{ACCESS_TOKEN}}|{{CHAT_ID}}`.
 */
function WeChat(string $Token, string $Topic = "", array $Message = null): array {
    throw new Exception("Not Implemented");
}

/**
 * Send Message to DingTalk Chat Group.
 */
function DingTalk(string $Token, string $Topic = "", array $Message = null): array {
    $Response = [
        "Ec" => 0,
        "Em" => ""
    ];

    if ($Message === null) { $Message = []; }

    try {
        $MessageBody = "<font color=#6A65FF>**" . $Topic . "**</font> \n\n " . date("Y-m-d H:i:s") . " \n\n";

        foreach ($Message as $Item) {
            if (empty($Item["Title"])) {
                $MessageBody .= " --- \n\n ";
            } else {
                $Color = strtoupper($Item["Color"] ?? "UNKNOWN");
                if (strpos($Color, "#") !== 0 || strlen($Color) != 7) {
                    $Color = [
                        "PURPLE" => "#6A65FF",
                        "RED"    => "#FF6666",
                        "GREEN"  => "#92D050",
                        "BLUE"   => "#76CCFF"
                    ][$Color]    ?? "#76CCFF";
                }
                $MessageBody .= " --- \n\n <font color=" . $Color . ">**" . $Item["Title"] . "**</font> \n\n ";
            }
            $MessageBody .= implode(" \n\n ", $Item["Text"] ?? []) . " \n\n ";
        }

        $MessageBody .= "<font color=#6A65FF>" . $Topic . "</font>";
    } catch (Exception $Error) {
        $Response["Ec"] = 50001; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    try {
        $Url = "https://oapi.dingtalk.com/robot/send?access_token=" . str_replace("https://oapi.dingtalk.com/robot/send?access_token=", "", str_replace("http://oapi.dingtalk.com/robot/send?access_token=", "", $Token));
        $Dat = [
            "msgtype"   => "markdown",
            "markdown"  => [
                "title" => $Topic,
                "text"  => $MessageBody
            ]
        ];
        $Rsp = json_decode(file_get_contents($Url, false, stream_context_create([
            "http" => [
                "method"  => "POST",
                "header"  => "content-type: application/json",
                "content" => json_encode($Dat),
                "timeout" => 10
            ]
        ])), true);

        if (($Rsp["errcode"] ?? -1) !== 0) {
            throw new Exception(($Rsp["errcode"] ?? "Unknown") . "-" . ($Rsp["errmsg"] ?? "Unknown"));
        }
    } catch (Exception $Error) {
        $Response["Ec"] = 50002; $Response["Em"] = MakeErrorMessage($Error); return $Response;
    }

    return $Response;
}

/**
 * Send Message via Telegram Bot.
 */
function Telegram(string $Token, string $Topic = "", array $Message = null): array {
    throw new Exception("Not Implemented");
}

/**
 * Send Message via SeverChan.
 */
function SeverChan(string $Token, string $Topic = "", array $Message = null): array {
    throw new Exception("Not Implemented");
}

?>