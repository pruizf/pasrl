"""
Read output of script that extracts roles for nominal preds to
see if any of them are an actor
"""

__author__ = 'Pablo Ruiz'
__date__ = '07/10/15'

import codecs
import inspect
import os
import re
import sys
import time


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, os.pardir))
sys.path.append(os.path.join(os.path.join(here, os.pardir),
                os.pardir))
sys.path.append(os.path.join(os.path.join(here, os.pardir), "srl"))
sys.path.append(os.path.join(
                os.path.join(os.path.join(here, os.pardir), os.pardir), "srl"))


import manage_domain_data as mdd
from normalize_pronouns import find_actor_variants_in_argu
import utils as ut


predres = "/home/pablo/projects/ie/out/enb_corefs_out_npreds4"
outfn = "/home/pablo/projects/ie/out/enb_corefs_out_npreds10_with_actors.txt"

dacts = mdd.parse_actors()
ofd = codecs.open(outfn, "w", "utf8")

dones = 0
for fn in os.listdir(predres):
    ffn = os.path.join(predres, fn)
    with codecs.open(ffn, "r", "utf8") as infd:
        line = infd.readline()
        while line:
            if line.startswith("S: "):
                myroles = []
                #sentence
                sent = line
                # predicate
                pred = infd.readline()
                pred_form = re.search(r"PRED: (\w+)", pred).group(1).lower()
                assert pred_form
                line = infd.readline()
                # roles
                while "ROLE" in line:
                    myroles.append(line)
                    line = infd.readline()
                # out
                for mr in myroles:
                    test_actors = find_actor_variants_in_argu(dacts, mr)
                    if test_actors:
                        ofd.write(u"\n{}\n".format(os.path.basename(ffn)))
                        for ta in test_actors:
                            sent = sent.lower().replace(
                                ta.lower(), u"**{}**".format(ta.lower()))
                            sent = sent.lower().replace(
                                pred_form, ur"++{}++".format(pred_form))
                        sent = re.sub(ur"\+{2,}", "++", sent)
                        sent = re.sub(ur"\*{2,}", "**", sent)
                        ofd.write("".join((sent[0].upper(), sent[1:])))
                        ofd.write(pred)
                        ofd.write("".join([r for r in myroles]))
            dones += 1
            if dones % 1000 == 0:
                print "Done {} lines {}".format(
                    dones,time.strftime("%H:%M:%S", time.localtime()))
            line = infd.readline()

ofd.close()