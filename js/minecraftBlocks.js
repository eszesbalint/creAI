var fs = require('fs')
var path = require('path')

module.exports = {
  getTileGeometry: function (id, data) {
    var geometry = null
    var blockstatesfilepath = getBlockStatesFilePath(id,data)
    if (blockstatesfilepath != null){
      var blockstatesjson = fs.readFileSync(blockstatesfilepath)
      blockstatesjson = JSON.parse(blockstatesjson)

      let variant_key = getBlockVariant(id, data)
      let variant = selectVariant(blockstatesjson, variant_key)
      let modelfilename = variant['model']
      let modelfilepath = path.join(__dirname, '..', 'tiles', 'models', modelfilename + '.json')
      let modeljson = fs.readFileSync(modelfilepath)
      modeljson = JSON.parse(modeljson)
      let elements = getElementsFromModel(modeljson)
      geometry = buildGeometryFromElements(elements, getRotationFromVariant(variant))
    }
    return geometry
  }
};

var filenames = fs.readFileSync('./tiles/blocks.json')
filenames = JSON.parse(filenames)

function getBlockStatesFilePath(id, data){
  var block = filenames[id.toString()]
  var filepath = null
  if (block != null){
    if (typeof block === 'string'){
      //filepath = path.join(__dirname, '..', 'tiles', 'blockstates', block + '.json')
    } else {
      var blockdata = block[data.toString()]
      if (blockdata != null){
          var blockstatesfilename = block[data.toString()][0]['filename']
          filepath = path.join(__dirname, '..', 'tiles', 'blockstates', blockstatesfilename + '.json')
      }
    }
  }
  return filepath
}

function getBlockVariant(id, data){
  var block = filenames[id.toString()]
  var variant = null
  if (block != null){
    if (typeof block === 'string'){
      //do nothing
    } else {
      var blockdata = block[data.toString()]
      if (blockdata != null){
        variant = blockdata[1]['variants']
      }
    }
  }
  return variant
}

function selectVariant(bsjson, v){
  var variant = null
  if (v != null){
    variant = bsjson['variants'][v]
  } else {
    var keys = Object.keys(bsjson['variants'])
    variant = bsjson['variants'][keys[ keys.length*Math.random() << 0]]
  }
  if (Array.isArray(variant)){
    variant = variant[ variant.length*Math.random() << 0]
  }
  return variant
}

function getElementsFromModel(mjson){
  var elements = null
  if (mjson['elements'] != null){
    elements = mjson['elements']
  } else {
    var modelfilename = mjson['parent']
    var modelfilepath = path.join(__dirname, '..', 'tiles', 'models', modelfilename + '.json')
    var modeljson = fs.readFileSync(modelfilepath)
    modeljson = JSON.parse(modeljson)
    elements = getElementsFromModel(modeljson)
  }
  return elements
}

function buildGeometryFromElements(elements, rotation){
  var blockgeometry = new THREE.Geometry()
  var rotatedgeometry = new THREE.Geometry()
  for (var i = 0; i < elements.length; i++) {
    var w =  elements[i]['to'][0] - elements[i]['from'][0]
    var h =  elements[i]['to'][1] - elements[i]['from'][1]
    var d =  elements[i]['to'][2] - elements[i]['from'][2]

    var x = (elements[i]['from'][0] + elements[i]['to'][0])/2/16 - 0.5
    var y = (elements[i]['from'][1] + elements[i]['to'][1])/2/16 - 0.5
    var z = (elements[i]['from'][2] + elements[i]['to'][2])/2/16 - 0.5

    var cube = new THREE.BoxGeometry(w,h,d)
    var mesh = new THREE.Mesh( cube )

    mesh.position.x = x
    mesh.position.y = y
    mesh.position.z = z

    mesh.scale.set(1/16,1/16,1/16)

    mesh.updateMatrix()
    blockgeometry.merge(mesh.geometry, mesh.matrix)
  }
  blockmesh = new THREE.Mesh( blockgeometry )
  blockmesh.rotation.order = 'YXZ'
  blockmesh.rotation.y = THREE.Math.degToRad(rotation[1])
  blockmesh.rotation.x = THREE.Math.degToRad(rotation[0])
  blockmesh.rotation.z = THREE.Math.degToRad(rotation[2])
  blockmesh.updateMatrix()
  rotatedgeometry.merge(blockmesh.geometry, blockmesh.matrix)
  return rotatedgeometry
}

function getRotationFromVariant(v){
  var rot = [0,0,0]
  if (v['x'] != null){rot[0] = v['x']}
  if (v['y'] != null){rot[1] = v['y']}
  if (v['z'] != null){rot[2] = v['z']}
  return rot
}
