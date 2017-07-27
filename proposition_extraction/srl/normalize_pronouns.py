"""
To normalize personal pronouns that refer to a country as the country.
General idea is:
L{get_sentence_infos_with_deps} will provide candidate antecedents (very limited
set of contexts that are useful for this corpus).
L{normalize pronouns} will verify if there are pronouns that can be considered
to corefer with those candidate antecedents.
"""

__author__ = 'Pablo Ruiz'
__date__ = '02/10/15'

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

import config as cfg
import manage_domain_data as mdd
import utils as ut


# functions -------------------------------------------------------------------


def find_actor_variants_in_argu(actors, argu):
    """
    Find a variant for an actor from domain data inside surface form
    """
    founds = {}
    for actortype, defined_actors in actors.items():
        for dblabel, variants in defined_actors.items():
            for variant in variants:
                mymatch = re.search(re.compile(
                    ut.ACTARG.format(ut.rgescape(variant)),
                    re.I|re.U), argu)
                if mymatch:
                    # need variant as key cos use it to search against
                    # word-forms in the dep-based workflow below
                    founds[variant] = (mymatch.start(), mymatch.end(),
                                       dblabel)
                    #founds[dblabel] = (mymatch.start(), mymatch.end())
    return founds


def get_sentence_infos(nafo, dacts):
    """
    Return sentence number, its first token, and first actor
    found in sentence
    """
    infos = []
    try:
        toks = list(nafo.get_tokens())
    except TypeError:
        print "!! No tok layer"
        logging.info("!! No tok layer")
        return []
    total_sents = max([int(wf.get_sent()) for wf in toks])
    for snbr in range(total_sents + 1)[1:]:
        wfos = [wf for wf in toks if int(wf.get_sent()) == snbr]
        wfs = [wfo.get_text() for wfo in wfos]
        sent_surface = ut.detokenize(" ".join(wfs))
        actors = find_actor_variants_in_argu(dacts, sent_surface)
        # sort by start of match
        s_actors = sorted(actors, key=lambda a: actors[a][0])
        if s_actors:
            infos.append({"snbr": snbr, "iniac": s_actors[0],
                          "iniwf": wfs[0], "iniwf_id": wfos[0].get_id()})
        else:
            infos.append({"snbr": snbr, "iniac": [],
                          "iniwf": wfs[0], "iniwf_id": wfos[0].get_id()})
    return infos


