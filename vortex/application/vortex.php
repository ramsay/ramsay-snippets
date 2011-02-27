<?php

function get_quote($x){
	static $quotes;
	if (!isset($quotes)){
		$quotes = file('../public/quotes.txt');
	}
	if (!isset($quotes[$x])) $x = 0;
	return $quotes[$x];
}

function get_vortex($vidStr = '', $max_image=243, $max_quote=184){
	$za = ord('0'); // Zero ascii code offset.
	if (strlen($vidStr) == 18) {
		//decode vid string to a vortex id.
		for($i = 0; $i < 18; $i+=3){
			$vid[$i/3] = (ord($vidStr[$i]) - $za)*100;
			$vid[$i/3] += (ord($vidStr[$i]) - $za)*10;
			$vid[$i/3] += ord($vidStr[$i]) - $za;
		}
	}
	else {
		//Generate a new vortex id
		$vid = array();
		for ($i = 0; $i < 3; $i++) {
			$vid[$i*2+1] = rand(1,$max_quote);
			$vid[$i*2] = rand(1,$max_image);
		}
	}
	$response = array();
	$response['vid'] = join($vid);
	$panels = array();
	for ($i = 0; $i < 3; $i++){
		$panels[$i] = array();
		$panels[$i]['image'] = 'http://www.peculiarcomics.com/vortex/img/'. 
			str_pad($vid[$i*2], 3, '0', STR_PAD_LEFT) . '.jpg';
		$panels[$i]['quote'] = get_quote($vid[$i*2+1]);
	}
	$response['panels'] = $panels;
	return $response;
}

function generate_url($vortex){
	/* The opposite of get_vortex, generates a url for sharing vortex comics.
	 * $vortex - a vortex array object.
	 */
	return "http://www.peculiarcomics.com/vortex/index.html?vid=" . $vortex['vid'];
}

if ($_SERVER['PHP_SELF'] == 'vortex.php'){
	// equivalent to python if __name__ == "__main__"
		
	if (isset($argv)) {
		foreach ($argv as $k=>$v)
		{
			if ($k == 0) continue;
			parse_str($v, $tmp);
			$_REQUEST = array_merge($_REQUEST, $tmp);
		}
	}
	
	if (isset($_REQUEST['json'])) {
		$decoded = json_decode($_REQUEST['json']);
		$vortex = get_vortex($decoded);
		$encoded = json_encode($vortex);
		die($encoded);
	}
}
?>