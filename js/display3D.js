var container, canvas;

module.exports = {
  init: function (con, can) {
    container = con;
    canvas = can;
  },
  start: function () {
    init();
  },
  display: function (data) {
    removeMeshFromScene();
    addMeshToScene(data);
  }
};


var camera, controls, scene, renderer, mainMesh;

var tileModelLoader = require('./minecraftBlocks.js')

function addMeshToScene(recv_data){
  var material = new THREE.MeshNormalMaterial();
  var frameMaterial = new THREE.MeshBasicMaterial({color: 0x000000, wireframe: true});
  var singleGeometry = new THREE.Geometry();
  for (var i = 0; i < recv_data.length; i++) {
    for (var j = 0; j < recv_data[i].length; j++) {
      for (var k = 0; k < recv_data[i][j].length; k++) {
        if (recv_data[i][j][k][0] > 0.) {
          console.log('Beep boop')
          //var cube = new THREE.BoxGeometry(1,1,1);
          var cube = tileModelLoader.getTileGeometry(recv_data[i][j][k][0],recv_data[i][j][k][1]);
          if (cube == null){cube = new THREE.BoxGeometry(1,1,1)}
          var mesh = new THREE.Mesh( cube );

          mesh.position.y = i + 0.5;
          mesh.position.x = j + 0.5 - Math.floor(recv_data[i].length/2);
          mesh.position.z = k + 0.5 - Math.floor(recv_data[i][j].length/2);
          mesh.updateMatrix();
          singleGeometry.merge(mesh.geometry, mesh.matrix);

        }
      }
    }
  }
  mainMesh = new THREE.Mesh( singleGeometry, material);
  scene.add(mainMesh);
}

function addGridToScene(){
  var size = 14, step = 1;
  var geometry = new THREE.Geometry();
  var material = new THREE.LineBasicMaterial({color: 'black'});

  for (var i = -size; i < size; i += step) {
    geometry.vertices.push(new THREE.Vector3( - size, - 0.004, i));
    geometry.vertices.push(new THREE.Vector3( size, - 0.004, i));
    geometry.vertices.push(new THREE.Vector3( i, - 0.004, - size));
    geometry.vertices.push(new THREE.Vector3( i, - 0.004, size));
  }

  var line = new THREE.Line(geometry, material, THREE.LinePieces);
  scene.add(line);
}

function removeMeshFromScene(){
  if (mainMesh != null){
    scene.remove(mainMesh);
  }
  mainMesh = null;
}

function render(){
  renderer.render( scene, camera );
  requestAnimationFrame( render );
  controls.update();
}



init = function(){

 camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 1, 10000);
 camera.position.x=-16;
 camera.position.y=16;
 camera.position.z=-16;

 controls = new THREE.OrbitControls( camera, canvas, canvas );
 //controls.addEventListener('change', render);

 scene = new THREE.Scene();
 scene.background = new THREE.Color( 0xeeeeee );
 scene.fog = new THREE.FogExp2( 0xcccccc, 0.07 );
 addGridToScene();

 renderer = new THREE.WebGLRenderer({antialias: true});
 renderer.setClearColor( 0xeeeeee,1);
 renderer.setSize( container.clientWidth, container.clientHeight);
 container.appendChild(renderer.domElement);

 render();
}

window.addEventListener( 'resize', onWindowResize, false );

function onWindowResize(){

    camera.aspect = container.clientWidth/ container.clientHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( container.clientWidth, container.clientHeight);

}
