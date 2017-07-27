"""Writes OIE4 rels tagged as support/oppose/report/other"""

__author__ = 'Pablo Ruiz'
__date__ = '12/09/15'

import codecs
import inspect
import os
import sys


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(here, os.pardir))


import config as cfg


# Format of data to work with
# rel = {"type": rt, "confidence": cfd, "sentence": st,
#        "pred": prd, "argus": [ar[1] for ar in sorted(argus.items())]}
# {fn: supp: [rel1, rel2], opp: ..., "other" }


def write_rel(fn, rd, origin):
    """Write relation infos based on the dict that expresses the rel"""
    #fn, predtype, arg1, pred, other_args(4 slots), conf, sent
    assert origin in ("domain", "extra")
    out = u"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n"
    try:
        allargus = [ar for ar in rd["argus"][1:]]
    except IndexError:
        allargus = ["", "", "", ""]
    while len(allargus) < 4:
        allargus.append("")
    strargs = [fn, origin, rd["type"], rd["argus"][0], rd["pred"]]
    strargs.extend(allargus)
    strargs.extend((rd["confidence"], rd["sentence"]))
    formatted = out.format(*strargs)
    return formatted


def write_as_txt_with_dups(fn, results, cf=cfg, outdir=None):
    """Does not remove duplicate rels"""
    supports = sorted(results[cf.spref],
                      key=lambda rs: (rs["argus"][0], rs["pred"]))
    opposes = sorted(results[cf.opref],
                     key=lambda rs: (rs["argus"][0], rs["pred"]))
    others = sorted(results["other"],
                    key=lambda rs: (rs["argus"][0], rs["pred"]))
    if outdir is None:
        ffn = os.path.join(cf.outdir, fn)
        print "Writing to {}".format(ffn)
        with codecs.open(ffn, "w", "utf8") as ofd:
            for sup in supports:
                ofd.write(write_rel(fn, sup, "domain"))
            for opp in opposes:
                ofd.write(write_rel(fn, opp, "domain"))
            for oth in others:
                ofd.write(write_rel(fn, oth, "extra"))


def write_as_txt(fn, results, cf=cfg, outdir=None):
    supports = sorted(results[cf.spref],
                      key=lambda rs: (rs["argus"][0], rs["pred"]))
    opposes = sorted(results[cf.opref],
                     key=lambda rs: (rs["argus"][0], rs["pred"]))
    others = sorted(results["other"],
                    key=lambda rs: (rs["argus"][0], rs["pred"]))
    if outdir is None:
        ffn = os.path.join(cf.outdir, fn)
        print "Writing to {}".format(ffn)
        dones = []
        with codecs.open(ffn, "w", "utf8") as ofd:
            for sup in supports:
                outstr = write_rel(fn, sup, "domain")
                if outstr not in dones:
                    ofd.write(outstr)
                    dones.append(outstr)
            for opp in opposes:
                outstr = write_rel(fn, opp, "domain")
                if outstr not in dones:
                    ofd.write(outstr)
                    dones.append(outstr)
            for oth in others:
                outstr = write_rel(fn, oth, "extra")
                if outstr not in dones:
                    ofd.write(outstr)
                    dones.append(outstr)
