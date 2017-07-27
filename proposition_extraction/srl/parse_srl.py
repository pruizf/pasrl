"""Retrieve infos from NAF SRL layer for actor/predicate combinations of interest"""

__author__ = 'Pablo Ruiz'
__date__ = '18/09/15'

import codecs
import inspect
import logging
from lxml.etree import XMLSyntaxError
import os
import pickle
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
import evaluation as ev
import manage_domain_data as mdd
import model as md
from parse_coref import analyze_corefs, ANLIST, ANRE
import utils as ut


# functions -------------------------------------------------------------------


def get_sentence_nbr_for_term_ids(naf):
    """
    Return hash of sentence numbers by term-id
    """
    try:
        tree = np(naf)
    except XMLSyntaxError:
        print "!! Document is empty {}".format(os.path.basename(naf))
        return
    tid2sent = {}
    for term in naf.get_terms():
        span_ids = term.get_span().get_span_ids()
        wf = tree.get_token(span_ids[0])
        tid2sent[term.get_id()] = int(wf.get_sent())
    return tid2sent


def get_preds_by_sentence_nbr(naf):
    """
    Return hash of predicate-id lists hashed by sentence number
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
    snbr2pred = {}
    for pred in spreds:
        pred_id = pred.get_id()
        tids = pred.get_span().get_span_ids()
        terms = [te for te in tree.term_layer if te.get_id() in tids]
        tokens = [tree.text_layer.get_wf(te.get_span().get_span_ids()[0])
                  for te in terms]

        sent_nbr = int(tree.get_token(tokens[0].get_id()).get_sent())
        snbr2pred.setdefault(sent_nbr, []).append(pred_id)
    return snbr2pred


def find_disagreement_span_in_role(rs):
    """
    Sometimes the roles assigned by SRL contain a predicate that
    contradicts the predicate we're assessing. Work around this problem by finding
    actor mentions in the spans containing another predicate
    @param rs: surface rep for the role (the chain of characters for it)
    """
    opposition_span = ""
    test_for_opposition = re.search(r"\bopposed\b", rs)
    test_for_support = re.search(r"\bsupported\b", rs)
    try:
        mystart = test_for_opposition.start()
        myend = test_for_support.start()
        try:
            assert myend > mystart
        except AssertionError:
            # return up to role end unless 'support' cue after 'opposition' cue
            myend = None
    except AttributeError:
        myend = None
    if test_for_opposition:
        opposition_span = rs[mystart:myend]
    return opposition_span


def get_srl_infos_from_naf(naf, dacts, dpreds, dnpreds, coracts, corpreds, out,
                           sid2pid, coref_infos):
    """
    Parse NAF SRL layer to get relations
    @param dacts: domain actors from config
    @param dpreds: domain verbal predicates from config
    @param dnpreds: domain nominal predicates from config
    @param coracts: dict of L{md.Actor} hashed by string
    corresponding to L{md.Actor.alabel}. Name is abbrev. of 'corpus actors'.
    @param corpreds: dict of L{md.Predicate} hashed by string
    corresponding to L{md.Predicate.label}. Name is abbrev of 'corpus preds'.
    @param out: open handle for output
    @param sid2pid: sentence-id to predicate-id hash
    @param coref_infos: hash with info about pronouns and possible antecedents
    per sentence.

    Yields infos per sentence, using sid2pid.
    """
    try:
        tree = np(naf)
    except XMLSyntaxError:
        print "!! Document is empty {}".format(os.path.basename(naf))
        return
    try:
        spreds = list(tree.srl_layer.get_predicates())
    except AttributeError:
        print "!! Error with {}".format(os.path.basename(naf))
        return

    # check for relevant predicates ===========================================

    for sid, pidlist in sorted(sid2pid.items()):
        if cfg.VERBOSE:
            print "Running Sentence Nbr [{}]".format(sid)
        sent_surface = ""
        chosen_sent_infos = []
        sentpreds = [predo for predo in spreds if predo.get_id() in pidlist]
        for pred in sentpreds:
            skip_pred = False
            candidates = []
            tids = pred.get_span().get_span_ids()
            # store pred term number for treating negation
            pred_tid_nbr = int(tids[-1].replace("t", ""))
            terms = [te for te in tree.term_layer if te.get_id() in tids]
            assert len(terms) == 1
            pred_lemmas = [te.get_lemma() for te in terms]
            pred_pos = terms[0].get_pos()
            # determine predicate type c/o config (report, support, oppose)
            for lem in pred_lemmas:
                if (pred_pos == "V" and lem in dpreds["rep"] or
                    pred_pos == "N" and lem in dnpreds["rep"]):
                    ptype = cfg.rpref
                elif (pred_pos == "V" and lem in dpreds["sup"] or
                      pred_pos == "N" and lem in dnpreds["sup"]):
                    ptype = cfg.spref
                elif (pred_pos == "V" and lem in dpreds["opp"] or
                      pred_pos == "N" and lem in dnpreds["opp"]):
                    ptype = cfg.opref
                else:
                    # pred not relevant
                    skip_pred = True
            if skip_pred:
                continue

            lem = u"{}_{}".format(lem, pred_pos)

            pred_wfs = [tree.text_layer.get_wf(te.get_span().get_span_ids()[0])
                        for te in terms]
            sent_nbr = pred_wfs[0].get_sent()
            sent_surface = ut.detokenize(" ".join(
                [tok.get_text() for tok in list(tree.get_tokens())
                 if tok.get_sent() == sent_nbr]))

            roles = list(pred.get_roles())

            # reject nominal predicates with incomplete info
            if pred_pos == "N":
                srtypes = [ro.get_sem_role() for ro in roles]
                if not "A0" in srtypes and "A1" in srtypes:
                    logging.debug("Incomplete pred (id={}, S{}): {}".format(
                        pred.get_id(), sent_nbr, repr([w.get_text()
                                                       for w in pred_wfs])))
                    continue

            # check for negation ------------------------------

            # negation available from SRL
            has_NEG = False
            for role in roles:
                if role.get_sem_role() == "AM-NEG":
                    logging.debug(
                        "AM-NEG from role: {}".format(repr(sent_surface)))
                    has_NEG = True
                    break

            # negation available from surface forms
            if not has_NEG:
                negation_span = [te for te in tree.term_layer if te.get_id()
                                 in ("t{}".format(pred_tid_nbr - 1),
                                     "t{}".format(pred_tid_nbr - 2))]
                negation_span_surfaces = [tree.text_layer.get_wf(
                                          te.get_span().get_span_ids()[0]).get_text()
                                          for te in negation_span]
                for negcand in negation_span_surfaces:
                    if negcand in cfg.negations:
                        has_NEG = True
                        logging.debug(
                            "Add NEG from span: {}".format(
                            repr(negation_span_surfaces)))
                        break

            # create predicate from model ---------------------

            if has_NEG:
                lem = "not {}".format(lem)
                ptype = cfg.inversions[ptype]
            pr = md.Predicate(lem)
            pr.ptype = ptype
            pr.pos = pred_pos
            corpreds.setdefault(lem, pr)

            # create predicate mention
            pred_surface = ut.detokenize(" ".join([wf.get_text()
                                             for wf in pred_wfs]))
            if has_NEG:
                pred_surface = " ".join(("not", pred_surface))
            p_start, p_end = ut.get_offsets_for_wfs(pred_wfs)
            pm = md.PredicateMention(pred_surface, p_start, p_end,
                                     pred_wfs[0].get_sent(), tids)
            pm.label = corpreds[lem].label
            pm.ptype = corpreds[lem].ptype
            # can't take pos form corpreds cos can have 2 POS for same lemma
            pm.pos = pred_pos
            pm.pid = pred.get_id()
            candidates.append(pm)
            out.write("\n\n{}\n".format("### [{}, {}, s{}] {}".format(
                tids[0], pred.get_id(), pred_wfs[0].get_sent(), "#" * 72)))
            out.write("".join((unicode(pm), "\n")))

            # check for relevant arguments ========================================

            has_A0 = False
            has_A1 = False
            has_A2 = False

            # to stock 'disagreers' (in those 'opposed  by' spans)
            pred_disagreers = []

            for role in roles:

                sr = role.get_sem_role()

                # AM-ADV cos need it for "supported by" / "opposed by"
                # AM-TMP for errors where agent span is in temporal adjunct
                # AM-LOC for errors where agent span is in a LOC, sentence-initially
                if sr not in ["A0", "A1", "A2", "AM-NEG", "AM-ADV", "AM-MNR",
                              "AM-TMP", "AM-PNC", "AM-LOC"]:
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
                r_start, r_end = ut.get_offsets_for_wfs(role_wfs)
                sentence = role_wfs[0].get_sent()

                disagreement_span = find_disagreement_span_in_role(role_surface)

                # Need to check both A0 and A1 c/o passives
                if (
                    (pr.pos == "V" and (sr in ("A0", "A1", "AM-TMP")
                     or (sr == "AM-ADV" and
                             role_surface.lower().startswith("with"))
                     or (sr in ("AM-PNC", "AM-ADV") and
                             role_surface.lower().startswith("for "))
                     or (sr in ("AM-ADV", "AM-MNR") and
                             role_surface.lower().startswith("on behalf"))
                     or (sr in ("AM-LOC") and r_start < pm.start)
                     or (sr == "AM-ADV" and "opposed by" in role_surface)))

                    #or (pr.pos == "N" and (sr in ("A0", "A1")))#, "A3")))
                    or (pr.pos == "N" and (sr in ("A0", "A1", "A3")))
                   ):
                    # check for coreference candidates -------------------------------
                    # if has '=>', anaphor already resolved by normalize_pronouns
                    if (cfg.run_corefs and coref_infos and not
                        "=>" in role_surface):
                        corefs_for_file = coref_infos[os.path.basename(naf)]
                        # corefs for file is a hash {fn: {sent_id: (anaph, antec)}}
                        # from code below looks it is {sent_id: (antec_tok1, ... ,
                        #     antec_tokn)}
                        # so the condition means:
                        #  - if the role is an antecedent (role_tids in corefs_for_ ...)
                        if (int(sid) in corefs_for_file and (tuple(role_tids)) in
                            corefs_for_file[int(sid)]):
                            antecedent = " ".join([tree.get_token(tree.get_term(
                                corefs_for_file[int(sid)][mytid][0]).get_span(
                                ).get_span_ids()[0]).get_text()
                                for mytid in corefs_for_file[int(sid)]])
                            #TODO: change naf object to reflect new surface?
                            # (but useless unless write out)
                            new_role_surface = u"{} [-> {}]".format(role_surface,
                                                                    antecedent)
                            logging.debug(
                                u"Changing role surface: OLD [{}] NEW [{}]".format(
                                role_surface, new_role_surface))
                            role_surface = new_role_surface

                    # find actor in arguments ----------------------------------------
                    logging.debug("Matching domain actors against argus")
                    dmatches = ut.find_actors_in_argu(dacts, role_surface)
                    counter_matches = ut.find_actors_in_argu(dacts,
                                                             disagreement_span)
                    logging.debug("Counter-Matches: {}".format(
                        repr(counter_matches)))

                    if len(dmatches) > 0:
                        for actor_label, actor_type in dmatches:
                            if (actor_label, actor_type) in counter_matches:
                                pred_disagreers.append((actor_label, actor_type))
                                continue
                            coracts.setdefault(actor_label,
                                md.Actor(actor_label, actor_type))
                            am = md.ActorMention(actor_label, sr, r_start, r_end,
                                                 sentence, role_tids)
                            # could reassign roles here (ie. from AM-LOC to A0)
                            # and keep the original role as an attribute on the
                            # actor mention
                            am.label = coracts[actor_label].label
                            am.atype = coracts[actor_label].atype
                            candidates.append(am)
                            logging.debug(
                                "AcInArg AMention |{}| for pred |{}|".format
                                (am, pm))
                            out.write("".join((unicode(am), "\n")))
                    else:
                        # find argument in actors ------------------------------------
                        logging.debug("Matching argus against domain actors")
                        dmatches = ut.find_argu_in_actors(role_surface, dacts)
                        if len(dmatches) > 0:
                            for actor_label, actor_type in dmatches:
                                coracts.setdefault(actor_label,
                                    md.Actor(actor_label, actor_type))
                                am = md.ActorMention(actor_label, sr, r_start,
                                                     r_end, sentence, role_tids)
                                am.label = coracts[actor_label].label
                                am.atype = coracts[actor_label].atype
                                candidates.append(am)
                                out.write("".join((unicode(am), "\n")))
                                logging.debug(
                                    "ArgInAc AMention |{}| for pred |{}|".format
                                    (am, pm))
                        else:
                            # in nominal preds, only accept actor A0 (no "OTHER")
                            if sr == "A0" and pr.pos == "V":
                                am = md.ActorMention(role_surface, sr, r_start, r_end,
                                                     sentence, role_tids)
                                candidates.append(am)
                                out.write("".join((unicode(am), "\n")))
                                has_A0 = True
                                am.atype = "UNK"
                                logging.debug(
                                    "UNK A0 AMention |{}| for pred |{}|".format
                                    (am, pm))
                    # add the "message" (will later filter out for actors in A1)
                    if sr == "A1":
                        uttered = md.Uttered(role_surface, sr, r_start, r_end,
                                             sentence)
                        candidates.append(uttered)
                        out.write("".join((unicode(uttered), "\n")))
                        has_A1 = True
                        logging.debug(
                            "UTT A1 |{}| for pred |{}|".format(uttered, pm))
                    if sr == "A0":
                        has_A0 = True

                # other roles -------------------------------------------
                elif pr.pos == "V" and sr == "A2":
                    keep_A2 = False
                    # urge to
                    if role_surface.split()[0] == "to" and pred_surface.startswith("urge"):
                        keep_A2 = True
                    # call for
                    elif role_surface.split()[0] == "for" and pred_surface.startswith("call"):
                        keep_A2 = True
                    # disagree over
                    elif role_surface.split()[0] in ("over", "about", "on") \
                            and pred_surface.startswith("disagree"):
                        keep_A2 = True

                    elif not has_A1:
                        keep_A2 = True
                    # in the end keeping all A2 as message!
                    keep_A2 = True
                    if keep_A2:
                        uttered = md.Uttered(role_surface, sr, r_start, r_end, sentence)
                        candidates.append(uttered)
                        out.write("".join((unicode(uttered), "\n")))
                        logging.debug(
                            "UTT A2 |{}| for pred |{}|".format(uttered, pm))
                elif pr.pos == "N" and sr == "A3":
                    uttered = md.Uttered(role_surface, sr, r_start, r_end, sentence)
                    candidates.append(uttered)
                    out.write("".join((unicode(uttered), "\n")))
                    logging.debug(
                        "UTT A3 |{}| for nom pred |{}|".format(uttered, pm))

            # Create candidate propositions ===========================================

            disagreers_am = []

            for da in pred_disagreers:
                disagreers_am.append(md.ActorMention(da[0], "A0", None, None,
                                                     sentence, []))
                disagreers_am[-1].atype = da[1]
            disagreers_surfaces = [da[0] for da in pred_disagreers]

            chosen_cands = {"A0": [], "A1": [], "UTT": [], "pm": pm,
                            "DIS": disagreers_am}

            # A0 for actors inside an SRL A0
            chosen_cands["A0"].extend([ca for ca in candidates
                                       if isinstance(ca, md.ActorMention)
                                       and ca.srole == "A0"
                                       and ca.surface not in disagreers_surfaces])

            # A0 reassigned from actors contained in SRL adjunct roles
            chosen_cands["A0"].extend([ca for ca in candidates
                                       # some actors in what srl parses as a
                                       # temporal adjunct
                                       if isinstance(ca, md.ActorMention)
                                       and ca.srole == "AM-TMP"
                                       and ca.surface not in disagreers_surfaces
                                       and pm.pos != "N"])
            chosen_cands["A0"].extend([ca for ca in candidates
                                       # some actors in what srl parses as a
                                       # sentence-initial loc adjunct
                                       if isinstance(ca, md.ActorMention)
                                       and ca.srole == "AM-LOC"
                                       and ca.surface not in disagreers_surfaces
                                       and pm.pos != "N"])
            chosen_cands["A0"].extend([ca for ca in candidates
                                       # some actors in what srl parses as
                                       # different types of adjuncts
                                       if isinstance(ca, md.ActorMention)
                                       and ca.srole in ("AM-ADV", "AM-PNC", "AM-MNR")
                                       and ca.surface not in disagreers_surfaces
                                       and pm.pos != "N"])

            # A1
            chosen_cands["A1"].extend([ca for ca in candidates
                                       if isinstance(ca, md.ActorMention)
                                       and ca.srole == "A1"
                                       and pm.pos != "N"])

            # 'Uttered' instances, or reassign roles as utterances
            chosen_cands["UTT"].extend([ca for ca in candidates
                                       if isinstance(ca, md.Uttered)])
            chosen_cands["UTT"].extend([ca for ca in candidates
                                       # some messages tagged as A2
                                       if isinstance(ca, md.ActorMention)
                                       and ca.srole == "A2"])

            # deduplicate role members
            chosen_cands["A0"] = ut.deduplicate_role_members(chosen_cands["A0"])
            chosen_cands["A1"] = ut.deduplicate_role_members(chosen_cands["A1"])

            # Writeout ============================================================
            out.write(u"{}\n".format("= |{}, {}, {}| {}".format(
                tids[0], pred.get_id(), pred_wfs[0].get_sent(),"=" * 32)))
            # print sentence
            sent_surface = ut.detokenize(" ".join([wf.get_text()
                                         for wf in tree.text_layer
                                         if wf.get_sent() == pm.sentence]))
            out.write(u"> {}\n".format(sent_surface))
            # print extracted infos
            out.write(u"  - Source: {}\n".format(", ".join(sorted(set([ca.surface for
                                                 ca in chosen_cands["A0"]])))))
            out.write(u"  - Position: {} [{}]\n".format(pm.ptype, pm.surface))
            out.write(u"  - Target: {}\n".format(", ".join(sorted(set([ca.surface for
                                                 ca in chosen_cands["A1"]])))))
            out.write(u"  - Message: {}\n".format(", ".join(set([ca.surface for
                                                 ca in chosen_cands["UTT"]]))))
            chosen_cands_obj = md.PropositionCandidate(chosen_cands)
            chosen_sent_infos.append(chosen_cands_obj)
        yield sent_surface, chosen_sent_infos


def process_sent_prop_candidates(pclist):
    """
    Choose the best among a sentence's propositions as returned by SRL
    (A proposition is seen as a predicate and its roles)
    @param pclist: L{md.PropositionCandidateGroup} with props for sentence
    """
    pclist.remove_prop_candidate_with_message_containing_predicate()
    #pclist.combine_prop_candidates_from_group()
    pclist.create_propositions_from_disagreers()
    pclist.remove_incomplete_prop_candidates()
    pclist.remove_redundant_prop_candidates()
    pclist.remove_weaker_prop_candidates()


def write_sentence_results(sent_txt, inname, prop_cand_group, ofh):
    """
    Write out the info for the sentence.
    @param sent_txt: sentence text
    @param inname: name of input file (to see it for each sentence)
    @param prop_cand_group: L{PropositionCandidateGroup} for sentence
    @param ofh: open handle to write
    """
    if prop_cand_group.prop_candidates or sent_txt:
    #if len(prop_cand_group.prop_candidates) > 0:
        ofh.write(u"{} [{}] {}\n".format(
            "*" * 4, os.path.basename(inname), "*" * 70))
        ofh.write(u"{}\n".format(sent_txt))
        ofh.write(unicode(prop_cand_group))
        ofh.write("\n")


def write_sentence_results_exp(sent_txt, inname, prop_cand_group, ofh,
                               actors):
    """
    Write out the info for the sentence in format matching evaluation script,
    and skipping props that do not fulfill some criteria (must have an A0 etc.)
    @param sent_txt: sentence text
    @param inname: name of input file (to see it for each sentence)
    @param prop_cand_group: L{PropositionCandidateGroup} for sentence
    @param ofh: open handle to write
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
                sorted_utts = sorted([u for u in prop.UTT],
                                     key=lambda usu: usu.start)
                indivs.append((a0.surface, prop.pm.surface, prop.pm.ptype,
                    " ".join([u.surface for u in sorted_utts
                              if not ut.find_actors_in_argu(actors,
                              u.surface)])))
            # sort by shorter prgiedicate first, then by actor
            #all_indivs.extend(sorted(indivs, key=lambda i: (len(i[1]), i[0])))
            all_indivs.extend(indivs)
    # write out
    if all_indivs:
        ofh.write(u"{}-{}\t{}\n".format(
            #inname.replace(".par.coref.srl.naf", ""), sent_id, sent_txt))
            re.sub(r"(\.txt|\.html).+$", r"\1", inname), sent_id, sent_txt))
        for ip in all_indivs:
            ofh.write(u"{}\t{}\t{}\n".format(ip[0], ip[1], ip[-1]))
        ofh.write("\n")


