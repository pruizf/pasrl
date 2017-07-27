"""Tests mADIOS grammar induction algo"""

import codecs
from nltk import sent_tokenize
import os
import sys

"""
Best results with 0.9 0.05 4 0.65
"""

MPATH = "/home/pablo/projects/ie/tools/madios"
workdir = "/home/pablo/projects/ie/corpora/madios_mid"
outdir = "/home/pablo/projects/ie/enb_madios_out"


#inf = "/home/pablo/projects/clm/enbmid11000/enb1216e.txt"
inf = "/home/pablo/projects/ie/corpora/enb_all.txt"
splitf = os.path.join(workdir, os.path.basename(inf))

#outf = os.path.join(outdir, os.path.basename(inf))
outf = os.path.join(outdir, os.path.splitext(
    os.path.basename(inf))[0] + "_2.txt")
print "Writing to {}:".format(outf)

print "Getting sentences"
with codecs.open(inf, "r", "utf8") as infh:
    sents = sent_tokenize(infh.read())

print "Writing sentences out"
with codecs.open(splitf, "w", "utf8") as splitfh:
    for sent in sents:
        splitfh.write("".join((" * ", sent, " #", "\n")))

print "Running MADIOS3"
command = "{}/ModifiedADIOS3 {} 0.9 0.05 4 0.65 > {}".format(
    MPATH, splitf, outf)

os.system(command)