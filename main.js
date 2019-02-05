const {app, BrowserWindow} = require('electron')
const path = require('path')

var python_proc

function runPythonServer(){
  python_proc = require('child_process').spawn('python',['./py/creaiapi.py'])
  if (python_proc != null){
    console.log('Python server is running')
  } else {
    console.log('Python server couldn\'t start')
  }
}

function killPythonServer(){
  python_proc.kill()
  python_proc = null
  console.log('Python server stopped')
}

//app.on('ready', runPythonServer)
runPythonServer()
app.on('will-quit', killPythonServer)




function createWindow () {
  window = new BrowserWindow({width: 800, height: 600, frame: false})
  window.setMenu(null)
  window.loadURL(require('url').format({
    pathname: path.join(__dirname, 'index.html'),
    protocol: 'file:',
    slashes: true
  }))
  window.webContents.openDevTools()
}

app.on('ready', createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin'){
    app.quit()
  }
})
