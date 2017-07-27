"""
Need to get pointmentions from fixture, so that can run climatetagger api on them
"""
__author__ = 'Pablo Ruiz'
__date__ = '25/04/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import os
import simplejson
import time

#{"fields": {"text": " (conclusions (FCCC/SBSTA/2014/L.25)", "point": 5, "end": 141, "start": 101}, "model": "ui.pointmention", "pk": 6974},
infi = "/home/pablo/projects/ie/wk/ui_wireframe/uibo/webuibo/ext_data/json/fixture_04162016.json"
outdir = "/home/pablo/projects/ie/corpora/pointmentions_04252016"


if not os.path.exists(outdir):
    os.makedirs(outdir)

ofinbr = 1
with codecs.open(infi, "r", "utf8") as infd:
    line = infd.readline()
    dones = 0
    while line:
        if "ui.pointmention" in line:
            jsob = simplejson.loads(line.strip().strip(","))
            txt = jsob["fields"]["text"]
            if txt == "NONE":
                line = infd.readline()
                continue
            with codecs.open(os.path.join(outdir, "pointmention_nbr_{}".format(ofinbr)),
                             "w", "utf8") as ofifd:
                ofifd.write(u"{}\n".format(txt))
            ofinbr += 1
            dones += 1
            if not dones % 1000:
                print "Done {} pointmentions, {}".format(dones, time.strftime(
                    "%H:%M:%S", time.localtime()))
        line = infd.readline()
