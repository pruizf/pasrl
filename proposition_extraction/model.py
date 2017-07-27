"""
Model for IE demo tasks
"""

__author__ = 'Pablo Ruiz'
__date__ = '18/09/15'

import copy
import inspect
import logging
import os
import re
import sys


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, os.pardir))

import config as cfg

logger = logging.getLogger(__name__)


class Actor(object):
    """
    Actor in the domain
    @ivar label: unique label
    @ivar type: type (e.g. annex I country, banker ...)
    """
    def __init__(self, label, atype):
        self.label = label
        self.atype = atype

    def __unicode__(self):
        return u"{}\t{}".format(self.label, self.atype)

    def __str__(self):
        return self.__unicode__().encode("utf8")


class ActorMention(object):
    """
    Mention of an L{Actor}
    @note: L{Actor.label} is "foreign key"
    @note: for the db model, get atype from the Actor instance,
    i.e. atype is stored as a field of Actor only
    """
    def __init__(self, surface, srole, start, end, sentence, tids):
        self.surface = surface
        self.srole = srole
        self.start = start
        self.end = end
        self.sentence = sentence
        self.tids = tids
        self.label = None
        self.atype = None

    def __unicode__(self):
        return u"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(self.surface,
            self.label, self.atype, self.srole, self.start, self.end,
            self.sentence, self.tids)

    def __str__(self):
        return self.__unicode__().encode("utf8")


class Uttered(object):
    """
    What an L{ActorMention} expresses via a L{PredicateMention}
    E.g. "China, supported by The US, stated that they like the VW Bug"
    Here, "they like the VW Bug" is the uttered element
    """
    def __init__(self, surface, srole, start, end, sentence):
        self.surface = surface
        self.srole = srole
        self.start = start
        self.end = end
        self.sentence = sentence
        self.etype = "UTT"

    def __unicode__(self):
        return u"{}\t{}\t{}\t{}\t{}\t{}".format(self.surface,
            self.etype, self.srole, self.start, self.end, self.sentence)

    def __str__(self):
        return self.__unicode__().encode("utf8")


class Predicate(object):
    """
    Predicate to model the domain
    @ivar label: a unique label
    @ivar ptype: a type among predicate types chosen to model the domain
    @ivar pos: part of speech (n or v)
    """

    def __init__(self, label):
        self.label = label
        self.ptype = None
        self.pos = None
        assert self.pos in cfg.allowed_pred_pos

    def __unicode__(self):
        return u"{}\t{}\t({})".format(self.label, self.ptype, self.pos)

    def __str__(self):
        return self.__unicode__().encode("utf8")


class PredicateMention(object):
    """
    Mention of a L{Predicate}.
    @note: L{Predicate.label} is "foreign key"
    """
    def __init__(self, surface, start, end, sentence, tids):
        self.surface = surface
        self.start = start
        self.end = end
        self.label = None
        self.ptype = None
        self.sentence = sentence
        self.tids = tids
        self.pid = None
        self.pos = None

    def __unicode__(self):
        return u"{}\t{}\t{}\t({})\t{}\t{}\t{}\t{}\t{}".format(self.surface,
            self.label, self.ptype, self.pos, self.start, self.end, self.pid,
            self.sentence, self.tids)

    def __str__(self):
        return self.__unicode__().encode("utf8")


class Relation(object):
    """
    Relates a predicate and argument
    @ivar rtype: type of relation based on the predicate
    @ivar rid: unique id
    @ivar pred: the predicate
    @ivar argus: list of arguments
    @type argus: list
    """
    def __init__(self, rtype, rid, pred, argus):
        self.pred = pred
        self.argus = argus
        self.rtype = rtype
        self.rid = rid
        self.confidence = None

    def __unicode__(self):
        return u"{}\t{}\t{}\t{}".format(self.rtype, self.pred,
                                        "::".join(self.argus),
                                        self.confidence)

    def __str__(self):
        return self.__unicode__().encode("utf8")


class RelationMention(object):
    """
    Mention of a L{Relation}
    @ivar prem: a L{PredicateMention}
    @ivar argm: some L{ActorMention}
    @note: L{Relation.rid} is "foreign key"
    """
    def __init__(self, prem, argms):
        self.prem = prem
        self.argms = argms
        self.rid = None
        self.confidence = None

    def __unicode__(self):
        return u"{}\t{}\t{}".format(self.prem,
                                    "::".join(self.argms),
                                    self.confidence)

    def __str__(self):
        return self.__unicode__().encode("utf8")


class PropositionCandidate(object):
    """
    Proposition, seen as a predicate and its arguments and/or adjuncts
    @ivar paa: dict with predicate, arguments and adjunts
    """
    def __init__(self, paa):
        for ele in ("A0", "A1", "pm", "UTT", "DIS"):
            assert ele in paa
        self.A0 = paa["A0"]
        self.A1 = paa["A1"]
        self.pm = paa["pm"]
        self.UTT = paa["UTT"]
        self.DIS = paa["DIS"]

    def __unicode__(self):
        outlist = [unicode(self.pm)]
        out_A0 = [unicode(a0) for a0 in sorted(
            self.A0, key=lambda a: a.surface)]
        out_A1 = [unicode(a1) for a1 in sorted(
            self.A1, key=lambda a: a.surface)]
        out_UTT = [unicode(utt) for utt in sorted(
            self.UTT, key=lambda u: u.start)]
        outlist.append("\n".join(out_A0))
        outlist.append("\n".join(out_A1))
        outlist.append("\n".join(out_UTT))
        return re.sub("\n{2,}", "\n", "\n".join(outlist))

    def __str__(self):
        return self.__unicode__().encode("utf8")


