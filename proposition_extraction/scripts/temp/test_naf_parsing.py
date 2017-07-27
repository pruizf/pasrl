"""
Test NAF parser from https://github.com/cltl/KafNafParserPy
Has been previously added to Python import path
"""

__author__ = 'Pablo Ruiz'
__date__ = '11/09/15'

import inspect
import os
import sys

from KafNafParserPy import KafNafParser as np

here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, os.pardir))
sys.path.append(os.path.join(os.path.join(here, os.pardir),
                os.pardir))


import utils as ut

#inf = "/home/pablo/projects/ie/out/fcic_srlmt_out_2/srl/CHAIRMAN_ANGELIDES_10_FCIC_HRG.srl"
#inf = "/home/pablo/projects/ie/out/enb_srlmt_out/srl/enb12154e.txt.srl"
#inf = "/home/pablo/projects/ie/out/enb_corefs_out_with_countries/srl/enb1204e.txt.par.coref.srl.naf"
inf = "/home/pablo/projects/ie/out/srl/enb_corefs_out_with_countries/srl/enb1204e.txt.par.coref.srl.naf"
tree = np(inf)
a = 0
if True:
    preds = tree.srl_layer.get_predicates()
    for x in preds:
        #import pdb;pdb.set_trace()
        pred_lemmas = []
        pred_ids = []
        sentence_printed = False
        for id_ in x.get_span().get_span_ids():
            #import pdb;pdb.set_trace()
            pred_ids.append(id_)
            pred_lemmas.append(tree.term_layer.get_term(id_).get_lemma())
        print "## PRED_LEMMAS: {} {}".format(" ".join(pred_lemmas), "-" * 40)
        print "   PRED_IDS: {}".format(repr(pred_ids))
        if len(pred_lemmas) > 1:
            sys.exit(2)
        #import pdb;pdb.set_trace()
        #print x, dir(x)
        if a > 100:
            break
        for y in x.get_roles():
            # cd try a combination of lemma and external ref ...
            # (wd need to lk at the external refs to see which select for each notion ...)
            sent_nbr = None
            lemmas = []
            #import pdb;pdb.set_trace()
            for id_ in y.get_span().get_span_ids():
                lemmas.append(tree.term_layer.get_term(id_).get_lemma())
                if sent_nbr is None:
                    sent_nbr = tree.text_layer.get_wf(
                        tree.term_layer.get_term(id_).get_span().get_span_ids()[0]).get_sent()
            sent_tokens = [tok.get_text() for tok in list(tree.get_tokens())
                           if tok.get_sent() == sent_nbr]
            #print "{}".format("=" * 30)
            # print "GET_ID", dir(y.get_id()), "\n", y.get_id()
            # print "GET_NODE", dir(y.get_node()), "\n", y.get_node()
            # print "GET_SEM_ROLE", dir(y.get_sem_role()), "\n", y.get_sem_role()
            # print ("GET_SPAN", dir(y.get_span()), "\n", y.get_span().get_span_ids(),
            #        y.get_span().node)
            # print "\n{}".format("#" * 20)
            if not sentence_printed:
                print "   >> SENTENCE: {}\n{}".format(sent_nbr, " ".join(sent_tokens))
                sentence_printed = True
            print "   >> SEM_ROLE: {}".format(y.get_sem_role())
            print "      %% SPAN_IDS: {}".format(y.get_span().get_span_ids())
            print "      $$  ROLE_LEMMAS: {}".format(" ".join(lemmas))

            # print "{}\n".format("#" * 20)
            #import pdb;pdb.set_trace()
        a += 1

# an analysis layer (beyond 'text') is composed of spans
# a span is composed of targets that point to another (previous) layer
# get_span_ids() returns a list of the target ids for the element
# with those target ids, you can look up information in the other layers
# so, here:
#   with the get_span_ids() on each coreference span:
#       you go to terms layer, and store terms with the ids you got from coref
#       with those terms, you do get_span_ids() to get their text layer targets
#           voila with the text layer targets you access word-forms and offsets
# if need lemmas, they're on terms layer

if False:
    corl = tree.get_corefs()
    terl = list(tree.get_terms())
    for coref in corl:
        print "== {} ==".format(coref.get_id())
        #spans = [s.get_span_ids() for s in coref.get_spans()]
        spans = coref.get_spans()
        termlist = []
        for sp in spans:
            termlist.append([])
            tids = sp.get_span_ids()
            for tid in tids:
                termlist[-1].append([t for t in terl if t.get_id() == tid][0])
        for terms in termlist:
            wfs = [tree.text_layer.get_wf(
                    term.get_span().get_span_ids()[0]) for term in terms]
            detok = ut.detokenize(" ".join([wf.get_text() for wf in wfs]))
            print detok, wfs[0].get_offset(), str(int(wfs[-1].get_offset()) +
                                                  int(wfs[-1].get_length()))
            # for term in terms:
            #     #import pdb;pdb.set_trace()
            #     wf = tree.text_layer.get_wf(
            #         term.get_span().get_span_ids()[0])
            #     print wf.get_text(), wf.get_offset(), \
            #         str(int(wf.get_offset()) + int(wf.get_length()))
            #print tree.text_layer.get_wf(term[0].get_span().get_span_ids()[0]).get_text()
        #import pdb;pdb.set_trace()
        #lemmas = [[tree.text_layer.get_wf(tid) for tid in span] for span in spans]
        #print lemmas
        #for span in spans:
        #    #for sp in span:
        #    print span.get_id()

