/*
Vortex V2 - This is my version of the Vortex V2 script refactored and with the capability
of being shared on facebook.
*/

function inject_vortex(vortex){
	// This edits the html objects on the fly to create new comics.
	for(i=0; i < 3; i++){
		panel = document.getEletmentbyId(''+i);
		panel.img.src = vortex['panels'][i]['image'];
		panel.p.innerHTML = vortex['panels'][i]['quote'];
	}
	
	// Update FaceBook share link.
	document.getElementById('fbshare').href='http://www.facebook.com/sharer.php?u='
		'http://peculiarcomics.com/vortex/index.php' + 
		vortex['vid'] +
		+ '&t=Peculiar Comics Vortex Experiment 3';
}
function vortex(){
	//A limited vortex function that runs a simple ajax call to vortex.php.
	if (window.XMLHttpRequest){// code for IE7+, Firefox, Chrome, Opera, Safari
		xmlhttp=new XMLHttpRequest();
	}
	else {// code for IE6, IE5
		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
	}
	xmlhttp.onreadystatechange=function()
	{
		if (xmlhttp.readyState==4 && xmlhttp.status==200)
		{
			inject_vortex(xmlhttp.responseText);
		}
	}
	xmlhttp.open("GET","vortex.php?q="+str,true);
	xmlhttp.send();
}

