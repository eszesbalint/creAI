var display3D = require('./js/display3D.js')
display3D.init(document.querySelector('.canvascontainer'), document.querySelector('.maincanvas'))
display3D.start()

var t_width, t_height, t_depth

document.querySelector('#width').addEventListener('input', function(){
  let input = parseInt(document.querySelector('#width').value, 10)
  if (input != NaN && input > 0){
    t_width = input
  }
})

document.querySelector('#height').addEventListener('input', function(){
  t_height = parseInt(document.querySelector('#height').value, 10)
  if (input != NaN && input > 0){
    t_height = input
  }
})

document.querySelector('#depth').addEventListener('input', function(){
  t_depth = parseInt(document.querySelector('#depth').value, 10)
  if (input != NaN && input > 0){
    t_depth = input
  }
})

var zerorpc = require("zerorpc")
var client = new zerorpc.Client()
client.connect("tcp://127.0.0.1:4242")

function generateTileMap(attributes){
  client.invoke("generate", "", (error, res) => {
    if(error) {
      console.error(error)
    } else {
      display3D.display(JSON.parse(res))
    }
  })
}

function generate(){
  generateTileMap({x:t_width,y:t_height,z:t_depth})
}

document.querySelector('.generate_btn').addEventListener('click',function(){
  generate();
})

var dimformIsVisible = false;
document.querySelector('.dimension_btn').addEventListener('click',function(){
  if (dimformIsVisible){
    document.querySelector('.dimform').classList.remove('hide')
    dimformIsVisible = false
  } else {
    document.querySelector('.dimform').classList.add('hide')
    dimformIsVisible = true
  }

})

function initCloseBtn() {
      var closeEl = document.querySelector(".close");
      if (closeEl) {
        closeEl.addEventListener('click', function() {
          window.close();
        });
      };
      return closeEl;
}

document.addEventListener('DOMContentLoaded', function() {
  initCloseBtn();
});
