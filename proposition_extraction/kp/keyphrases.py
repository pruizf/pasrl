# -*- coding: utf8 -*-

"""
Format keyphrase extraction results in a way that can be imported into DB.
The challenges here were two:
  - the filenames in the Yatea integration do not correspond to the filename
    conventions elsewhere in the corpus, so had to normalize for that.
  - had to add sentence numbers to the Yatea extractions so that can import
    into DB
"""

__author__ = 'Pablo Ruiz'
__date__ = '10/10/15'


import codecs
import inspect
from lxml.etree import XMLSyntaxError
import os
import re
import sys

from KafNafParserPy import KafNafParser as np

# app-specific imports --------------------------------------------------------
here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, os.pardir))
sys.path.append(os.path.join(os.path.join(here, os.pardir),
                             "scripts"))

import config as cfg
import sentence_split as sp
import utils as ut


badchars = [u"“", u"”", u"’"]


def read_yatea_output(ydir=cfg.yatea_results_dir,
                      flist=cfg.yatea_results_list):
    """
    Read yatea kws based on file list under data
    Clean up the keywords and normalize to lowercase
    @param ydir: base dir to yatea results
    @param flist: list with path to each yatea termList relative to ydir.
    """
    print "- Yatea results directory: {}".format(ydir)
    print "- Yatea full paths: {}".format(flist)
    print "\n- Reading Yatea output"
    dir2kw = {}
    fns = [ll.strip() for ll in codecs.open(flist, "r", "utf8").readlines()
           if not ll.startswith("#")]
    for fn in fns:
        fn2kw = {}
        with codecs.open(os.path.join(ydir, fn), "r", "utf8") as inf:
            line = inf.readline()
            while line:
                if line.startswith("# "):
                    line = inf.readline()
                for bc in badchars:
                    line = line.replace(bc, "")
                sl = line.split("\t")
                if len(sl) < 2:
                    line = inf.readline()
                    continue
                kw = sl[0].strip()
                kw = re.sub("\s{2,}", " ", kw)
                if not kw:
                    line = inf.readline()
                    continue
                #TODO: use actual case, not lc
                fn2kw.setdefault(kw.lower(), int(sl[1]))
                fn2kw[kw.lower()] += int(sl[1])
                line = inf.readline()
        dir2kw[fn] = fn2kw
    return dir2kw


def clean_yatea_fn(myfn):
    """Make yatea result-file-name match filename elsewhere in the workflow"""
    myfn = myfn.replace("e.ttg", "e.txt")
    myfn = myfn.replace("e_html", "e.html")
    myfn = myfn.replace("._html", ".html")
    myfn = myfn.replace(".ttg", "")
    myfn = myfn[2:]
    myfn = re.sub("/.+", "", myfn)
    return myfn


def find_sentence_offsets_for_files_in_dir(flist, nafdir=cfg.srlres):
    """
    Given an iterable with filenames for yatea results, 
    return sentence offsets for that file, having normalized the yatea filename
    to the filenames used elsewher in the corpus.
    """
    print "- Getting sentence positions for corpus"
    dir2so = {}
    for fn in flist:
        orig_fn = fn
        fn = clean_yatea_fn(orig_fn)
        ffn = os.path.join(nafdir, fn + cfg.srlsuffix)
        print "FFN", ffn
        try:
            nafo = np(ffn)
        except IOError:
            print "!! Missing output file {}".format(os.path.basename(ffn))
            nafo = None
        except XMLSyntaxError:
            print "!! Document is empty {}".format(os.path.basename(ffn))
            nafo = None
        if nafo is not None:
            file_offsets = sp.get_sentence_offsets_from_naf(nafo)
            if not file_offsets:
                print "!! Empty text layer for file {}".format(
                    os.path.basename(ffn))
            #print fn
            dir2so[fn] = file_offsets
    return dir2so


def kp_occurrences_to_sentence_id(dir2kps, dir2spos, txtdir=cfg.yatea_textdir):
    """
    Given the raw text of a file, a dict of keyphrase per filename, and
    a dict with sentence offsets per filename, find the keyphrase occurrences
    and return dict with kp, positions and sentence offsets.
    @param dir2kps: dict of filenames and their kws (with fns in normal corpus
    format, not in the yatea format)
    @param dir2spos: hash with sentence offsets by fn and sentence id
    @param txtdir: dir with texts
    """
    print "- Getting sentence ids for keyphrases"
    kw2infos = {}
    for fn, kws in dir2kps.items():
        orig_fn = fn
        fn = clean_yatea_fn(orig_fn)
        try:
            assert fn in dir2spos
        except AssertionError:
            print "!! No sentence positions for {}".format(fn)
            kw2infos[fn] = {}
            continue
        with codecs.open(os.path.join(txtdir, fn), "r", "utf8") as inf:
            txt = inf.read()
        kw2infos.setdefault(fn, {})
        for kw in kws:
            assert kw
            mos = re.finditer(re.compile(ur"\b{}\b".format(
                ut.rgescape(kw)), re.I|re.UNICODE), txt)
            kw2infos[fn][kw] = [{"start": mb.start(), "end": mb.end()}
                                for mb in mos]
            for idx, kwp in enumerate(kw2infos[fn][kw]):
                for sid, (s_start, s_end) in dir2spos[fn].items():
                    if s_end >= kwp["end"] and s_start <= kwp["start"]:
                        kw2infos[fn][kw][idx]["sid"] = sid
                        break
    return kw2infos


def write_out(infos, outf=cfg.yatea_analyzed):
    """
    Writes out the hash containing keyphrase occurrence
    info per file
    """
    print "- Writing out to: {}".format(outf)
    with codecs.open(outf, "w", "utf8") as ofd:
        for fn, kwdict in infos.items():
            for kw, kinfos in kwdict.items():
                for occurrence in kinfos:
                    try:
                        outl = u"{}\t{}\t{}\t{}\t{}\t{}-{}\n".format(
                            fn, kw, occurrence["start"],
                            occurrence["end"], occurrence["sid"],
                            fn, occurrence["sid"])
                    except KeyError:
                        import pdb;pdb.set_trace()
                        print "KeyError: {}\t{}\t{}".format(fn, kw,
                                                            repr(occurrence))
                        # tokenization pb w st. kitts
                        if (fn in ("enb12585e.html", "enb12586e.html")
                            and kw == "st. kitts"):
                            mysid = 45
                        elif (fn in ("enb12594e.html") and kw == "st. kitts"):
                            mysid = 587
                        # other tokenization pbs
                        elif (fn in ("enb12176e.html") and kw == "vol. iii"):
                            mysid = 286
                        elif (fn in ("enb12498e.html") and
                              kw == "cap. parties"):
                            mysid = -1
                        # there were some others, but really, the kws are not
                        # informative, so no need to add them ... (like, it's
                        # street addresses with a period that tokenized wrong etc.)
                        else:
                            mysid = -1
                        outl = u"{}\t{}\t{}\t{}\t{}\t{}-{}\n".format(
                            fn, kw, occurrence["start"], occurrence["end"],
                            mysid, fn, mysid)
                    ofd.write(outl)


def main():
    """Run"""
    dir2kw = read_yatea_output()
    dir2off = find_sentence_offsets_for_files_in_dir(dir2kw)
    dir2infos = kp_occurrences_to_sentence_id(dir2kw, dir2off)
    write_out(dir2infos)


if __name__ == "__main__":
    main()
