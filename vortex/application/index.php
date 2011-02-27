<!DOCTYPE html>
<?php
//clear a json request variable on index.php 
unset($_REQUEST['json']);
include('vortex.php');
$vortex = get_vortex();
?>
<html>
	<head>
		<style type="text/css">
			body {
				background-image:url('http://peculiarcomics.com/vortex/img/bgtile.jpg');
				text-align: center;
				margin-left: auto;
				margin-right: auto;
			}
			img {
				border: 0 none;
			}
			
			.expose {
				padding-top:0px;
				padding-right:5px;
				padding-bottom:10px;
				padding-left:10px;
				font-style: italic;
				font-size: 24px;
			}
			
			.panel img {
				border:10px solid #ffffff;
			}
			
			.vortex {
				border: 2px solid #ffffff;
				padding: 5px 5px;
				width: 430px;
				font-family:"Times New Roman", Times, serif;
				color: #ffffff;
				font-size: 18px;
				margin-left: auto;
				margin-right: auto;
			}
			
			ul {
				list-style-type: none;
				border-width: 0px;
				padding: 0px 0px 0px 0px;
			}
			
			li {
				display: inline;
			}
			
			hr {
					width: 80%;
			}
		
		</style>
		<script type="text/javascript" src="vortex.js"></script>
		<title>PECULIAR COMICS PRESENTS: The Vortex Experiment 2.0</title>		

</head>
<body>
<div class="vortex">
	<img src = "http://peculiarcomics.com/vortex/img/banner.png" />
	<hr />
	<p class="expose">The Vortex Experiment Version 2 consists of randomly 
	selected black and white images taken from various public domain 
	databases and text taken from select movie taglines.
	</p>
	<hr />
	<!-- style = "padding-top:0px;padding-right:0px;padding-bottom:0px;padding-left:0px;" -->
	<ul>
		<li>
			<a href = "http://peculiarcomics.com/index.html">
			<!-- style = "border:0px" -->
			<img src = "http://peculiarcomics.com/vortex/img/homenav.png" /></a>
		</li>
		<li>
			<!-- style = "border:0px" -->
			<img src = "http://peculiarcomics.com/vortex/img/midnav.png" />
		</li>
		<li>
			<!-- style = "border:0px" -->
			<a onclick=vortex()>
			<img src = "http://peculiarcomics.com/vortex/img/refnav.png" />
			</a>
		</li>
	</ul>
	<div id='0' class='panel'>
		<img src="<?php echo $vortex['panels'][0]['image'];?>" />
		<p><?php echo $vortex['panels'][0]['quote'];?></p>
	</div>
	<div id='1' class='panel'>
		<img src="<?php echo $vortex['panels'][1]['image'];?>" />
		<p><?php echo $vortex['panels'][1]['quote'];?></p>
	</div>
	<div id='2' class='panel'>
		<img src="<?php echo $vortex['panels'][2]['image'];?>" />
		<p><?php echo $vortex['panels'][2]['quote'];?></p>
	</div>
	<a id='fbshare' href="http://www.facebook.com/sharer.php?u=<?php echo generate_url($vortex);?>&t=VortexVersion3">
	<!-- style = "border:0px" -->
	<img src = "http://peculiarcomics.com/vortex/img/fbshare.png" />
	</a>
</div>
</body>
</html>