def get_sentence_infos_with_deps(nafo, naffn, dacts):
    """
    For each actor-variant matched in the surface of a sentence,
    if the actor is a SBJ in dependecy layer, return list of dicts
    with sentence-number, the first token in the sentence, and term-id(s)
    for the actors
    @param nafo: naf object
    @param naffn: filename for the naf object
    @param dacts: dict with domain actors
    @rtype: list
    """
    #TODO: take the SBJ of ROOT (mb via taking shortest shortest-path to ROOT)
    infos = []
    try:
        toks = list(nafo.get_tokens())
    except TypeError:
        print "!! No tok layer"
        logging.warn("!! No tok layer")
        return []
    total_sents = max([int(wf.get_sent()) for wf in toks])
    try:
        deps = list(nafo.get_dependencies())
    except TypeError:
        print "!! No dep layer"
        logging.warn("!! No dep layer")
        return []
    for snbr in range(total_sents + 1)[1:]:
        nodeps = True
        # note: could exploit the 'lemma' attribute from the term (pos) layer
        #       instead of matching on wf (tokens) and mapping to terms
        wfos = [wf for wf in toks if int(wf.get_sent()) == snbr]
        wfs = [wfo.get_text() for wfo in wfos]
        sent_surface = ut.detokenize(" ".join(wfs))
        # match actors against wf
        actor_matches_dico = find_actor_variants_in_argu(dacts, sent_surface)
        #     workaround for china/g-77 pb
        actor_matches_dico = ut.workaround_variant_with_slash(
            actor_matches_dico)
        if actor_matches_dico:
            logging.debug("*" * 40)
            logging.info("[{}] S {}".format(os.path.basename(naffn), snbr))
            logging.debug(sent_surface)
            logging.debug(sorted(actor_matches_dico.items(), key=lambda it: it[1]))
        # check if the actor is a subject
        for sa, actor_infos in actor_matches_dico.items():
            split_sa = sa.split()
            wfos_for_actor = []
            #TODO: wont' work for cases like 'the EU' when there's another 'the' earlier
            #in sentence. Just iterate over possible "start_wfo" and take longest!
            #(i.e. don't take start_wfo[0], iterate over start_wfo)
            start_wfo = [wfo for wfo in wfos
                         if wfo.get_text().strip().lower() ==
                         split_sa[0].strip().lower()]
            # looks like getting term-ids for each of the actor's tokens
            if start_wfo:
                # i guess HERE is where id' iterate over the start_wfo
                # instead of taking the first one
                wfos_for_actor.append(start_wfo[0])
                try:
                    j = 1
                    while split_sa[j].strip().lower() == \
                        wfos[wfos.index(start_wfo[0]) + j].get_text().strip().lower():
                        wfos_for_actor.append(wfos[wfos.index(start_wfo[0]) + j])
                        j += 1
                except IndexError:
                    pass
            if wfos_for_actor:
                logging.debug(u"- {} {}".format(sa, actor_infos))
                logging.debug(u"{}wfoall {}".format(" " * 4, [x.get_text()
                                                    for x in wfos_for_actor]))
            else:
                logging.debug(u"- {} {}: no wf matches".format(sa, actor_infos))

            terms_for_actor = [[te for te in nafo.term_layer
                               if wfo.get_id() in te.get_span().get_span_ids()]
                               for wfo in wfos_for_actor]
            flattened_terms = []
            for term_list in terms_for_actor:
                flattened_terms.extend(term_list)
            terms_for_actor = flattened_terms
            # sanity
            try:
                assert not (wfos_for_actor and not terms_for_actor)
            except AssertionError:
                import pdb;pdb.set_trace()
            if not terms_for_actor:
                #print "    no terms"
                continue
            logging.debug(u"{}terms for actor {}".format(
                " " * 8, [x.get_id() for x in terms_for_actor]))
            #TODO: accumulate SBJ and take the SBJ of ROOT (shortest paths)
            for tfa in terms_for_actor:
                logging.debug(u"{}checking deps for {}".format(
                    " " * 12, tfa.get_id()))
                check_deps = [hd for hd in deps if hd.get_to() == tfa.get_id()
                              and hd.get_function() == "SBJ"]
                if check_deps:
                    assert len(check_deps) == 1
                    info = check_deps[0]
                    logging.debug(u"{}DEPS: from H {} ({}) to D {} F {}".format(
                        " " * 16, info.get_from(),
                        nafo.get_term(info.get_from()).get_lemma(),
                        info.get_to(), info.get_function()))
                    # still calling it iniac ('initial actor') but it's a SBJ actor,
                    # not really the first actor ('initial') in the sentence
                    # actor_infos[-1] is dbpedia label, use 'sa' for lc mention
                    infos.append({"snbr": snbr, "iniac": actor_infos[-1],
                                  "iniwf": wfs[0], "iniwf_id": wfos[0].get_id()})
                    nodeps = False
        if nodeps:
            infos.append({"snbr": snbr, "iniac": [],
                          "iniwf": wfs[0], "iniwf_id": wfos[0].get_id()})
    return infos


