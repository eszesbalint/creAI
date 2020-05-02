


eel.expose(add_DOM_element);
function add_DOM_element(parent_id, html_tag, attributes) {
	var tag = document.createElement(html_tag);
	for (var key in attributes) {
		tag.setAttribute(key, attributes[key]);
	}
	if (parent_id != "body") {
		document.getElementById(parent_id).appendChild(tag);
	} else {
		document.body.appendChild(tag);
	}
	
}

eel.expose(append_text);
function append_text(parent_id, text) {
	document.getElementById(parent_id).innerHTML += text;
}

eel.expose(set_innerHTML);
function set_innerHTML(parent_id, text) {
	document.getElementById(parent_id).innerHTML = text;
}

eel.expose(show_DOM_element);
function show_DOM_element(id) {
	var element = document.getElementById(id);
	remove_class_from_DOM_element(id, 'hidden');
	remove_class_from_DOM_element(id, 'hide');
	add_class_to_DOM_element(id, 'show');
}

eel.expose(hide_DOM_element);
function hide_DOM_element(id) {
	var element = document.getElementById(id);
	remove_class_from_DOM_element(id, 'show');
	add_class_to_DOM_element(id, 'hide');
}

eel.expose(add_class_to_DOM_element);
function add_class_to_DOM_element(id, class_) {
	var element = document.getElementById(id);
	element.classList.add(class_);
}

eel.expose(remove_class_from_DOM_element);
function remove_class_from_DOM_element(id, class_) {
	var element = document.getElementById(id);
	element.classList.remove(class_);
}


eel.expose(remove_DOM_element);
function remove_DOM_element(id) {
	document.getElementById(id).remove();
}

eel.expose(file_open_dialog);
function file_open_dialog(callback_script, file_extention) {
	var file_selector = document.createElement('input');
	file_selector.setAttribute('type', 'file');
	file_selector.setAttribute('accept', file_extention);
	file_selector.onchange = e => { 
   		var file = e.target.files[0]; 
   		var reader = new FileReader();
   		reader.readAsArrayBuffer(file);


   			reader.onload = readerEvent => {
   			   var content = readerEvent.target.result;
   			   console.log( content );
   			   window['eel'][callback_script.split('.')[1].split('(')[0]](file.name, new Uint8Array(content));
   			}
   			
   		}
	file_selector.click();
	return false;
}

eel.expose(file_save_dialog);
function file_save_dialog(file_name, buffer) {
	var base64 = btoa(
		new Uint8Array(buffer)
		  .reduce((data, byte) => data + String.fromCharCode(byte), '')
	  );
	var element = document.createElement('a');
  	element.setAttribute('href', 'data:application/octet-stream;charset=utf-16le;base64,' + base64);
  	element.setAttribute('download', file_name);

  	element.style.display = 'none';
  	document.body.appendChild(element);

  	element.click();

  	document.body.removeChild(element);
}


function read_form(id, callback_script) {
	var form = document.getElementById(id);
	var values = {};
	for (var element = 0; element < form.elements.length; element++) {
		if (form.elements[element].name != ""){
			values[form.elements[element].name] = form.elements[element].value;
		}
	}
	console.log(values);
	window['eel'][callback_script.split('.')[1].split('(')[0]](values);
	return false;
}