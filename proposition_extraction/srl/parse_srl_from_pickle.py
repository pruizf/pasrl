"""
Write out pickled infos output by L{parse_srl.py}
All the module does is *writing* out (not really parsing)
"""

__author__ = 'Pablo Ruiz'
__date__ = '06/11/15'


import codecs
import inspect
import os
import pickle
import re
from string import punctuation
import sys
import time


# app-specific imports --------------------------------------------------------
here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, os.pardir))

import config as cfg
import manage_domain_data as mdd
import model as md
import parse_srl as psrl
import utils as ut

# exp: evaluable format, exp_free: accepts incomplete propositions,
# exp_free_at: accepts incomplete and adds actor types
formats_to_write = {"exp": False, "exp_free": False,
                    "exp_free_at": True}

# postprocess actors or not (filtering some props)
POSPRO = True


def write_sentence_results_exp(sent_txt, inname, prop_cand_group, ofh, actors,
                               sactors, groles, pospro=POSPRO):
    """
    Write out the info for the sentence in format matching evaluation script,
    and skipping props that do not fulfill some criteria (must have an A0 etc.)
    @param sent_txt: sentence text
    @param inname: name of input file (to see it for each sentence)
    @param prop_cand_group: L{PropositionCandidateGroup} for sentence
    @param ofh: open handle to write
    @param actors: dict of domain actors by actor type
    @param sactors: set of DBpedia labels for the actors. It's used to score the
    @param groles: generic roles like "delegates", "participants", "Chair" ...
    proposition for confidence
    """
    # create individual propositions of relevant characteristics
    all_indivs = []
    if prop_cand_group.prop_candidates:
        for prop in prop_cand_group.prop_candidates:
            # skip incomplete props
            if not prop.A0 or not prop.UTT:
                continue
            # skip prop if actor in utt
            #TODO: should it be if actor == utt ?
            utts_with_actor = 0
            for utt in prop.UTT:
                if ut.find_actors_in_argu(actors, utt.surface):
                    utts_with_actor += 1
            if len(prop.UTT) == utts_with_actor:
                continue
            indivs = []
            # sentence id is id of pm for first ok prop
            sent_id = prop.pm.sentence
            # remove non-countries for now
            for a0 in [a for a in prop.A0 if a.atype != "UNK"]:
                pospro_penalty = 0.0
                sorted_utts = sorted([u for u in prop.UTT],
                                     key=lambda usu: usu.start)
                msg = " ".join([u.surface for u in sorted_utts
                                if not ut.find_actors_in_argu(actors,
                                u.surface)])
                # postprocess actors
                if pospro:
                    norm_a0_sfc, pospro_penalty = ut.post_process_prop(
                        a0.surface, prop.pm.surface, msg)
                else:
                    norm_a0_sfc = a0.surface
                # ut.post_process returns False if proposition should be skipped
                if not norm_a0_sfc:
                    continue
                # the filtering can create propositions equal to existing ones
                if (norm_a0_sfc, prop.pm.surface, prop.pm.type, msg) in indivs:
                    continue
                # add confidence score
                conf_sco = ut.score_proposition(
                    norm_a0_sfc, prop.pm.surface, msg,
                    [pospro_penalty], sactors, groles)
                indivs.append((norm_a0_sfc, prop.pm.surface, prop.pm.ptype,
                               msg, conf_sco))
            all_indivs.extend(indivs)
    # write out
    if all_indivs:
        ofh.write(u"{}-{}\t{}\n".format(
            re.sub(r"(\.txt|\.html).+$", r"\1", inname), sent_id, sent_txt))
        for ip in all_indivs:
            ofh.write(u"{}\t{}\t{}\t{}\t{}\n".format(ip[0], ip[1], ip[2], ip[3],
                                                     ip[-1]))
        ofh.write("\n")


