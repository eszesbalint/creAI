
var camera, controls, scene, renderer, tilemap_meshes, raycaster, mouse, cursor3D, grid_helper;



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


eel.expose(addBoxes);
function addBoxes(positions) {
	scene.remove( tilemap_mesh );
	var tilemap_geometry = new THREE.Geometry();
	for (var i = 0; i < positions.length; i++) {
		var geometry = new THREE.BoxGeometry( 1, 1, 1 );
		var material = new THREE.MeshStandardMaterial( {color: 0x00ff00} );
		var cube = new THREE.Mesh( geometry, material );
		cube.position.set(positions[i][0]+0.5, positions[i][1]+0.5, positions[i][2]+0.5);
		cube.updateMatrix();
    	tilemap_geometry.merge(cube.geometry, cube.matrix);
    }
    var material = new THREE.MeshNormalMaterial();
    tilemap_mesh = new THREE.Mesh( tilemap_geometry, material );
	scene.add( tilemap_mesh );
}

eel.expose(add_tilemap);
function add_tilemap(id, vertices, normals, colors) {
	console.log(vertices)
	scene.remove( tilemap_mesh );
	var tilemap_geometry = new THREE.BufferGeometry();
	var vertices = Float32Array.from(vertices);
	var normals = Float32Array.from(vertices);
	var colors = Float32Array.from(colors);
	tilemap_geometry.setAttribute( 'position', new THREE.BufferAttribute( vertices, 3 ) );
	tilemap_geometry.setAttribute( 'normal', new THREE.BufferAttribute( normals, 3 ) );
	tilemap_geometry.setAttribute( 'color', new THREE.BufferAttribute( colors, 3 ) );
	tilemap_geometry.computeVertexNormals();
    var material = new THREE.MeshPhongMaterial({ vertexColors: THREE.VertexColors });
    tilemap_mesh = new THREE.Mesh( tilemap_geometry, material );
    tilemap_mesh.name = id;
    tilemap_meshes[id] = tilemap_mesh;
	//scene.add( tilemap_meshes[id] );
}

eel.expose(remove_tilemap);
function remove_tilemap(id) {
	if(id in tilemap_meshes) {
		delete tilemap_meshes[id];
		scene.remove( scene.getObjectByName(id + '_helper') );
		scene.remove( scene.getObjectByName(id) );
	}
}


eel.expose(show_tilemap);
function show_tilemap(id) {
	if(id in tilemap_meshes) {
		var box = new THREE.BoxHelper( tilemap_meshes[id], 0xfcba03 );
		box.name = id + '_helper';
		scene.add( box );
		scene.add(tilemap_meshes[id]);
	}
}

eel.expose(hide_tilemap);
function hide_tilemap(id) {
	if(id in tilemap_meshes) {
		scene.remove( scene.getObjectByName(id + '_helper') );
        scene.remove( scene.getObjectByName(id) );
	}
}



function onMouseMove( event ) {
	mouse.x = ( event.clientX / renderer.domElement.clientWidth ) * 2 - 1;
	mouse.y = - ( event.clientY / renderer.domElement.clientHeight ) * 2 + 1;
	raycaster.setFromCamera( mouse, camera );
	// See if the ray from the camera into the world hits one of our meshes
	var intersects = new THREE.Vector3();
	raycaster.ray.intersectPlane( new THREE.Plane( new THREE.Vector3( 0, 1, 0 ), 0 ), intersects);
	// Toggle rotation bool for meshes that we clicked

	cursor3D.position.copy(intersects);
	//cursor3D.updateMatrix();


}

init = function(){
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
	//controls.addEventListener('change', render);
	
	scene = new THREE.Scene();
	//scene.background = new THREE.Color( 0x4d4646 );


	raycaster = new THREE.Raycaster();
	mouse = new THREE.Vector2();
	

	var directionalLight = new THREE.DirectionalLight( 0xffffff, 1 );
	directionalLight.position.set(20, 10, 10);
	scene.add( directionalLight );

	var light = new THREE.AmbientLight( 0x999999 ); // soft white light
	scene.add( light );
	//addGridToScene();

	grid_helper = new THREE.InfiniteGridHelper( 1, 10, new THREE.Color(0x5F6369), 500);
	scene.add( grid_helper );

	var tilemap_geometry = new THREE.Geometry();
    var material = new THREE.MeshStandardMaterial( {color: 0x00ff00} );
    tilemap_mesh = new THREE.Mesh( tilemap_geometry, material );
    scene.add( tilemap_mesh );


    //CURSOR
    var cone_geometry = new THREE.ConeGeometry( 1, -3, 32 );
    cone_geometry.translate(0,1.5,0);
    var cone = new THREE.Mesh( cone_geometry );

    var cylinder_geometry = new THREE.CylinderGeometry( 0.1, 0.1, 20, 6 );
    cylinder_geometry.translate(0,11,0);
    cylinder_geometry.merge(cone.geometry, cone.matrix);
    
	var material = new THREE.MeshBasicMaterial( {color: 0xfcba03} );
	cursor3D = new THREE.Mesh( cylinder_geometry, material );
	cursor3D.scale.set(0.3,0.3,0.3);
	scene.add(cursor3D);
	
	tilemap_meshes = {};

	render();

	window.addEventListener( 'resize', onWindowResize, false );
	window.addEventListener( 'mousemove', onMouseMove, false );


}

init();

