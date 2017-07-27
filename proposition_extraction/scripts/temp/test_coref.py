"""To run some tests on NAF coreference layer"""

__author__ = 'Pablo Ruiz'
__date__ = '20/09/15'

import codecs
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


import manage_domain_data as mdd
import utils as ut


def analyze_corefs(naf, dacts, ofd):
    """
    See what possible antecedents you find for pronouns in a sentence.
    - Sort the span terms by their id, numeric
    - Iterate over spans:
        - If find an actor, and a pronoun (see below) in the same or in the
        preceding sentence, print out the infos
    """
    try:
        tree = np(naf)
    except XMLSyntaxError:
        print "!! Document is empty {}".format(os.path.basename(naf))
        return
    try:
        corefs = tree.get_corefs()
    except AttributeError:
        print "!! Error with {}".format(os.path.basename(naf))
        return
    try:
        toks = list(tree.get_tokens())
    except TypeError:
        print "!! Document has no text layer: {}".format(os.path.basename(naf))
        return
    for cr in corefs:
        sorted_list = sorted(list(cr.get_spans()),
            key=lambda s:int(list(s.get_span_ids(
            ))[0].replace("t", "")))
        pairs = []
        actor_sents = {}
        for crs in sorted_list:
            tids = crs.get_span_ids()
            terms = [te for te in tree.term_layer if te.get_id() in tids]
            cr_wfs = [tree.text_layer.get_wf(te.get_span().get_span_ids()[0])
                      for te in terms]
            cr_surface = ut.detokenize(" ".join([wf.get_text() for wf in cr_wfs]))
            if ut.find_argu_in_actors(cr_surface, dacts):
                actor = (cr_surface, [t.get_id() for t in terms])
                actor_sent = int(cr_wfs[0].get_sent())
                actor_sents.setdefault(actor_sent, 1)
            elif re.search(r"\bit\b", cr_surface):
                pronoun = (cr_surface, [t.get_id() for t in terms])
                pronoun_sent = int(cr_wfs[0].get_sent())
                if pronoun_sent in actor_sents or pronoun_sent -1 in actor_sents:
                    pairs.append((actor, pronoun, actor_sent, pronoun_sent))

        for actor, pronoun, actor_sent, pronoun_sent in pairs:
            ofd.write(u"\n{}\n".format("+" * 80))
            ofd.write(u"[{}] {} -- {}\n".format(cr.get_id(), actor, pronoun))
            ofd.write(u"AS: {}\n".format(
                ut.detokenize(" ".join([wf.get_text() for wf in toks
                                  if int(wf.get_sent()) == actor_sent]))))
            ofd.write(u"PS: {}\n".format(
                ut.detokenize(" ".join([wf.get_text() for wf in toks
                                  if int(wf.get_sent()) == pronoun_sent]))))


def main(indir, outdir):
    global dactors
    dactors = mdd.parse_actors()
    if not os.path.exists(indir):
        os.makedirs(indir)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    for fn in os.listdir(indir):
        ffn = os.path.join(indir, fn)
        outfn = os.path.join(outdir, fn)
        print ffn
        with codecs.open(outfn, "w", "utf8") as outfd:
            analyze_corefs(ffn, dactors, outfd)


if __name__ == "__main__":
    #indir = "/home/pablo/projects/ie/out/enb_corefs_out_with_countries/srl"
    indir = "/home/pablo/projects/ie/out/enb_corefs_out/srl"
    outdir = "/home/pablo/projects/ie/out/enb_corefs_out_coref_ana_they"
    #indir = "/home/pablo/projects/ie/out/enb_srlmt_out_2/srl"
    main(indir, outdir)

