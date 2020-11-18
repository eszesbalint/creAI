
async function populate_app_info(){
    var header = document.getElementsByTagName('header')[0];
    //list_element.innerHTML = '';
    var info = await eel.get_app_info()();
    header.innerHTML = `
        <h1>creai</h1>
        <p>`+info['description']+`</p>
    `
}

async function save(){
    var schematic = await eel.get_tilemap_schematic()();
    //if (!schematic) {
    //    return;
    //}
    var base64 = btoa(
        new Uint8Array(schematic)
          .reduce((data, byte) => data + String.fromCharCode(byte), '')
        );
    var data_uri = 'data:application/octet-stream;charset=utf-16le;base64,' + base64;

    var element = document.createElement('a');
  	element.setAttribute('href', data_uri);
  	element.setAttribute('download', 'generated.schem');

  	element.style.display = 'none';
  	document.body.appendChild(element);

  	element.click();

  	document.body.removeChild(element);
}

eel.expose(exception_alert);
function exception_alert(s){
    alert(s);
}

populate_app_info();
populate_style_list();