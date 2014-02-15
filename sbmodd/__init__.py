import hashlib
import os
import glob
import os.path
import json
#import logging


def md5(data):
    m = hashlib.md5()
    m.update(data)


def md5sum_directory(dir):
    m = hashlib.md5()
    for o in os.walk(dir):
        for fn in o[2]:
            if fn.startswith('.'): continue
            with open(os.path.join(o[0], fn), 'rb') as f:
                m.update(f.read())

    return m.hexdigest()


def get_subdirs(dir):
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]


def get_mod_dirs(mod_dir, checksum=False):
        o = []
        subdirs = get_subdirs(mod_dir)
        #logging.debug(subdirs)
        for d in subdirs:
            d = os.path.join(mod_dir, d)
            modinfo = glob.glob(os.path.join(d, "*.modinfo"))
            #logging.debug(modinfo)
            if len(modinfo) == 1:
                x = {
                    "dir": os.path.basename(d),
                    "modinfo": json.load(open(modinfo[0]))
                }

                if checksum:
                    x["md5sum"] = md5sum_directory(d)
                o.append(x)
        return o

