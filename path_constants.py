import os
import sys


bundle_dir = parent_dir = config_path = None

if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    parent_dir = os.path.dirname(sys.executable)
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = bundle_dir
'''
config_path = os.path.join(parent_dir, "config")
if not os.path.isdir(config_path):
        os.makedirs(config_path)
'''

