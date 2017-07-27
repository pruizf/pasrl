"""
Split a document text into sentences using IXA piples tokenization
@note: this was left unfinished but can still import and use available functions
"""

__author__ = 'Pablo Ruiz'
__date__ = '02/10/15'

import codecs
import inspect
import logging
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
sys.path.append(os.path.join(os.path.join(here, os.pardir),
                os.pardir))

import config as cfg
import manage_domain_data as mdd
import model as md
import utils as ut

rawdir = "/home/pablo/projects/clm/enbmid"
normdir = "/home/pablo/projects/clm/enbnorm"
nafdir = "/home/pablo/projects/ie/out/enb_srlmt_out_2/srl"
nafnormdir = "/home/pablo/projects/ie/out/enb_srlmt_out_2_norm"


def get_sentence_nbr_for_term_ids(naf):
    """
    Return hash of sentence numbers by term-id
    """
    try:
        tree = np(naf)
    except IOError:
        print "!! Missing output file {}".format(os.path.basename(naf))
        return
    except XMLSyntaxError:
        print "!! Document is empty {}".format(os.path.basename(naf))
        return
    tid2sent = {}
    for term in naf.get_terms():
        span_ids = term.get_span().get_span_ids()
        wf = tree.get_token(span_ids[0])
        tid2sent[term.get_id()] = int(wf.get_sent())
    return tid2sent


def get_sentence_offsets_from_naf(naf):
    sent_ids = {}
    sent_offsets = {}
    try:
        toks = list(naf.get_tokens())
    except TypeError:
        print "!!File has no text layer"
        return {}
    for wf in toks:
        sent_ids.setdefault(int(wf.get_sent()), 1)
    maxsent = max(sent_ids)
    for sid in range(maxsent + 1)[1:]:
        swfs = [wf for wf in toks if int(wf.get_sent()) == sid]
        sent_offsets[sid] = (int(swfs[0].get_offset()),
                             int(swfs[-1].get_offset()) +
                             int(swfs[-1].get_length()))
    return sent_offsets


def get_surface_form_for_sentence():
    pass


def main():
    if not os.path.exists(nafnormdir):
        os.makedirs(nafnormdir)


if __name__ == "__main__":
    main()