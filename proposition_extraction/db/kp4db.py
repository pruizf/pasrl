"""
Format KeyPhrase outputs for DB import, making sentence ids match ixa pipes tokenization
"""

__author__ = 'Pablo Ruiz'
__date__ = '04/11/15'

import codecs
import inspect
from lxml.etree import XMLSyntaxError
import os
import pickle
import re
import sys
import time

from KafNafParserPy import KafNafParser as np

# app-specific imports --------------------------------------------------------
here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, os.pardir))

import config as cfg
import utils as ut


def naf2sent_offsets(naf):
    """For a NAF file, return sentence numbers and offsets"""
    try:
        tree = np(naf)
    except IOError:
        print "!! Missing output file {}".format(os.path.basename(naf))
        return
    except XMLSyntaxError:
        print "!! Document is empty {}".format(os.path.basename(naf))
        return
    sent_offsets = {}
    try:
        toks = list(tree.get_tokens())
    except TypeError:
        return {}
    fid = re.match(ur"^[^.]+\.(?:html|txt)", os.path.basename(naf))
    assert fid
    fid = fid.group(0)
    for wf in toks:
        sent_offsets.setdefault(int(wf.get_sent()), 1)
    maxsent = max(sent_offsets)
    for sid in range(maxsent + 1)[1:]:
        sent_offsets[sid] = {}
        swfs = [wf for wf in toks if int(wf.get_sent()) == sid]
        sent_offsets[sid] = (int(swfs[0].get_offset()),
                             int(swfs[-1].get_offset()) +
                             int(swfs[-1].get_length()))
    return {fid: sent_offsets}


def dir2offsets(indir):
    """Apply L{naf2sent_offsets} for each file, return aggregated dict"""
    print "Getting sentence offsets"
    allfn2offsets = {}
    for idx, fn in enumerate(sorted(os.listdir(indir))):
        print "  {}".format(fn)
        ffn = os.path.join(indir, fn)
        fn2offsets = naf2sent_offsets(ffn)
        try:
            allfn2offsets.update(fn2offsets)
        except TypeError:
            print "! Error with file: {}".format(fn)
        if idx and not idx % 50:
            print "Done {} files, {}".format(
                idx, time.asctime(time.localtime()))
    return allfn2offsets


def verify_sentence_id_for_keyphrases(kpf, fn2o, okpf):
    """
    Read keyphrase extraction outputs and write out, correcting sentence id as needed
    @param kpf: keyphrase file for corpus
    @param fn2o: hash with sentence ids and offsets per file
    """
    with codecs.open(kpf, "r", "utf8") as kpfd, \
         codecs.open(okpf, "w", "utf8") as kpout:
        line = kpfd.readline()
        dones = 0
        while line:
            skip_file = False
            sl = line.strip().split("\t")
            kfn = sl[0]
            try:
                k_start, k_end = int(sl[2]), int(sl[3])
            except IndexError:
                line = kpfd.readline()
                continue
            try:
                assert kfn in fn2o
            except AssertionError:
                skip_file = True
            if not skip_file:
                for sid, (s_start, s_end) in fn2o[kfn].items():
                    if s_end >= k_start and s_start <= k_end:
                        sl[-2] = sid
                        break
            kpout.write("".join(["\t".join([unicode(b) for b in sl]), "\n"]))
            line = kpfd.readline()
            if not dones % 10000:
                print "Done {} lines, {}".format(
                    dones, time.asctime(time.localtime()))
            dones += 1


def main(indir, kpfile, outf, offsets_from_pickle=True):
    global offsets # debug
    print "NAF: {}".format(indir)
    print "KP: {}".format(kpfile)
    print "Out: {}".format(outf)
    if offsets_from_pickle:
        print "Loading offsets from pickle: {}".format(
            os.path.basename(cfg.sentence_offsets))
        offsets = pickle.load(open(cfg.sentence_offsets))
    else:
        offsets = dir2offsets(indir)
    verify_sentence_id_for_keyphrases(kpfile, offsets, outf)


if __name__ == "__main__":
    nafdir = "/home/pablo/projects/ie/out/enb_corefs_out_with_countries/srl"
    keyphrases = "/home/pablo/projects/ie/out/kp/enb_test_kp_yatea_5.txt"
    outfn = "/home/pablo/projects/ie/wk/db/enb_keyphrases_4db.txt"
    main(nafdir, keyphrases, outfn)
