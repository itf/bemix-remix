<?php

$url =  $_REQUEST['url'];


$encoded = '';
// include GET as well as POST variables; your needs may vary.
foreach($_GET as $name => $value) {
  $encoded .= urlencode($name).'='.urlencode($value).'&';
}
foreach($_POST as $name => $value) {
  $encoded .= urlencode($name).'='.urlencode($value).'&';
}
$encoded = substr($encoded, 0, strlen($encoded)-1);
function getURL($url,$encoded){
	print_r($encoded);
		die();
		$ch = curl_init();
	/**
	* Set the URL of the page or file to download.w
	*/
	curl_setopt($ch, CURLOPT_URL,
	$url);
	/**
	* Ask cURL to return the contents in a variable
	* instead of simply echoing them to the browser.
	*/
	
	curl_setopt($ch, CURLOPT_HEADER, 0);
	
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
	
	curl_setopt($ch, CURLOPT_POST, 1); 
	
	curl_setopt($ch, CURLOPT_POSTFIELDS, $encoded); 
	
	/**
	* Execute the cURL session
	*/
	$contents = curl_exec ($ch);
	/**
	* Close cURL session
	*/
	curl_close ($ch);
	return $contents;
}

echo getURL($url);