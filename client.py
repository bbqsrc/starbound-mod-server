import requests
import argparse
import jsonn

from .shared import md5sum_directory, get_subdirs, get_mod_dirs

def get_server_mod_info(host):
    return requests.get("http://%s/mods" % host).json()