def normalize_pronouns(naf, dacts, simple=False):
    """
    Replace personal pronouns (he/she) that likely refer to a country with a
    mention to the country.
    Pronouns have to be in the initial position of a sentence following the
    sentence of the antededent. Iterate while there's a pronoun in that first
    position.
    @param naf: path to a naf file
    @param dacts: dictionary of domain actors
    @param simple:
        - True normalizes to first actor in sentence preceding anaphor.
        - False normalizes to subject in sentence preceding anaphor.
    """
    try:
        tree = np(naf)
    except XMLSyntaxError:
        print "!! Document is empty {}".format(os.path.basename(naf))
        logging.warn("!! Document is empty {}".format(os.path.basename(naf)))
        return
    if simple:
        sent_infos = get_sentence_infos(tree, dacts)
    else:
        sent_infos = get_sentence_infos_with_deps(tree, naf, dacts)
    for idx, si in enumerate(sent_infos):
        i = 1
        if si["iniac"]:
            # here compare with later actors ....
            try:
                while sent_infos[idx + i]["iniwf"].lower() in ("he", "she"):
                    new_wf_text = u"{} [=> {}]".format(
                        sent_infos[idx + i]["iniwf"], si["iniac"])
                    tree.get_token(sent_infos[idx + i]["iniwf_id"]).set_text(
                        new_wf_text)
                    logging.debug(
                        u"Replacing text for wf [{}]. OLD [{}]. NEW [{}]".format(
                        sent_infos[idx + i]["iniwf_id"],
                        sent_infos[idx + i]["iniwf"]))
                    i += 1
            except IndexError:
                continue
    return tree


def create_log(cf):
    """Create a log for app"""
    logging.basicConfig(filename='{}'.format(cf.norm_log_fn),
        level=cf.loglevel,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def main(inputdir, outdir):
    """Run"""
    create_log(cfg)
    print "In: {}".format(inputdir)
    print "Out: {}".format(outdir)
    print "Log: {}".format(cfg.norm_log_fn)
    logging.debug("In: {}".format(inputdir))
    logging.debug("Out: {}".format(outdir))
    logging.debug("Log: {}".format(cfg.norm_log_fn))
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    dactors = mdd.parse_actors()
    # process
    dones = 0
    for fn in os.listdir(inputdir):
        ffn = os.path.join(inputdir, fn)
        ofn = os.path.join(outdir, fn)
        print u"{} {}: {} {}".format("=" * 2, os.path.basename(ffn),
                                     time.asctime(time.localtime()), "=" * 2)
        logging.info(os.path.basename(ffn))
        norm_tree = normalize_pronouns(ffn, dactors)
        try:
            norm_tree.dump(ofn)
        except AttributeError:
            continue
        dones += 1
        if dones >= cfg.todo:
            print "Done: {}".format(time.asctime(time.localtime()))
            break


if __name__ == "__main__":
    check_log = raw_input("Need to change name for log? (Y/N) ")
    if check_log == "Y":
        print "- Exiting."
        sys.exit()
    else:
        pass
    try:
        inputdir = sys.argv[1]
    except IndexError:
        # these are from 'with_countries', that i want to normalize to get results
        # for the missing documents
        inputdir = "/home/pablo/projects/ie/out/srl/enb_ie_missing_one/srl"
        #inputdir = "/home/pablo/projects/ie/out/srl/enb_to_add_no_summaries"
        #inputdir = "/home/pablo/projects/ie/out/srl/enb_to_add"
        # inputdir = "/home/pablo/projects/ie/out/enb_corefs_out/srl"
        #inputdir = "/home/pablo/projects/ie/corpora/coref"
    try:
        outdir = sys.argv[2]
    except IndexError:
        outdir = "/home/pablo/projects/ie/out/srl/enb_ie_missing_one_norm_pronouns"
        #outdir = "/home/pablo/projects/ie/out/srl/enb_to_add_no_summaries_norm_pronouns_20160330"
        #outdir = "/home/pablo/projects/ie/out/enb_to_add_norm_pronouns_20160330"
        #outdir = "/home/pablo/projects/ie/out/enb_corefs_out_norm_pronouns_DEBUG_5oct3"
        #outdir = "/home/pablo/projects/ie/out/coref_pbs4"
    main(inputdir, outdir)
