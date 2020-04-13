#import os
#
# modules = [name for name in os.listdir(os.path.dirname(__file__)) if os.path.isdir(
#    os.path.join(os.path.dirname(__file__), name)) and name != '__pycache__']
#
# for module in modules:
#    __import__('creAI.plugins.' + module, locals(), globals())
#
#del modules
