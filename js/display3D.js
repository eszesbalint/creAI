
var camera, controls, scene, renderer, mesh1, mesh2, mesh3;


function animate(){
var time = Date.now() * 0.0001;
mesh1.rotation.y=time;
mesh2.rotation.x=time;
mesh4.position.x=1000*Math.sin(time*10);
mesh4.position.y=1000*Math.cos(time*10);
}

function render(){
  renderer.render( scene, camera );
  requestAnimationFrame( render );
  controls.update();
  animate();
}



init = function(){
 camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 10000);
 camera.position.x=-1600;
 camera.position.y=1600;
 camera.position.z=-1600;

 controls = new THREE.TrackballControls( camera, document.querySelector(".maincanvas") );
 //controls.addEventListener('change', render);

 scene = new THREE.Scene();
 scene.background = new THREE.Color( 0xffffff );


 var sphere1 = new THREE.SphereGeometry(200,10,10);
 var sphere2 = new THREE.SphereGeometry(800,10,10);
 var cube1 = new THREE.BoxGeometry(1500,1500,1500);
 var cube2 = new THREE.BoxGeometry(100,100,100);

 var material = new THREE.MeshNormalMaterial();
 var frameMaterial = new THREE.MeshBasicMaterial({color: 0x000000, wireframe: true});


 mesh1 = new THREE.Mesh( sphere1, frameMaterial);
 mesh2 = new THREE.Mesh( sphere2, frameMaterial);
 mesh3 = new THREE.Mesh( cube1, new THREE.MeshBasicMaterial({color: 0xff0000, wireframe: true}));
 mesh4 = new THREE.Mesh( cube2, material);

 scene.add(mesh1);
 scene.add(mesh2);
 scene.add(mesh3);
 scene.add(mesh4);

 renderer = new THREE.WebGLRenderer({antialias: true});
 renderer.setClearColor( 0xffffff,1);
 renderer.setSize( window.innerWidth, window.innerHeight);
 document.body.appendChild(renderer.domElement);

 render();
}

window.addEventListener( 'resize', onWindowResize, false );

function onWindowResize(){

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

}

init();
