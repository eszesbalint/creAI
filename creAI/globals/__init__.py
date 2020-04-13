import random
import string

cli_mode = True

plugins = {}
selected_plugin_id = None

current_max_id = 0
def gen_id():
    global current_max_id
    id_ = '{}'.format(current_max_id)
    current_max_id += 1
    return id_

def gen_rand_id(length):

    id_ = ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(length)
        )

    return id_