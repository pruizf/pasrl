"""Parse coreference layer, returning domain relevant coreference candidates"""

__author__ = 'Pablo Ruiz'
__date__ = '06/10/15'

import codecs
import inspect
from KafNafParserPy import KafNafParser as np
import logging
from lxml.etree import XMLSyntaxError
import os
import re
import sys
import time


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, os.pardir))


import config as cfg
import manage_domain_data as mdd
import utils as ut


logger = logging.getLogger(__name__)

#TODO: would 'its' and 'their' be useful?
ANLIST = ["it", "he", "she", "they"]
ANRE = [re.compile(ur"\b{}\b".format(an), re.I|re.U) for an in ANLIST]


def analyze_corefs(naf, dacts, nocorefs, ofd=None):
    """
    See what possible antecedents you find for pronouns in a sentence.
    - Sort the span terms by their id, numeric
    - Iterate over spans:
        - If find an actor, and a pronoun (see below) in the same or in the
        preceding sentence, AND THE ACTOR IS A SBJ in dep layer, print out
    @param naf: naf fn
    @param dacts: domain actors
    @param nocorefs: list of expressions with expletive 'it'
    @param ofd: output file handle
    @return: hash of antecedents by filename, sentence number and anaphoric
    """
    print "{}coref: {}".format(
        " " * 4, time.strftime("%H:%M:%S", time.localtime()))
    try:
        tree = np(naf)
    except XMLSyntaxError:
        print "!! Document is empty {}".format(os.path.basename(naf))
        logger.warn("!! Document is empty {}".format(os.path.basename(naf)))
        return
    try:
        toks = list(tree.get_tokens())
    except TypeError:
        print "!! Document is empty {}".format(os.path.basename(naf))
        logger.warn("!! Document is empty {}".format(os.path.basename(naf)))
        return
    try:
        deps = list(tree.get_dependencies())
    except TypeError:
        print "!! No dep layer"
        logger.warn("!! No dep layer")
        return []
    try:
        corefs = tree.get_corefs()
    except AttributeError:
        print "!! Error with {}".format(os.path.basename(naf))
        return
    out = {}
    out.setdefault(os.path.basename(naf), {})
    for cr in corefs:
        logger.debug("** start coref [{}]".format(cr.get_id()))
        sorted_list = sorted(list(cr.get_spans()),
            key=lambda s: int(list(s.get_span_ids(
            ))[0].replace("t", "")))
        pairs = []
        actor_sents = {}
        for crs in sorted_list:
            has_actor = False
            has_pronoun = False
            has_expletive = False
            tids = crs.get_span_ids()
            logger.debug("{}start cr span {}".format(" " * 4, tids))
            keep = True
            # check if member of coref chain is a subject
            #TODO: restrict to subject of root verb (not in an embedded clause)
            for tid in tids:
                check_deps = [hd for hd in deps if hd.get_to() == tid
                              and hd.get_function() == "SBJ"]
                if check_deps:
                    info = check_deps[0]
                    logger.debug(
                        u"{}deps: from H {} ({}) to D {} ({}) F {}".format(
                        " " * 8, info.get_from(),
                        tree.get_term(info.get_from()).get_lemma(),
                        info.get_to(),
                        tree.get_term(info.get_to()).get_lemma(),
                        info.get_function()))
                if not check_deps:
                    keep = False
            if not keep:
                logger.debug("{}not a subject: {}".format(" " * 8, tids))
                continue
            # if member of coref chain is subject, then go on with it
            terms = [te for te in tree.term_layer if te.get_id() in tids]
            cr_wfs = [tree.text_layer.get_wf(te.get_span().get_span_ids()[0])
                      for te in terms]
            cr_surface = ut.detokenize(" ".join([wf.get_text()
                                                 for wf in cr_wfs]))
            # check for actors
            if ut.find_argu_in_actors(cr_surface, dacts, silent=True):
                actor = (cr_surface, [t.get_id() for t in terms])
                actor_sent = int(cr_wfs[0].get_sent())
                actor_sents.setdefault(actor_sent, 1)
                logger.debug("{}found actor [S{}]: {}".format(" " * 12,
                    actor_sent, actor))
                has_actor = True
            # check for pronouns
            if not has_actor:
                logger.debug("{}no actor".format(" " * 12))
                for ar in ANRE:
                    pronoun_search = re.search(ar, cr_surface)
                    # 'it' requires special treatment cos can be expletive
                    if ar.pattern == r"\bit\b":
                        sent_surface = ut.detokenize(
                            " ".join([wf.get_text() for wf in toks
                                      if wf.get_sent() ==
                                      cr_wfs[0].get_sent()]))
                        # this is called 'expletive_search', but it looks for 'it'
                        # then right below it's checked if that 'it' is expletive
                        expletive_search = re.search(ar, sent_surface)
                        # check if expletive 'it':
                        #   search performed on the whole sentence to see if
                        #   this 'it' coincides with start of an expletive expression
                        for expr in nocorefs:
                            blocker_find = re.search(expr, sent_surface.lower())
                            if (expletive_search and blocker_find and
                                blocker_find.start() == expletive_search.start()):
                                has_expletive = True
                                logger.debug(u"{}expletive %{}%".format(
                                    " " * 12, expr))
                    # check sentence number for actor and pronoun
                    if pronoun_search and not has_expletive:
                        pronoun = (cr_surface, [t.get_id() for t in terms])
                        pronoun_sent = int(cr_wfs[0].get_sent())
                        if (pronoun_sent in actor_sents or
                            pronoun_sent -1 in actor_sents):
                            pairs.append((actor, pronoun, actor_sent,
                                          pronoun_sent))
                            logger.debug("{}found pronoun [S{}]: {}".format(
                                " " * 12, pronoun_sent, pronoun))
                            logger.debug("{}ADDED [AS{}] [PS{}]: {} {}".format(
                                " " * 16, actor_sent, pronoun_sent,
                                actor, pronoun))
                            logger.debug("{}AS: {}".format(" " * 16, ut.detokenize(
                                repr(" ".join(
                                    [wf.get_text() for wf in toks
                                     if int(wf.get_sent()) == actor_sent])))))
                            logger.debug("{}PS: {}".format(" " * 16, ut.detokenize(
                                repr(" ".join(
                                    [wf.get_text() for wf in toks
                                     if int(wf.get_sent()) == pronoun_sent])))))
                            has_pronoun = True
                            # here append to output hash
                            out[os.path.basename(naf)].setdefault(
                                pronoun_sent, {})
                            # hash by tuple of term-ids
                            out[os.path.basename(naf)][int(pronoun_sent)]\
                                [tuple(pronoun[-1])] = tuple(actor[-1])
                if not has_pronoun:
                    logger.debug("{}no pronoun".format(" " * 12))
    return out


