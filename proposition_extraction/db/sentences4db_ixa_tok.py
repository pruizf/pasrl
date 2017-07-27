"""
Split a document text into sentences using IXA piples tokenization
"""

__author__ = 'Pablo Ruiz'
__date__ = '03/11/15'

import codecs
import inspect
from lxml.etree import XMLSyntaxError
import os
import re
import sys
import time

from KafNafParserPy import KafNafParser as np

# app-specific imports --------------------------------------------------------
here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, os.pardir))

import utils as ut


def naf2sents(naf):
    """For a NAF file, return sentences and their metadata"""
    try:
        tree = np(naf)
    except IOError:
        print "!! Missing output file {}".format(os.path.basename(naf))
        return
    except XMLSyntaxError:
        print "!! Document is empty {}".format(os.path.basename(naf))
        return
    sent_ids = {}
    sents = {}
    try:
        toks = list(tree.get_tokens())
    except TypeError:
        return {}
    fid = re.match(ur"^[^.]+\.(?:html|txt)", os.path.basename(naf))
    assert fid
    fid = fid.group(0)
    for wf in toks:
        sent_ids.setdefault(int(wf.get_sent()), 1)
    maxsent = max(sent_ids)
    for sid in range(maxsent + 1)[1:]:
        sents[sid] = {}
        swfs = [wf for wf in toks if int(wf.get_sent()) == sid]
        sents[sid]["text"] = ut.detokenize(" ".join(
            [wf.get_text() for wf in swfs]))
        sents[sid]["start"] = int(swfs[0].get_offset())
        sents[sid]["end"] = int(swfs[-1].get_offset()) + \
                            int(swfs[-1].get_length())
    return {fid: sents}


def dir2sents(indir):
    """Apply L{naf2sents} for each file as generator"""
    for fn in sorted(os.listdir(indir)):
        ffn = os.path.join(indir, fn)
        fn2sents = naf2sents(ffn)
        yield fn2sents


def write_sents(di, outf):
    """
    Write sentence info based on a hash of infos by sentence-id
    by filename.
    """
    if not di:
        return
    with codecs.open(outf, "a", "utf8") as outfd:
        for fn, sid2infos in sorted(di.items()):
            print "Processing {}, {}".format(
                fn, time.asctime(time.localtime()))
            for sid, infos in sorted(sid2infos.items()):
                outl = u"{}\t{}\t{}\t{}\t{}\t{}-{}\n".format(fn, sid,
                    infos["text"], infos["start"], infos["end"], fn, sid)
                outfd.write(outl)


def main(indir, outf):
    print "In: {}".format(indir)
    print "Out: {}".format(outf)
    for fn2sinfo in dir2sents(indir):
        write_sents(fn2sinfo, outf)


if __name__ == "__main__":
    # nafdir = "/home/pablo/projects/ie/out/enb_corefs_out_with_countries/srl"
    # outfn = "/home/pablo/projects/clm/enb_corpus/sentences/" + \
    #         "ixa_sentence_tokenization/enb_sentences_4db.txt"
    nafdir = "/home/pablo/projects/ie/out/ENB_postAR4_txt/srl"
    outfn = "/home/pablo/projects/clm/enb_corpus/" + \
            "enb_postAR4_json.txt"
    main(nafdir, outfn)
