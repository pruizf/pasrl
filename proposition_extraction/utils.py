"""General tools for app"""

import inspect
import logging
from lxml import etree
import os
import re
import string
import sys


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)

import config as cfg

logger = logging.getLogger(__name__)

DBG = False

# to match arguments and actors
ACTARG = ur"\b{}\b"

# don't produce a match based on this subpart of an actor!
#TODO: create config for this
DONTMATCH = {"country": 1, "group": 1, "committee": 1,
             "african": 1, "european": 1, "american": 1,
             "developed country": 1, "states": 1,
             "guinea": 1}


def sqlesc(st):
    """Avoid sql errors"""
    st = st.replace("'", r"\'")
    st = st.replace('"', r'\"')
    return st


def rgescape(st):
    """Avoid regex errors (unbalanced parenthesis, escaping etc)"""
    st = st.replace("(", r"\(")
    st = st.replace(")", r"\)")
    st = st.replace("[", r"\[")
    st = st.replace("]", r"\]")
    st = st.replace("+", r"\+")
    st = st.replace("*", r"\*")
    return st


def atoi(text):
    """https://stackoverflow.com/questions/5967500"""
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    https://stackoverflow.com/questions/5967500
    http://nedbatchelder.com/blog/200712/human_sorting.html
    """
    return [atoi(c) for c in re.split('(\d+)', text)]


def setup(odir=cfg.outdir, runname=cfg.batchname):
    """Initial operations like creating output dirs"""
    if odir != cfg.outdir and runname != cfg.batchname:
        odirfull = os.path.join(odir, runname)
    else:
        odirfull = cfg.outdir
    if not os.path.isdir(odirfull):
        os.mkdir(odirfull)
        if runname == os.path.basename(odir):
            runname = ""
        logger.info("- Created output directories: {}/{}".format(odir, runname))
        print "- Created output directories: {}/{}".format(odir, runname)


def detokenize(txt):
    """Return detokenized text"""
    openers = ["(", "["]
    for pc in string.punctuation:
        if pc == "%":
            pc == "%%"
        txt = txt.replace(r" %s" % pc, pc)
    txt = re.sub(r"(\S)(``) ?", "\g<1> \g<2>", txt)
    for op in openers:
        txt = txt.replace("%s " % op, " %s" % op)
    return txt


def get_offsets_for_wfs(wfs):
    """Return start an end of a NAF/KAF word-form sequence"""
    return wfs[0].get_offset(), \
           int(wfs[-1].get_offset()) + int(wfs[-1].get_length())


def find_argu_in_actors(argu, actors, silent=False):
    """
    Find surface form of an argument in the domain actors dicos
    created with L{manage_domain_data}
    @note: this does not apply, it's L{find_actors_in_argu} that applies
    """
    founds = {}
    argu = argu.lower()
    for actortype, defined_actors in actors.items():
        for dblabel, variants in defined_actors.items():
            for variant in variants:
                mymatch = re.search(re.compile(
                    ACTARG.format(rgescape(argu)), re.I|re.U), variant)
                if mymatch and mymatch.group().lower().strip() in DONTMATCH:
                    if not silent:
                        logger.debug("::Skip Argu in Actor: {}".format(
                            mymatch.group()))
                    continue
                if mymatch:
                    founds.setdefault((dblabel, actortype), 1)
                    if not silent:
                        logger.debug("::Found Argu in Actor: {}".format(
                            mymatch.group()))
    return founds


def find_actors_in_argu(actors, argu, silent=False):
    """
    Find a variant for an actor from domain data inside word-forms
    of an OIE/SRL argument
    """
    founds = {}
    for actortype, defined_actors in actors.items():
        for dblabel, variants in defined_actors.items():
            for variant in variants:
                mymatch = re.search(re.compile(
                    ACTARG.format(rgescape(variant)), re.I|re.U), argu)
                if mymatch and mymatch.group().lower().strip() in DONTMATCH:
                    if not silent:
                        logger.debug("::Skip Variant in Argu: {}".format(
                            mymatch.group()))
                    continue
                if mymatch:
                    founds.setdefault((dblabel, actortype), 1)
                    if not silent:
                        logger.debug("::Found Variant in Argu: {}".format(
                            mymatch.group()))
    return founds


def deduplicate_role_members(candlist):
    """
    Given a list with L{model.PropositionCandidate}, remove
    duplicates based on the label attribute.
    """
    filtered = []
    slist = sorted(candlist, key=lambda ca: ca.label)
    elist = enumerate(slist)
    for idx, ca in elist:
        try:
            if (ca.label == slist[idx+1].label
                and ca.label is not None
                and slist[idx+1].label is not None):
                try:
                    logger.debug(
                        "Dedup role members, Filter out {}".format(
                            unicode(ca)))
                except (UnicodeDecodeError, UnicodeEncodeError):
                    logger.debug(
                        "Dedup role members, Filter out {}".format(
                            repr(ca)))
                pass
            else:
                filtered.append(ca)
        except IndexError:
            filtered.append(ca)
    return filtered


def find_sublist(sub, bigger):
    """
    Find subsequence
    https://stackoverflow.com/questions/2250633
    """
    if not bigger:
        return -1
    if not sub:
        return 0
    first, rest = sub[0], sub[1:]
    pos = 0
    try:
        while True:
            pos = bigger.index(first, pos) + 1
            if not rest or bigger[pos:pos+len(rest)] == rest:
                return pos
    except ValueError:
        return -1


def workaround_variant_with_slash(matches_dico):
    """
    When match variants against actor candidates, it's useful to match
    china/g77 and its variants as a single actor.
    """
    lckeys = [k.lower() for k in matches_dico]
    if "china" in lckeys and (
        "g-77" in lckeys or "g77" in lckeys or
        "g -77" in lckeys or "g- 77" in lckeys or "g 77" in lckeys):
        matches_dico["china/g-77"] = (None, None, "CHINA/G-77")
        matches_dico["china/g -77"] = (None, None, "CHINA/G-77")
        matches_dico["china/g- 77"] = (None, None, "CHINA/G-77")
        matches_dico["china/g77"] = (None, None, "CHINA/G-77")
        matches_dico["g-77/china"] = (None, None, "G-77/CHINA")
        matches_dico["g -77/china"] = (None, None, "G-77/CHINA")
        matches_dico["g- 77/china"] = (None, None, "G-77/CHINA")
        matches_dico["g77/china"] = (None, None, "G-77/CHINA")
    return matches_dico


def filter_actor(sfc):
    """
    Filter actors based on surface characteristics. This is because,
    when accepting non-canonical actors, SRL errors (or even tokenization ones)
    result in aberrant roles.
    """
    bkp = sfc
    sno = sfc
    goon = True
    penalty = 0
    # remove part before : if in parens
    test = re.match(ur"^\([^)]+\):?\s(.+)]", sfc)
    if test:
        sno = test.group(2)
        goon = True
    # remove parentheses
    if goon:
        test = re.search(ur"\s*\(\)\s*", sno)
        if test:
            sno = re.sub(ur"\(\)", "", sno)
            goon = True
    # skip a proposition where surface starts or end with an unmatched parens
    if goon:
        test = sno[0] in ("(", ")") and \
               (sno[-1] not in ("(", ")") or sno[-1] == sno[0])
        if test:
            return False, False
        else:
            goon = True
    if goon:
        test = sno[-1] in ("(", ")") and \
               (sno[0] not in ("(", ")") or sno[-1] == sno[0])
        if test:
            return False, False
        else:
            goon = True
    if goon:
        if "HIGHLIGHTS" in sno.upper():
            return False, False
        else:
            goon = True
    # keep only what follows colon
    sno = re.sub(ur"^.+:", "", sno).strip()
    # "On development and ...., " keep what follows
    sno = re.sub(ur"^On.+, :", "", sno).strip()
    # "Following ...., " keep what follows
    sno = re.sub(ur"^Following.+, :", "", sno).strip()
    # , which
    sno = re.sub(ur", which$", "", sno).strip()
    sno.strip(string.punctuation)
    if len(sno) == 1:
        return False, False
    # very specific cases
    if re.search(r"199[59]", sno):
        return False, False
    if sno and sno[0] in {"(", ":", "`", "/"}:
        return False, False
    if sno and sno[0].isdigit():
        return False, False
    if "adopted without amendment" in sno:
        return False, False
    if sno != bkp:
        if DBG:
            print u"FILTER: [{}] => [{}]".format(bkp, sno)
        penalty = 1
    return sno, penalty


def remove_pred_and_point_from_actor(ac, pr, pnt):
    """
    Some actors (A0 roles) contain the predicate and the point
    as well. Remove them.
    @param ac: actor surface
    @param pr: predicate surface
    @param pnt: point surface
    """
    penalty = 0
    has_pred = ac.find(pr)
    has_point = ac.find(pnt)
    if has_pred <= has_point and has_pred > 0:
        acno = ac[0:has_pred].strip()
    elif has_point <= has_pred and has_point > 0:
        acno = ac[0:has_point].strip()
    else:
        acno = ac
    if acno != ac:
        penalty = 1
        if DBG:
            print u"REMOVE: [{}] => [{}]".format(ac, acno)
    return acno, penalty


def post_process_prop(ac, pr, pnt):
    """
    Apply the actor filtering and actor cleanup in this same module.
    If returns False, intepret this as meaning that the proposition
    needs to not be output.
    @param ac: actor surface
    @param pr: predicate surface
    @param pnt: point surface
    """
    acno, modifs1 = remove_pred_and_point_from_actor(ac, pr, pnt)
    acno, modifs2 = filter_actor(acno)
    total_modifs = int(modifs1) + int(modifs2)
    if acno:
        return acno, total_modifs
    else:
        return False, float(False)


def score_proposition(ac, pr, pnt, penalties, myactors, gactors):
    """
    Assign a confidence score to a proposition based on the types
    of actors it has and other characteristics (e.g. has a mesasge or not,
    has had anaphora resolution ...)
    """
    sco = 0
    # canonical actors
    if ac.lower() in myactors:
        sco += 2
    else:
        # generic roles
        has_generic = False
        for ga in gactors:
            if ga in ac.lower():
                sco += 1
                has_generic = True
                break
        # not canonical, not generic
        if not has_generic:
            sco += 0.5
    # has message
    if pnt:
        sco += 3
    # message is very short, penalize
    if len(pnt.split()) == 1:
        sco -= 1
    elif len(pnt.split()) <= 3:
        sco -= 0.5
    # anaphora
    if "=>" in ac or "->" in ac:
        sco -= 1
    # penalties applied (9 march, only penalties are for actor filtering)
    for pen in penalties:
        sco -= pen
    # other indications of bad actor
    if "(" in ac or ")" in ac:
        sco -= 1
    return float(sco)


def find_point_in_sentence(pnt, sent, logfd):
    """
    Find point in sentence, after some manipulations and with some tolerance.
    @pnt: string for point
    @sent: string for sentence
    """
    pnt = re.sub("^to ", "", pnt)
    pnt = re.sub("^that ", "", pnt)
    stnew = sent
    for pu in string.punctuation:
        pnt = pnt.replace(pu, " ")
        stnew = stnew.replace(pu, " ")
    pnt = re.sub(" {2,}", " ", pnt)
    pnt = re.sub(" {2,}", " ", pnt)
    stnew = re.sub(" {2,}", " ", stnew)
    stnew = re.sub(" {2,}", " ", stnew)
    pntstart = stnew.lower().find(pnt.strip().lower())
    if pntstart < 0:
        logfd.write(u"POINT NF [{}] || [{}]\n".format(pnt.lower(),
                                                      stnew.lower()))
        return -1, -1
    if pntstart >= cfg.pt_tolerance:
        pntstart -= cfg.pt_tolerance
    pntend = pntstart + len(pnt) + 2 * cfg.pt_tolerance
    return pntstart, pntend
