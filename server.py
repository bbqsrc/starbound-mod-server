import tornado.web
import tornado.ioloop
import json
import logging
import tarfile
import os

from io import BytesIO
from tornado.web import RequestHandler
from tornado.options import define, options

from sbmodd import md5sum_directory, get_subdirs, get_mod_dirs


define('port', type=int, default=21026)
define('mods', type=str)


class GetInstalledModData(RequestHandler):
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(get_mod_dirs(options.mods, True), indent=2))


class GetMod(RequestHandler):
    def get(self, mod_name):
        self.set_header("Content-Type", 'application/x-lzma')

        moddata = get_mod_dirs(options.mods)
        o = [x['dir'] for x in moddata if x['modinfo']['name'] == mod_name]
        if len(o) == 0:
            return

        mod_dir = o[0]
        os.chdir(options.mods)

        out = BytesIO()
        tar = tarfile.open(mode='w:xz', fileobj=out)
        for o in os.walk(mod_dir):
            logging.debug(o)
            for fn in o[2]:
                tar.add(os.path.join(o[0], fn))
        tar.close()

        self.write(out.getvalue())


if __name__ == "__main__":
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/mods", GetInstalledModData),
        (r"/mod/(.*)", GetMod)
    ])
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
