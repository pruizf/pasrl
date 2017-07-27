#-*-coding: utf8 -*-

"""Finds sentence-id for test items"""

__author__ = 'Pablo Ruiz'
__date__ = '04/11/15'


import codecs
import re


def rem_irrel_chars(st):
    """
    SRL sometimes removes these from roles and they don't matter: delete.
    Copied from evaluation.py so that sentence format matches in files to cross
    """
    st = st.replace(u"“", "``")
    st = st.replace(u"”", '"')
    st = st.replace("``", "")
    st = st.replace("''", "")
    st = st.replace('"', "")
    st = re.sub("\.$", "", st)
    st = re.sub(ur"['+,-./:;<=>?@~]$", "", st)
    st = re.sub("_", " ", st)
    st = re.sub("^\s+", "", st)
    st = re.sub("\s+$", "", st)
    return st


def fix_detokenize(st):
    """
    Fix uncommon detokenization errors so that system and golden match.
    (This is due to way i detokenize IXA-Pipes outputs into surface strings,
    irrelevant for evaluation)
    e.g. '2(b)' gets detokenized as '2 (b)'
    Copied from evaluation.py so that
    """
    st = re.sub(ur"( [0-9]+)[ ](\(b\))", ur"\1\2", st)
    return st


def read_sentences(sf):
    """Read sentences in db import format and return a hash of id per text"""
    s2id = {}
    with codecs.open(sf, "r", "utf8") as sfd:
        ll = sfd.readline()
        while ll:
            sl = ll.strip().split("\t")
            fid = sl[0]
            sid = sl[1]
            txt = sl[2]
            s2id[fix_detokenize(rem_irrel_chars(txt.lower().strip()))] = \
                u"{}-{}".format(fid, sid)
            ll = sfd.readline()
    return s2id


def add_id_to_test_set(ts, of, sinfos):
    """
    Find id for sentences, add it and write out
    @param ts: test-set
    @sinfos: hash with ids per sentence
    """
    with codecs.open(ts, "r", "utf8") as tfd, \
         codecs.open(of, "w", "utf8") as ofd:
        ll = tfd.readline()
        while ll:
            if re.match(r"[0-9]+\t", ll):
                sl = ll.strip().split("\t")
                ts_txt = sl[-1]
                try:
                    fsid = sinfos[ts_txt.lower().strip()]
                    outl = u"{}\t{}\n".format(fsid, ts_txt)
                except KeyError:
                    print "NOT FOUND: {}".format(ts_txt.lower().strip())
                    outl = ">>>FIX" + ll
            else:
                outl = ll
            ofd.write(outl)
            ll = tfd.readline()


def main(testfi, outfi, sentfi):
    print "In: {}".format(testfi)
    print "Out: {}".format(outfi)
    print "Sen: {}".format(sentfi)
    seinfos = read_sentences(sentfi)
    add_id_to_test_set(testfi, outfi, seinfos)


if __name__ == "__main__":
    senfi = ("/home/pablo/projects/clm/enb_corpus/" +
             "sentences/ixa_sentence_tokenization/enb_sentences_4db.txt")
    tsfi = ("/home/pablo/projects/ie/ui/" +
            "resultats_systeme_pour_tests_interface.txt")
    tsnw = ("/home/pablo/projects/ie/ui/" +
            "resultats_systeme_pour_tests_interface_with_sentence_ids.txt")
    main(tsfi, tsnw, senfi)