def main(indir, outdir):
    """Run"""
    dactors = mdd.parse_actors()
    corblockers = mdd.parse_coref_blockers()
    if not os.path.exists(indir):
        os.makedirs(indir)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    print "In: {}".format(indir)
    print "Out: {}".format(outdir)
    print "Log: {}".format(cfg.norm_log_fn)
    for fn in os.listdir(indir):
        ffn = os.path.join(indir, fn)
        outfn = os.path.join(outdir, fn)
        print ffn
        logger.info("== {} ==".format(ffn))
        with codecs.open(outfn, "w", "utf8") as outfd:
            file_infos = analyze_corefs(ffn, dactors, corblockers, outfd)
            #outfd.write(repr(file_infos))


if __name__ == "__main__":
    def create_log(cf):
        """Create a log for app"""
        logging.basicConfig(filename='{}'.format(cf.norm_log_fn),
            level=cf.loglevel,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    create_log(cfg)
    indir = "/home/pablo/projects/ie/out/enb_corefs_out_norm_pronouns_DEBUG_5oct3"
    #indir = "/home/pablo/projects/ie/out/enb_corefs_out_with_countries/srl"
    #indir = "/home/pablo/projects/ie/out/enb_corefs_out/srl"
    outdir = "/home/pablo/projects/ie/out/enb_corefs_out_coref_ana_role_coref"
    #indir = "/home/pablo/projects/ie/out/enb_srlmt_out_2/srl"
    main(indir, outdir)

