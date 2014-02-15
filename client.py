import requests
import argparse
import json
import logging
import tarfile
import shutil
import os
import os.path

from io import BytesIO

from sbmodd import md5sum_directory, get_subdirs, get_mod_dirs


def get_server_mod_info(host, port=21026):
    return requests.get("http://%s:%s/mods" % (host, port)).json()


def compare(mod_info, mods_dir):
    mods = get_mod_dirs(mods_dir, True)

    missing = []
    conflict = []
    found = []

    for mod in mod_info:
        done = False
        for omod in mods:
            if omod['dir'] == mod['dir']:
                if omod['md5sum'] == mod['md5sum']:
                    found.append(mod)
                else:
                    logging.error("[%s] %s != %s" % (omod['modinfo']['name'], omod['md5sum'], mod['md5sum']))
                    conflict.append(mod)
                done = True
                break
        if done:
            continue
        missing.append(mod)

    dirs = [x['dir'] for x in missing + conflict + found]
    for mod in mods:
        if mod['dir'] in dirs:
            continue
        conflict.append(mod)

    return (found, missing, conflict)


def install(mod_name, mods_dir, host, port=21026):
    data = requests.get("http://%s:%s/mod/%s" % (host, port, mod_name))
    tar = tarfile.open(mode="r:xz", fileobj=BytesIO(data.content))
    tar.extractall(path=mods_dir)


def cleanup(mods_dir, mod_dir):
    shutil.rmtree(os.path.join(mods_dir, mod_dir))


def update_from_server(host, mods_dir, port=21026):
    print("Getting mod list...")
    modsinfo = get_server_mod_info(host, port)

    print("Comparing mods...")
    d = compare(modsinfo, mods_dir)

    if len(d[0]):
        print("Found:")
        print("  " + ", ".join([x['modinfo']['name'] for x in d[0]]))

    if len(d[1]):
        print("Missing:")
        print("  " + ", ".join([x['modinfo']['name'] for x in d[1]]))

    if len(d[2]):
        print("Conflicting:")
        print("  " + ", ".join([x['modinfo']['name'] for x in d[2]]))

    confirm = input("Would you like to synchronise your mods now? [y/N]")
    if confirm.strip() != 'y':
        return

    print("Removing conflicting mods...")
    for mod in d[2]:
        cleanup(mods_dir, mod['dir'])
        print("Removed %s" % mod['dir'])

    print("Updating conflicting mods...")
    for mod in d[2]:
        install(mod['modinfo']['name'], mods_dir, host, port)
        print("Installed [%s]." % mod['modinfo']['name'])

    print("Installing missing mods...")
    for mod in d[1]:
        install(mod['modinfo']['name'], mods_dir, host, port)
        print("Installed [%s]." % mod['modinfo']['name'])
