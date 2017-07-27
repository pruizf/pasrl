"""To run some tests on NAF SRL layer"""

__author__ = 'Pablo Ruiz'
__date__ = '20/09/15'


import inspect
from KafNafParserPy import KafNafParser as np
from lxml.etree import XMLSyntaxError
import os
import re
import sys


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


def get_srl_infos_from_naf(naf):
    """
    Parse NAF SRL layer to get relations
    @param dacts: domain actors from config
    @param dpreds: domain predicates from config
    @param coracts: dict of L{md.Actor} hashed by string
    corresponding to L{md.Actor.alabel}
    @param corpreds: dict of L{md.Predicate} hashed by string
    corresponding to L{md.Predicate.label}
    """
    try:
        tree = np(naf)
    except XMLSyntaxError:
        print "!! Document is empty {}".format(os.path.basename(naf))
        return
    try:
        spreds = tree.srl_layer.get_predicates()
    except AttributeError:
        print "!! Error with {}".format(os.path.basename(naf))
        return

    # check for relevant predicates ===========================================

    for pred in spreds:
        tids = pred.get_span().get_span_ids()
        terms = [te for te in tree.term_layer if te.get_id() in tids]
        pred_lemmas = [te.get_lemma() for te in terms]
        pred_wfs = [tree.text_layer.get_wf(te.get_span().get_span_ids()[0])
                    for te in terms]
        pred_surface = ut.detokenize(" ".join([wf.get_text()
                                          for wf in pred_wfs]))
        start, end = ut.get_offsets_for_wfs(pred_wfs)
        for role in pred.get_roles():
            sr = role.get_sem_role()
            # AM-ADV cos need it for "supported by"
            #TODO: add nominal roles
            if sr not in ["AM-LOC"]:
                continue
            role_tids = role.get_span().get_span_ids()
            terms = [te for te in tree.term_layer if te.get_id() in role_tids]
            role_lemmas = [tree.term_layer.get_term(tid).get_lemma()
                           for tid in role.get_span().get_span_ids()]
            role_wfs = [tree.text_layer.get_wf(te.get_span().get_span_ids()[0])
                        for te in terms]
            role_surface = ut.detokenize(" ".join([wf.get_text()
                                                   for wf in role_wfs]))
            role_surface = re.sub("^by ", "", role_surface)
            start, end = ut.get_offsets_for_wfs(role_wfs)
            sentence = role_wfs[0].get_sent()
            print "PRED: {}, {}, {}".format(pred_surface, start, end)
            try:
                print "ROLE: {}, {}, {}".format(role_surface, start, end)
            except (UnicodeDecodeError, UnicodeEncodeError):
                print "ROLE: {}, {}, {}".format(repr(role_surface), start, end)


if __name__ == "__main__":
    #indir = "/home/pablo/projects/ie/out/enb_corefs_out_with_countries/srl"
    indir = "/home/pablo/projects/ie/out/enb_corefs_out_with_countries/srl"
    for fn in os.listdir(indir):
        ffn = os.path.join(indir, fn)
        print ffn
        get_srl_infos_from_naf(ffn)