def write_sentence_results_exp_free(sent_txt, inname, prop_cand_group, ofh, actors,
                                    sactors, groles, pospro=POSPRO):
    """
    Write out the info for the sentence in format matching evaluation script,
    but without skipping any props.
    @param sent_txt: sentence text
    @param inname: name of input file (to see it for each sentence)
    @param prop_cand_group: L{PropositionCandidateGroup} for sentence
    @param ofh: open handle to write
    @param actors: dict of domain actors by actor type
    @param sactors: set of DBpedia labels for the actors. It's used to score the
    proposition for confidence
    @param groles: generic roles like "delegates", "participants", "Chair" ...
    """
    # create individual propositions of relevant characteristics
    all_indivs = []
    if prop_cand_group.prop_candidates:
        for prop in prop_cand_group.prop_candidates:
            indivs = []
            # sentence id is id of pm for first ok prop
            sent_id = prop.pm.sentence
            # DONT remove non-countries for now (XXXXX never matches)
            for a0 in [a for a in prop.A0 if a.atype != "XXXXX"]:
                pospro_penalty = 0.0
                sorted_utts = sorted([u for u in prop.UTT],
                                     key=lambda usu: usu.start)
                msg = " ".join([u.surface for u in sorted_utts
                                if not ut.find_actors_in_argu(actors,
                                u.surface)])
                # postprocess actors
                if pospro:
                    norm_a0_sfc, pospro_penalty = ut.post_process_prop(
                        a0.surface, prop.pm.surface, msg)
                else:
                    norm_a0_sfc = a0.surface
                # ut.post_process returns False if proposition should be skipped
                if not norm_a0_sfc:
                    continue
                # the filtering can create propositions equal to existing ones
                if (norm_a0_sfc, prop.pm.surface, prop.pm.type, msg) in indivs:
                    continue
                # add confidence score
                conf_sco = ut.score_proposition(
                    norm_a0_sfc, prop.pm.surface, msg,
                    [pospro_penalty], sactors, groles)
                indivs.append((norm_a0_sfc, prop.pm.surface, prop.pm.ptype,
                               msg, conf_sco))
            all_indivs.extend(indivs)
    # write out
    if all_indivs:
        ofh.write(u"{}-{}\t{}\n".format(
            re.sub(r"(\.txt|\.html).+$", r"\1", inname), sent_id, sent_txt))
        for ip in all_indivs:
            # now outputting all fields so would not need to do 0, 1, 2, -1 ...
            ofh.write(u"{}\t{}\t{}\t{}\t{}\n".format(ip[0], ip[1], ip[2], ip[3],
                                                 ip[-1]))
        ofh.write("\n")


def write_sentence_results_exp_free_with_actor_types(
        sent_txt, inname, prop_cand_group, ofh, actors,
        sactors, groles, pointlog, pospro=POSPRO):
    """
    Write out the info for the sentence in format matching evaluation script,
    but without skipping any props, and adding the actor type.
    @param sent_txt: sentence text
    @param inname: name of input file (to see it for each sentence)
    @param prop_cand_group: L{PropositionCandidateGroup} for sentence
    @param ofh: open handle to write
    @param actors: dict of domain actors by actor type
    @param sactors: set of DBpedia labels for the actors. It's used to score the
    proposition for confidence
    @param groles: generic roles like "delegates", "participants", "Chair" ...
    @param pointlog: open handle to log details for finding point in sentence
    """
    # create individual propositions of relevant characteristics
    all_indivs = []
    if prop_cand_group.prop_candidates:
        for prop in prop_cand_group.prop_candidates:
            indivs = []
            # sentence id is id of pm for first ok prop
            sent_id = prop.pm.sentence
            # DONT remove non-countries for now (XXXXX never matches)
            for a0 in [a for a in prop.A0 if a.atype != "XXXXX"]:
                pospro_penalty = 0.0
                sorted_utts = sorted([u for u in prop.UTT],
                                     key=lambda usu: usu.start)
                msg = " ".join([u.surface for u in sorted_utts
                                if not ut.find_actors_in_argu(actors,
                                u.surface)])
                # postprocess actors
                if pospro:
                    norm_a0_sfc, pospro_penalty = ut.post_process_prop(
                        a0.surface, prop.pm.surface, msg)
                else:
                    norm_a0_sfc = a0.surface
                # ut.post_process returns False if proposition should be skipped
                if not norm_a0_sfc:
                    continue
                # the filtering can create propositions equal to existing ones
                if (norm_a0_sfc, a0.atype, prop.pm.surface, prop.pm.ptype,
                    msg) in indivs:
                    continue
                # find point in sentence
                msgstart, msgend = ut.find_point_in_sentence(msg, sent_txt,
                                                             pointlog)
                # add confidence score
                conf_sco = ut.score_proposition(
                    norm_a0_sfc, prop.pm.surface, msg,
                    [pospro_penalty], sactors, groles)
                indivs.append((norm_a0_sfc, a0.atype, prop.pm.surface,
                    prop.pm.ptype, msg, msgstart, msgend, conf_sco))
            all_indivs.extend(indivs)
    # write out
    if all_indivs:
        ofh.write(u"{}-{}\t{}\n".format(
            re.sub(r"(\.txt|\.html).+$", r"\1", inname), sent_id, sent_txt))
        for ip in all_indivs:
            outl = u"\t".join([unicode(it) for it in (
                ip[0], ip[1], ip[2], ip[3], ip[4], ip[5], ip[6], ip[-1])])
            ofh.write("".join((outl, "\n")))
        ofh.write("\n")


