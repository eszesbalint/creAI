

function file_open_dialog(file_extention, callback_function) {
	var file_selector = document.createElement('input');
	file_selector.setAttribute('type', 'file');
	file_selector.setAttribute('accept', file_extention);
	file_selector.onchange = e => { 
   		var file = e.target.files[0]; 
   		var reader = new FileReader();
   		reader.readAsArrayBuffer(file);


   			reader.onload = readerEvent => {
   			   var content = readerEvent.target.result; // this is the content!
   			   console.log( content );
   			   callback_function(file.name, new Uint8Array(content));
   			}
   			
   		}
	file_selector.click();
	return false;
}

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
