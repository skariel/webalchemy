var overlay = document.createElement('div');
var overlay_shown = false;
overlay.style.position = 'fixed';
overlay.style.left = '0px';
overlay.style.right = '0px';
overlay.style.top = '0px';
overlay.style.bottom = '0px';
overlay.style.zIndex= 2;
overlay.style.background= 'rgba(0,0,0,0.7)';
overlay.style.textAlign= 'center';
var h1= document.createElement('h1');
h1.textContent='Connection lost. Trying to reconnect...';
h1.style.background='#FFFFFF'
h1.style.display='inline-block';
h1.style.marginTop='30%';
h1.style.padding='25px';
h1.style.boxShadow= '3px 3px 7px #000000';
h1.style.borderRadius= '10px';
overlay.appendChild(h1)