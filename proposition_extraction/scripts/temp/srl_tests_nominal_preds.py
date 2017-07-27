"""To run some tests on NAF SRL layer"""

__author__ = 'Pablo Ruiz'
__date__ = '20/09/15'


import codecs
import inspect
from KafNafParserPy import KafNafParser as np
from lxml.etree import XMLSyntaxError
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


import config as cfg
import manage_domain_data as mdd
import model as md
import utils as ut


def get_srl_infos_from_naf(naf, npreds, outfh):
    """print nominal srl preds and their roles"""
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
        # nominal verbal_preds only have one term
        if len(terms) > 1:
            continue
        if not terms[0].get_pos().startswith("N"):
            continue
        pred_lemmas = [te.get_lemma() for te in terms]
        pred_wfs = [tree.text_layer.get_wf(te.get_span().get_span_ids()[0])
                    for te in terms]
        pred_surface = ut.detokenize(" ".join([wf.get_text()
                                          for wf in pred_wfs]))
        if " ".join(pred_lemmas) not in npreds and pred_surface not in npreds:
            continue

        sent_id = pred_wfs[0].get_sent()
        sent_surface = ut.detokenize(" ".join(
            [tok.get_text() for tok in list(tree.get_tokens())
             if tok.get_sent() == sent_id]))
        try:
            outfh.write("\nS: {}\n".format(sent_surface))
        except (UnicodeEncodeError, UnicodeDecodeError):
            outfh.write("\nS: {}\n".format(repr(sent_surface)))

        p_start, p_end = ut.get_offsets_for_wfs(pred_wfs)
        outfh.write("PRED: {}, {}, {}\n".format(
            pred_surface, p_start, p_end))
        for role in pred.get_roles():
            sr = role.get_sem_role()
            # if sr not in ["AM-LOC"]:
            #     continue
            role_tids = role.get_span().get_span_ids()
            role_terms = [te for te in tree.term_layer if te.get_id() in role_tids]
            role_lemmas = [tree.term_layer.get_term(tid).get_lemma()
                           for tid in role.get_span().get_span_ids()]
            role_wfs = [tree.text_layer.get_wf(te.get_span().get_span_ids()[0])
                        for te in role_terms]
            role_surface = ut.detokenize(" ".join([wf.get_text()
                                                   for wf in role_wfs]))
            r_start, r_end = ut.get_offsets_for_wfs(role_wfs)
            try:
                outfh.write("{} ROLE [{}]: {}, {}, {}\n".format(
                    " " * 4, sr, role_surface, r_start, r_end))
            except (UnicodeDecodeError, UnicodeEncodeError):
                outfh.write("{} ROLE [{}]: {}, {}, {}\n".format(
                    " " * 4, sr, repr(role_surface), r_start, r_end))


def read_nominal_preds(inf):
    preds = {}
    with codecs.open(inf, "r", "utf8") as ifd:
        for ll in ifd:
            if len(ll) > 1:
                preds[ll.strip()] = 1
    return preds


def main(indir, outdir, npreds_fn):
    """Run"""
    #indir = "/home/pablo/projects/ie/out/enb_corefs_out_with_countries/srl"
    print "Indir: {}".format(indir)
    print "Outdir: {}".format(outdir)
    nom_preds = read_nominal_preds(npreds_fn)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    for fn in os.listdir(indir):

        ffn = os.path.join(indir, fn)
        ofn = os.path.join(outdir, fn)
        print "{} {}".format(os.path.basename(ffn), time.strftime(
            "%H:%M:%S", time.localtime()))
        with codecs.open(ofn, "w", "utf8") as outfd:
            outfd.write("{}\n".format(ffn))
            get_srl_infos_from_naf(ffn, nom_preds, outfd)


if __name__ == "__main__":
    #indir = "/home/pablo/projects/ie/out/enb_corefs_out_with_countries/srl"
    indir = "/home/pablo/projects/ie/out/enb_corefs_out/srl"
    outdir = "/home/pablo/projects/ie/out/enb_corefs_out_npreds4"
    nom_preds = "/home/pablo/projects/ie/wk/nominal_preds_raw.txt"
    main(indir, outdir, nom_preds)