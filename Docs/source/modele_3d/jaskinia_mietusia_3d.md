# Jaskinia Miętusia 3D

<body onload="onload();" >

<script type="text/javascript" >

document.addEventListener('keydown', (e) => {
  e.stopPropagation();
});


function onload () {

	const viewer = new CV2.CaveViewer( "scene", {
	view: {
			shadingMode: CV2.SHADING_SURVEY,			
			box: false,
			HUD: true,
			walls: false,			
			linewidth: 0.2,
			entrances: false,
			entrance_dots: true,			
		}		
	} 
	);

	const ui = new CV2.CaveViewUI( viewer );

	ui.loadCave("../3d_files/mietusia.3d" );	

}
</script>


<div style="padding: 20px">
	<div id="scene"></div>
</div>


</body>