def main(pk, outf):
    outf_plus = os.path.splitext(outf)[0] + "_accept_incomplete.txt"
    outf_at = os.path.splitext(outf)[0] + \
              "_accept_incomplete_with_actor_types.txt"
    print "Pkl: {}".format(pk)
    print "Loading pickle: {}".format(
        time.strftime("%H:%M:%S", time.localtime()))
    res = pickle.load(open(pk))
    print "Done: {}".format(time.strftime("%H:%M:%S", time.localtime()))
    dactors = mdd.parse_actors()
    actor_set = mdd.return_set_of_actor_labels()
    gen_set = mdd.return_set_of_generic_labels()
    done_fns = {}
    # file descriptors: ofde is normal ouptut, ofde_plus accepts
    # non-country actors, ofde_actypes additionnally writes actor types
    if formats_to_write["exp"]:
        ofde = codecs.open(outf, "w", "utf8")
        print "Out: {}".format(outf)
    if formats_to_write["exp_free"]:
        ofde_plus = codecs.open(outf_plus, "w", "utf8")
        print "Out (with incomplete): {}".format(outf_plus)
    if formats_to_write["exp_free_at"]:
        ofde_actyps = codecs.open(outf_at, "w", "utf8")
        print "Out (with incomplete with actor types): {}".format(outf_at)
    ptlogfh = codecs.open(cfg.log_for_points_in_sentence, "w", "utf8")
    # avoid overwriting if make manual changes to fnames etc.
    try:
        assert ofde.name != ofde_plus.name
        assert ofde.name != ofde_actyps.name
        assert ofde_plus.name != ofde_actyps.name
    except NameError:
        pass
    for idx, (ffn, sent, sent_infos) in enumerate(res):
        fn = os.path.basename(ffn)
        if fn not in done_fns:
            print "- {}, {}".format(
                fn, time.strftime("%H:%M:%S", time.localtime()))
        done_fns.setdefault(fn, 1)
        prop_cands = md.PropositionCandidateGroup(sent_infos)
        psrl.process_sent_prop_candidates(prop_cands)
        # write out in selected formats
        if formats_to_write["exp"]:
            write_sentence_results_exp(sent, fn, prop_cands, ofde, dactors,
                                       actor_set, gen_set)
        if formats_to_write["exp_free"]:
            write_sentence_results_exp_free(sent, fn, prop_cands, ofde_plus,
                                            dactors, actor_set, gen_set)
        if formats_to_write["exp_free_at"]:
            write_sentence_results_exp_free_with_actor_types(sent, fn,
                prop_cands, ofde_actyps, dactors, actor_set, gen_set, ptlogfh)
    try:
        ofde.close()
        ofde_plus.close()
        ofde_actyps.close()
        ptlogfh.close()
    except NameError:
        pass
    print "Done: {}".format(time.strftime("%H:%M:%S", time.localtime()))


if __name__ == "__main__":
    # pkl = ("/home/pablo/projects/ie/out/pasrl/all_corpus_test_export_format/" +
    #        "all_corpus_test_export_format.pkl")
    # outfn = "/home/pablo/projects/ie/out/pasrl/test_pickle_out_30_jan_actor_postpro_13_with_confsco.txt"
    pkl = ("/home/pablo/projects/ie/out/pasrl/" +
           "enb_missing_four/enb_missing_four.pkl")
    outfn = "/home/pablo/projects/ie/out/pasrl/enb_missing_four_from_pickle.txt"
    main(pkl, outfn)