class PropositionCandidateGroup(object):
    """
    Group whose elements are L{PropositionCandidate} objects.
    """
    def __init__(self, proplist):
        self.prop_candidates = proplist

    def sort_prop_candidates(self):
        return sorted(self.prop_candidates, key=lambda pr: pr.pm.start)

    def remove_prop_candidates(self, p2del):
        """Used to remove proposition candidates"""
        if isinstance(p2del, PropositionCandidate):
            logger.debug("General to remove prep: {}".format(
                unicode(p2del)))
            return [pc for pc in self.prop_candidates if pc != p2del]
        elif isinstance(p2del, list):
            logger.debug("General to remove list: {}".format(
                [unicode(x).replace("\n", "~~") for x in p2del]))
            temp_list = copy.deepcopy(self.prop_candidates)
            for p in p2del:
                temp_list = [pc for pc in temp_list if unicode(pc) != unicode(p)]
            return temp_list

    def remove_prop_candidate_with_message_containing_predicate(self):
        """
        Make up for cases where SRL treats an actor as its utterance.
        """
        filtered = []
        for pr in self.prop_candidates:
            keep = True
            for msg in pr.UTT:
                if re.search(r"\b{}\b".format(pr.pm.surface),
                             msg.surface):
                    try:
                        logger.info("Removing {}||Reason: {}".format(
                            unicode(pr).replace("\n", "~~"),
                            cfg.message_contains_predicate))
                    except UnicodeEncodeError:
                        logger.info("Removing {}||Reason: {}".format(
                            repr(unicode(pr)).replace("\\n", "~~"),
                            cfg.message_contains_predicate))
                    keep = False
            if keep:
                filtered.append(pr)
        self.prop_candidates = filtered

    def create_propositions_from_disagreers(self):
        """
        Create propositions for actors in spans like "opposed by"
        """
        for pc in self.prop_candidates:
            if len(pc.DIS) > 0:
                for da in pc.DIS:
                    dis_pred = copy.deepcopy(pc.pm)
                    if not dis_pred.surface.startswith("not "):
                        dis_pred.surface = "not " + pc.pm.surface
                    if not dis_pred.label.startswith("not "):
                        dis_pred.label = "not " + pc.pm.label
                    if pc.pm.ptype == cfg.spref:
                        dis_pred.ptype = cfg.opref
                    elif pc.pm.ptype == cfg.opref:
                        dis_pred.ptype = cfg.spref
                    dis_prop = PropositionCandidate({
                        #TODO: should ignore the A1 ? (i.e. always empty) pr218
                        "A0": [da], "A1": pc.A1, "UTT": pc.UTT,
                        "pm": dis_pred, "DIS": []})
                    self.prop_candidates.append(dis_prop)
                    logging.debug("Adding DIS Prop: {}".format(
                        repr(unicode(dis_prop)).replace("\n\n", "~~")))

    def combine_prop_candidates_from_group(self):
        """
        Work out new propositions based on incomplete info
        from existing propositions.
        @note: example is
          - The EU, supported by the US, CANADA and JAPAN, and opposed
            by the G-77/CHINA, proposed that the Co-Chairs prepare
            a new draft decision text.
        """
        logging.debug("Prop combination")
        new_props = []
        props_to_remove = []
        # Remove contradictory targets:
        #  - Subject of opposition predicate preceding a reporting predicate
        #    can be removed elsewhere as subject.
        logging.debug("Remove contradictory targets")
        for pc1 in self.prop_candidates:
            if pc1.pm.pos != "V":
                continue
            logging.debug("PRED1: {}".format(pc1.pm.surface))
            for pc2 in self.prop_candidates:
                if pc2.pm.pos != "V":
                    continue
                logging.debug("PRED1: {}".format(pc1.pm.surface))
                if pc1 == pc2:
                    continue
                for p1a0 in pc1.A0:
                    logging.debug("P1A0 {}".format(repr(p1a0.surface)))
                    for p2a1 in pc2.A1:
                        logging.debug("P2A1 {}".format(repr(p1a0.surface)))
                        if p1a0.surface == p2a1.surface:
                            try:
                                if (pc1.pm.ptype == cfg.opref and
                                    pc1.pm.start > pc2.pm.start):
                                    pc2.A1 = [a for a in pc2.A1 if a.surface
                                              != p1a0.surface]
                                    logging.debug(
                                        "New A1 after deletion: {}".format(
                                        [unicode(a1).replace("\n", "~~")
                                        for a1 in pc2.A1]))
                            except IndexError:
                                continue

    def remove_incomplete_prop_candidates(self):
        """
        Remove proposition candidates that don't have a minimum of content
        and can't be completed with info from other preds
        """
        to_remove = []
        has_UTT = False
        for pc in self.prop_candidates:
            if len(pc.UTT) > 0:
                has_UTT = True
                break
        for pc in self.prop_candidates:
            if pc.pm.pos == "V":
                if len(pc.A1) == 0 and len(pc.UTT) == 0 and not has_UTT:
                    to_remove.append(pc)
            elif pc.pm.pos == "N":
                if len(pc.A0) == 0 or len(pc.UTT) == 0:
                    to_remove.append(pc)
        if to_remove:
            logging.debug("Marked to remove as incomplete: {}".format(
                [unicode(pr).replace("\n", "~~") for pr in to_remove]))
            self.prop_candidates = self.remove_prop_candidates(to_remove)

    def remove_redundant_prop_candidates(self):
        """
        Remove 'short' propositions, i.e. for which there is a more
        complete ('long') candidate.
        @note: only requires an A0 to match
        @note: 'completeness' seen ashaving an UTT argument vs not (see code).
        """
        to_remove = []
        short_cands = []
        long_cands = []
        for pc1 in self.prop_candidates:
            for a0 in pc1.A0:
                if bool(len(pc1.UTT)):
                    long_cands.append((a0.surface, pc1.pm.surface, pc1))
                else:
                    short_cands.append((a0.surface, pc1.pm.surface, pc1))
        for sh in short_cands:
            #if (sh[0], sh[1]) in [(a0s, ps) for a0s, ps, pc in long_cands]:
            if sh[0] in [a0s for a0s, ps, pc in long_cands]:
                to_remove.append(sh[-1])
        if to_remove:
            logging.debug("Marked to remove as redundant: {}".format(
                [repr(unicode(pr)).replace("\\n", "~~") for pr in to_remove]))
            self.prop_candidates = self.remove_prop_candidates(to_remove)

    def remove_weaker_prop_candidates(self):
        """
        If find a reporting predicate near a support/oppose predicate, and same actors,
        keep the proposition with the support/oppose rather than the report one
        @note: docstring added later.
        """
        to_remove = []
        for pc in self.prop_candidates:
            if pc.pm.ptype in (cfg.spref, cfg.opref):
                a0s = [a0.surface.lower() for a0 in pc.A0]
                weaker = [
                    pc2 for pc2 in self.prop_candidates
                    if ((sorted([a02.surface.lower() for a02 in pc2.A0]) == a0s)
                         #TODO: move this second part elsewhere
                         or (pc2.A0 and pc2.A0[0].surface.lower()
                             in ("he", "she", "it", "they"))
                       )
                    # may add and if the other one is not also strong
                    and pc != pc2
                ]
                if weaker:
                    weaker_tid = int(weaker[0].pm.tids[0].replace("t", ""))
                    stronger_tid = int(pc.pm.tids[0].replace("t", ""))
                    #TODO: verify 5 as a threshold
                    # maybe "that" should intervene btn them
                    if abs(weaker_tid - stronger_tid) <= 3:
                        if weaker[0].pm.ptype == cfg.rpref:
                            to_remove.append(weaker[0])
                            logging.debug(
                            "Marked to remove as weaker: {}".format(weaker[0]))
                        #TODO: this may change
                        if pc.A0 and pc.A0[0].surface.lower() in (
                                "he", "she", "it", "they"):
                            pc.A0 = weaker[0].A0
        self.prop_candidates = self.remove_prop_candidates(to_remove)

    def create_props_eval_format(self):
        """
        Create dictionary of propositions in format required
        by evaluation script.
        """
        slist = self.sort_prop_candidates()
        all_indivs = []
        for prop in slist:
            indivs = []
            #removes actors of type unknown
            for a0 in [a for a in prop.A0 if a.atype != "UNK"]:
                sorted_utts = sorted([u for u in prop.UTT],
                                     key=lambda usu: usu.start)
                indivs.append((a0.surface, prop.pm.surface,
                               [u.surface for u in sorted_utts]))
            # sort by shorter predicate first, then by actor
            all_indivs.extend(sorted(indivs, key=lambda i: (len(i[1]), i[0])))
        return all_indivs

    def __unicode__(self):
        outstr = []
        slist = self.sort_prop_candidates()
        for idx, prop_cand in enumerate(slist):
            if idx > 0:
                outstr.append("-" * 40)
            outstr.append(u"{}\t{}".format("pm", unicode(prop_cand.pm)))
            for a0 in sorted(prop_cand.A0, key=lambda a: a.surface):
                outstr.append(u"A0\t{}".format(unicode(a0)))
            for a1 in sorted(prop_cand.A1, key=lambda a: a.surface):
                outstr.append(u"A1\t{}".format(unicode(a1)))
            for utt in sorted(prop_cand.UTT, key=lambda u: u.start):
                outstr.append(u"UTT\t{}".format(unicode(utt)))
        return "\n".join(outstr)

    def __str__(self):
        return self.__unicode__().encode("utf8")
