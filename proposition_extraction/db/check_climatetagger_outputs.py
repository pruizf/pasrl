"""To make sure what concepts i was getting"""

__author__ = 'Pablo Ruiz'
__date__ = '11/05/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import os
import simplejson as js
import time


indir = "/home/pablo/projects/ie/out/el/pointmentions_04252016"
outf = "/home/pablo/projects/ie/out/el/pointmentions_04252016_ana.txt"

cps = {} # concepts

for idx, fn in enumerate(sorted(os.listdir(indir))):
    ffn = os.path.join(indir, fn)
    with codecs.open(ffn, "r", "utf8") as ifd:
        jso = js.loads(ifd.read())
        for co in jso["concepts"]:
            cps.setdefault(co["prefLabel"], []).append(co["score"])
    if idx and not idx % 1000:
        print "Done {} files, {}".format(idx, time.strftime(
            "%H:%M:%S", time.localtime()))

print "Writing"
with codecs.open(outf, "w", "utf8") as outfd:
    allscos = []
    for co, scos in sorted(cps.items(), key=lambda x: -len(x[1])):
        ol = u"{}\t{}\t{}\t{}\t{}\t{}\n".format(co, len(scos),
                                                float(sum(scos)) / len(scos),
                                                min(scos), max(scos),
                                                ";".join([str(x) for x in scos]))
        outfd.write(ol)
        allscos.extend(scos)
    outfd.write("\nmin: {}\nmax: {}\nave: {}".format(
        min(allscos), max(allscos), float(sum(allscos)) / len(allscos)))
