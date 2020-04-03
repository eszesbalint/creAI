tilemaps = {}
selected_tilemap_id = None

plugins = {}
selected_plugin_id = None

current_max_id = 0
def gen_id():
    global current_max_id
    id_ = '{}'.format(current_max_id)
    current_max_id += 1
    return id_