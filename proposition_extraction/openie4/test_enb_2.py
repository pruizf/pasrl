"""Tests applying OIE4 to ENB corpus, different treatment of actors in output"""

__author__ = 'Pablo Ruiz'
__date__ = '12/09/15'


import codecs
import inspect
from nltk import stem
import os
import re
import sys


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, os.pardir))


import config as cfg
import utils as ut
import manage_domain_data as mdd
import writers as wr


def parse_oie_results(fn):
    """Read open ie column-format output, extracting infos we store"""
    arg_re = re.compile(ur"""
                         ^[A-Z][^A-Z]+Argument\(
                         ([^,)]+),List\(
                         \[([0-9]+),[ ]([0-9]+)\)\)
                         \)+$""", re.VERBOSE)
    rel_re = re.compile(ur"""
                          ^Relation\(
                          ([^,)]+),List\(
                          \[([0-9]+),[ ]([0-9]+)\)\)
                          \)+$""", re.VERBOSE)
    extractions = {}
    with codecs.open(fn, "r", "utf8") as fi:
        todo = 10000000000
        done = 0
        line = fi.readline()
        lnbr = 0
        while line:
            # skip empty cols
            sl = [x for x in line.split("\t") if x]
            ags = {}
            rel = {}
            argnbr = 1
            conf = float(sl[0])
            sent = sl[-1]
            for col in sl[1:-1]:
                is_arg = re.match(arg_re, col)
                if is_arg:
                    ags[argnbr] = {"arg": is_arg.group(1),
                                   "start": int(is_arg.group(2)),
                                   "end": int(is_arg.group(3))}
                    argnbr += 1
                else:
                    is_rel = re.match(rel_re, col)
                    if is_rel:
                        rel[is_rel.group(1)] = {"start": int(is_rel.group(2)),
                                                "end": int(is_rel.group(3))}
            if cfg.DBG:
                print "ARGS", ags, conf, sent.strip()
                print "REL", rel, "\n"
            extractions[lnbr] = (ags, rel, conf, sent)
            lnbr += 1
            done += 1
            if done == todo:
                sys.exit()
            line = fi.readline()
    return extractions


def add_relation(argus, prd, rt, cfd, st):
    """
    Create dict to represent relation
    @param argus: argument dict (values are arguments)
    @param prd: the predicate
    @param rt: predicat type (oppose, support, report)
    @param cfd: confidence for annotation
    @param st: sentence
    """
    rel = {"type": rt, "confidence": cfd, "sentence": st.strip(),
           "pred": prd, "argus": [ar[1]["arg"] for ar in sorted(argus.items())]}
    if not rel["argus"]:
        rel["argus"] = ["0"]
    return rel


def find_actor_in_argu(actor, argu):
    """Find actor from domain data inside an OIE argument"""
    return re.search(re.compile(ur"\b{}\b".format(actor),
                     re.IGNORECASE|re.UNICODE), argu)


def cross_oie_and_domain_infos(res, preds, actors, cf):
    """
    Cross OIE results and domain info like actors or
    domain-relevant predicates, to find sentences that
    contain domain-relevant information
    @param res: oie results
    @param preds: predicates
    @param actors: actors
    """
    # rel format: {rel: {"start": int, "end": int}}
    # arg format: {argnbr: {"arg": str, "start": int, "end": int}}
    tagged_rels = {cf.spref: [], cf.opref: [], cf.rpref: [], "other": []}
    file_rels = []
    # first see if have a relevant predicate
    lemr = stem.WordNetLemmatizer()
    for ll, (ags, pred, conf, sent) in sorted(res.items()):
        if not pred:
            continue
        if lemr.lemmatize(pred.keys()[0], 'v').lower() in preds["sup"]:
            rel = add_relation(ags, pred.keys()[0], cf.spref, conf, sent)
        elif lemr.lemmatize(pred.keys()[0], 'v').lower() in preds["opp"]:
            rel = add_relation(ags, pred.keys()[0], cf.opref, conf, sent)
        elif lemr.lemmatize(pred.keys()[0], 'v').lower() in preds["rep"]:
            rel = add_relation(ags, pred.keys()[0], cf.rpref, conf, sent)
        else:
            rel = []
        if rel:
            file_rels.append(rel)
    # now see if arguments are relevant
    for rel in file_rels:
        is_tagged = False
        # find argument in actors
        done_argus = []
        for arg in rel["argus"]:
            if arg.lower() in actors["AI"]:
                argm = u"{}_AI".format(arg)
                rel["argus"][rel["argus"].index(arg)] = argm
                is_tagged = True
                if arg.lower() not in done_argus:
                    tagged_rels[rel["type"]].append(rel)
                    done_argus.append(arg.lower())
            elif arg.lower() in actors["NAI"]:
                argm = u"{}_NAI".format(arg)
                rel["argus"][rel["argus"].index(arg)] = argm
                is_tagged = True
        if is_tagged:
            if rel["argus"][-1] not in done_argus:
                tagged_rels[rel["type"]].append(rel)
        else:
            # find actor in arguments
            for arg in rel["argus"]:
                done_actors = []
                for act in actors["AI"]:
                    if find_actor_in_argu(act, arg):
                        argm = u"{}_AI".format(arg)
                        try:
                            rel["argus"][rel["argus"].index(arg)] = argm
                        except ValueError:
                            rel["argus"][rel["argus"].index(argm)] = argm
                        if act not in done_actors and act.lower() not in done_argus:
                            tagged_rels[rel["type"]].append(rel)
                            done_actors.append(act)
                            done_argus.append(act.lower())
                        is_tagged = True
                if not is_tagged:
                    for act in actors["NAI"]:
                        if find_actor_in_argu(act, arg):
                            argm = u"{}_NAI".format(arg)
                            try:
                                rel["argus"][rel["argus"].index(arg)] = argm
                            except ValueError:
                                rel["argus"][rel["argus"].index(argm)] = argm
                            if act not in done_actors and act.lower() not in done_argus:
                                tagged_rels[rel["type"]].append(rel)
                                done_actors.append(act)
                                done_argus.append(act.lower())
                            is_tagged = True
            if not is_tagged:
                tagged_rels["other"].append(rel)
                done_argus.append(rel["argus"][-1].lower())
    return tagged_rels


def cross_infos_for_dir(di, predlist, actlist, mycf):
    """Run the cross infos function on a dir"""
    for fn in os.listdir(di):
        ffn = os.path.join(di, fn)
        oie_res = parse_oie_results(ffn)
        file_rels = cross_oie_and_domain_infos(oie_res, predlist, actlist, mycf)
        yield {fn: file_rels}


def main(cf=cfg):
    """Run"""
    try:
        resdir = sys.argv[1]
    except IndexError:
        resdir = cfg.oieres
    ut.setup()
    mypreds = mdd.parse_verbal_predicates()
    myactors = mdd.parse_actors()
    for dct in cross_infos_for_dir(resdir, mypreds, myactors, cfg):
        assert len(dct) == 1
        fn, rels = dct.items()[0]
        wr.write_as_txt(fn, rels)


if __name__ == "__main__":
    main()