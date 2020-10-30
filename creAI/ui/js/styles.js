var is_busy = false;

async function generate(stl_name){
  if (is_busy) {
    return;
  } else {
    is_busy = true;
    document.getElementsByClassName('loading-screen')[0].style.display = 'flex';
    try {
      await eel.generate(stl_name)();
      await display_tilemap();
    } catch (e) {
      alert(e['errorText'])
    }

    document.getElementsByClassName('loading-screen')[0].style.display = 'none';
    is_busy = false;
  }
}


async function populate_style_list(){
  var list_element = document.getElementsByClassName("list")[0];
  //list_element.innerHTML = '';
  var styles = await eel.get_style_list()();

  for (const i in styles) {
    (async function () {
      var info = await eel.get_style_info(styles[i])();
      //Icon bytearray to data URI
      var base64 = btoa(
        new Uint8Array(info['icon'])
          .reduce((data, byte) => data + String.fromCharCode(byte), '')
        );
      var src = 'data:image/png;base64,' + base64;
      list_element.innerHTML += `
        <div class="blob-container" onclick="generate('`+info['name']+`');">
          <div class="hover-container">
            <div class="scale-container">
              <div class="spin-container">
                <div class="blob">
                  <div>
                    <img src="`+src+`">
                  </div>
                </div>
              </div>
            </div>
          </div>
          <label>
            <div>
              <p>generate with:</p>
              <h1>`+info['name']+`</h1>
              <p>for Minecraft `+info['mc_version']+`</p>
            </div>
          </label>
        </div>
      `
    })();
  }
}

