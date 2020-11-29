var camera, controls, scene, renderer, tilemap_mesh, raycaster, mouse, grid_helper;


function render(){
	requestAnimationFrame( render );
	renderer.render( scene, camera );
	controls.update();
}


function onWindowResize() {
	windowHalfX = window.innerWidth / 2;
	windowHalfY = window.innerHeight / 2;
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize( window.innerWidth, window.innerHeight );
}


async function display_tilemap() {
	//Load buffer arrays from Python backend
	var geometry = await eel.get_tilemap_geometry()();
	console.log(geometry)
	//Create THREE js geometry based on those arrays
	var tilemap_geometry = new THREE.BufferGeometry();
	var vertices = Float32Array.from(geometry['vertices']);
	var normals = Float32Array.from(geometry['normals']);
	var colors = Float32Array.from(geometry['colors']);
	tilemap_geometry.setAttribute( 'position', new THREE.BufferAttribute( vertices, 3 ) );
	tilemap_geometry.setAttribute( 'normal', new THREE.BufferAttribute( normals, 3 ) );
	tilemap_geometry.setAttribute( 'color', new THREE.BufferAttribute( colors, 3 ) );
	tilemap_geometry.computeVertexNormals();
	//Adding material
	var material = new THREE.MeshPhongMaterial({ vertexColors: THREE.VertexColors });
	//Replacing the displayed mesh
	scene.remove( tilemap_mesh );
    tilemap_mesh = new THREE.Mesh( tilemap_geometry, material );
	scene.add( tilemap_mesh );
}


init = function(){
	//Initializing the 3D scene
	camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
	camera.position.x=20;
	camera.position.y=20;
	camera.position.z=20;
	
	renderer = new THREE.WebGLRenderer({antialias: true, alpha: true});
	renderer.setClearColor( 0xffffff, 0 );
	renderer.setSize( window.innerWidth, window.innerHeight);
	document.body.appendChild(renderer.domElement);

	controls = new THREE.OrbitControls( camera, renderer.domElement );
	controls.dynamicDampingFactor = 0.2
	controls.minDistance = 1.5

	scene = new THREE.Scene();

	raycaster = new THREE.Raycaster();
	mouse = new THREE.Vector2();
	
	var directionalLight = new THREE.DirectionalLight( 0xffffff, 1 );
	directionalLight.position.set(20, 10, 10);
	scene.add( directionalLight );

	var light = new THREE.AmbientLight( 0x999999 ); // soft white light
	scene.add( light );

	grid_helper = new THREE.InfiniteGridHelper( 1, 10, new THREE.Color(0xa3b4b4), 100);
	scene.add( grid_helper );

	render();

	window.addEventListener( 'resize', onWindowResize, false );
}

init();