def create_log(cf):
    """Create a log for app"""
    logging.basicConfig(filename='{}'.format(cf.logfn), level=cf.loglevel,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def main(evalu=cfg.is_eval):
    """Run"""
    global corpus_actors
    global corpus_preds
    global res4eval   # debug
    global fres4eval  # debug
    # logging
    create_log(cfg)
    # IO --------------------------------------
    try:
        inputdir = sys.argv[1]
    except IndexError:
        inputdir = cfg.srlres
    try:
        mybatchname = sys.argv[2]
    except IndexError:
        mybatchname = cfg.batchname
    try:
        outdir = sys.argv[3]
    except IndexError:
        outdir = cfg.outdir.format(mybatchname)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    print "In: {}".format(inputdir)
    print "Out: {}".format(outdir)
    print "Log: {}".format(cfg.logfn)
    print "Comment: {}".format(cfg.comment)
    logging.info("In: {}".format(inputdir))
    logging.info("Out: {}".format(outdir))
    logging.info("Batch: {}".format(cfg.batchname))
    logging.info("Comment: {}".format(cfg.comment))
    # Processing --------------------------------
    dactors = mdd.parse_actors()
    dpreds = mdd.parse_verbal_predicates()
    dnpreds = mdd.parse_nominal_predicates()
    anticoref = mdd.parse_coref_blockers()
    # corpus-level hashes
    corpus_actors = {}
    corpus_preds = {}
    # for evaluation
    if evalu:
        res4eval = {}
    # to pickle results
    if cfg.pickle_results:
        res4pkl = []
    # process
    dones = 0
    for fn in os.listdir(inputdir):
        # IO
        ffn = os.path.join(inputdir, fn)
        ofn = os.path.join(outdir, fn)
        ofna = os.path.join(outdir, os.path.splitext(fn)[0] + "_ana" +
                            os.path.splitext(fn)[1])
        ofne = os.path.join(outdir, os.path.splitext(fn)[0] + "_exp" +
                            os.path.splitext(fn)[1])
        print u"- {}: {}".format(os.path.basename(ffn),
                                 time.asctime(time.localtime()))
        logging.info(os.path.basename(ffn))
        if cfg.skip_dones:
            if os.path.exists(ofn) and os.stat(ofn) > 0:
                print "  Skipping"
                logging.info("Skipping")
                continue
            if os.path.exists(ofna):
                print "  Skipping"
                logging.info("Skipping")
                continue
        # Processing
        with codecs.open(ofn, "w", "utf8") as ofd, \
             codecs.open(ofna, "w", "utf8") as ofda, \
             codecs.open(ofne, "w", "utf8") as ofde:
            # get coreference info for file
            if cfg.run_corefs:
                coref_infos = analyze_corefs(ffn, dactors, anticoref)
            else:
                coref_infos = []
            # hash of pred-id by sent-id (so that can work per sentence)
            sent_id_to_pred_id = get_preds_by_sentence_nbr(ffn)
            # obtain SRL infos per sentence
            for idx, (sent, sent_infos) in enumerate(get_srl_infos_from_naf(
                    ffn, dactors, dpreds, dnpreds, corpus_actors,
                    corpus_preds, ofd, sent_id_to_pred_id, coref_infos)):
                prop_cands = md.PropositionCandidateGroup(sent_infos)
                # treat the infos
                process_sent_prop_candidates(prop_cands)
                # add to list for pickle
                if cfg.pickle_results:
                    res4pkl.append((ffn, sent, sent_infos))
                # writeout
                write_sentence_results(sent, fn, prop_cands, ofda)
                write_sentence_results_exp(sent, fn, prop_cands, ofde, dactors)
                # write eval format
                if evalu:
                    res4eval[(idx + 1, sent)] = \
                        prop_cands.create_props_eval_format()
        # format testset
        if cfg.is_eval:
            dactors4eval = ev.normalize_actors_for_evaluation(dactors)
            golres = ev.read_golden(domain_actors=dactors4eval)
            fres4eval = ev.format_annot_dict(res4eval)
            metrics = ev.score_results(golres, fres4eval)
            ev.print_results(metrics, golres, fres4eval)
            ev.write_results(metrics, golres, fres4eval)
            ev.error_analysis(golres, fres4eval)
        dones += 1
        if dones >= cfg.todo:
            print "Done: {}".format(time.asctime(time.localtime()))
            break
    if cfg.is_eval:
        ev.dump_results(fres4eval, cfg.system_exported)

    print "Done: {}".format(time.asctime(time.localtime()))
    if cfg.pickle_results:
        pickle.dump(res4pkl, open(cfg.respkl, "w"))


if __name__ == "__main__":
    main()