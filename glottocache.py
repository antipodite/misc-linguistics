"""
Useful for scripts which use Pyglottolog heavily to speed up access when using the same
languoids multiple times in different scopes or running the same script multiple times
"""
from cldfcatalog import Config
from pyglottolog import Glottolog
from pickle import dump, load
from pathlib import Path


class GlottoCache:
    """Save loaded Glottolog languoids so we don't have to wait every time"""
    def __init__(self, path, fname="glottocache.pickle"):
        if type(path) == str:
            path = Path(path)
        self.cachepath = path.joinpath(fname)
        try:
            with open(self.cachepath, "rb") as cachefile:
                self.cache = load(cachefile)
        except FileNotFoundError:
            self.cache = {}

        cfg = Config.from_file()
        self.glottolog = Glottolog(cfg.get_clone("glottolog"))
        # So we know whether to save
        self.written = False

    def __del__(self):
        self.save()

    def get(self, glottocode):
        if not glottocode:
            return None
        elif glottocode in self.cache:
            return self.cache[glottocode]
        else:
            lg = self.glottolog.languoid(glottocode)
            self.cache[glottocode] = lg
            self.written = True
            return lg

    def save(self):
        if self.written:
            with open(self.cachepath, "wb+") as cachefile:
                dump(self.cache, cachefile)

