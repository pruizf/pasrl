"""
Take export-format propositions, find agreeers/disagreers and write fixture
with the new information added to the previously available one.
"""

__author__ = 'Pablo Ruiz'
__date__ = '14/11/15'


import codecs
import json
from pprint import pprint
import re
import simplejson
import sys
import time


def fix_actor(ba):
    """
    Repro same normalizations as in txt2json_with_ptype_with_atype.pl,
    othewise will get AssertionError in L{create_agr_dis_objects} below
    cos labels not found ...
    """
    if ba == "American_Samoa":
        return "Samoa"
    elif ba == "Azerbaijan_Democratic_Republic":
        return "Azerbaijan"
    else:
        return ba


def find_props_by_sentence_from_export(rf, fmt):
    """
    Read export file and output hash with propositions by sentence-id
    @param rf: export file
    @param fmt: format ('types' where actors and predicates have types) or 'notypes'
    """
    assert fmt in ("types", "notypes")
    print "Finding props for sentences"
    sprops = {}
    with codecs.open(rf, "r", "utf8") as infi:
        line = infi.readline()
        while line:
            test = re.match(r"^(enb[^\t]+)\t", line)
            if test:
                sid = test.group(1)
                sprops.setdefault(sid, set())
                assert sid
                line2 = infi.readline()
                while line2 and not line2.startswith("enb"):
                    if len(line2.strip()) > 0:
                        sl = line2.strip().split("\t")
                        if fmt == "notypes":
                            assert len(sl) == 4
                            actor, pred, point = sl[0], sl[1], sl[-1]
                            sprops[sid].add((fix_actor(actor), pred, point))
                        else:
                            assert len(sl) == 8
                            actor, pred, point = sl[0], sl[2], sl[4]
                            sprops[sid].add((fix_actor(actor), pred, point))
                    line2 = infi.readline()
            if not line2:
                break
            line = line2
    return sprops


def find_agreement_disagreement(sen2props):
    """
    Based on propositions by sentence, find actor-mention pairs
    in agreement and disagreement.
    @note: The convention in the results is to indicate an 'opposed by'
    agent by prefixing 'not' to its predicate.
    """
    print "Finding agreement and disagreement"
    ad = {}
    dis = {}
    for idx, (sid, its) in enumerate(sen2props.items()):
        for ac, pr, pt in its:
            for ac2, pr2, pt2 in its:
                if pr == pr2 and pt == pt2 and ac != ac2:
                    ad.setdefault(tuple(sorted((ac, ac2))),
                                  set()).add((pt, sid))
                #TODO: need test ac != ac2 in elif as well?
                elif ((pr == u"not {}".format(pr2) or
                       pr2 == u"not {}".format(pr)) and pt == pt2):
                    dis.setdefault(tuple(sorted((ac, ac2))),
                                   set()).add((pt, sid))
        if not idx % 1000:
            print "  Done {}, {}".format(
                idx, time.strftime("%H:%M:%S", time.localtime()))
    return ad, dis


def enrich_json_propositions(injson):
    """
    Add actor labels and point text to propositions, so that it's
    easier to match them with proposition extraction results.
    @return: json object (you can use it as dict) with the added infos
    """
    print "Enriching proposition info in json, {}".format(
        time.strftime("%H:%M:%S", time.localtime()))
    jsons = simplejson.load(codecs.open(injson, "r", "utf8"), strict=False)
    # get 'tables' from db
    #TODO: why lists? looks slow: related? try with sets? Can't, cos "ob" are dict
    # took 10 min to traverse point mentions when allowing non-canonical props
    sentences = [ob for ob in jsons if ob["model"] == "ui.sentence"]
    actors = [ob for ob in jsons if ob["model"] == "ui.actor"]
    amentions = [ob for ob in jsons if ob["model"] == "ui.actormention"]
    points = [ob for ob in jsons if ob["model"] == "ui.point"]
    pmentions = [ob for ob in jsons if ob["model"] == "ui.pointmention"]
    props = [ob for ob in jsons if ob["model"] == "ui.proposition"]
    # hashes to store fields to add to propositions based on their pk
    s2sid = {}
    am2label = {}
    pt2text = {}
    # find labels for actor mentions
    print " - amentions: [{} todo] {}".format(len(amentions),
        time.strftime("%H:%M:%S", time.localtime()))
    for am in amentions:
        am["actor_label"] = [ac["fields"]["name"] for ac in actors
                             if int(ac["pk"]) == int(am["fields"]["actor"])][0]
        assert am["actor_label"]
    # find texts for point mentions
    print " - ptmentions [{} todo]: {}".format(len(pmentions),
        time.strftime("%H:%M:%S", time.localtime()))
    for ptm in pmentions:
        ptm["point_mention_text"] = [pt["fields"]["name"] for pt in points
                                     if int(pt["pk"]) == \
                                     int(ptm["fields"]["point"])][0]
        assert ptm["point_mention_text"]
    # find names (filename-sentid) for sentence
    print " - sentences: [{} todo] {}".format(len(sentences),
        time.strftime("%H:%M:%S", time.localtime()))
    # fill hahses
    print " - hashing pk to labels: {}".format(
        time.strftime("%H:%M:%S", time.localtime()))
    for se in sentences:
        s2sid[int(se["pk"])] = se["fields"]["name"]
    for acm in amentions:
        am2label.setdefault(int(acm["pk"]), acm["actor_label"])
    for pntm in pmentions:
        pt2text.setdefault(int(pntm["pk"]), pntm["point_mention_text"])
    # ENRICH PROPOSITIONS
    print " - propositions: [{} todo] {}".format(len(props),
        time.strftime("%H:%M:%S", time.localtime()))
    for prop in props:
        prop["fields"]["actor_mention_label"] = am2label[prop["fields"]["actorMention"]]
        prop["fields"]["point_mention_text"] = pt2text[prop["fields"]["pointMention"]]
        prop["fields"]["sentence_name"] = s2sid[int(prop["fields"]["sentence"])]
    return jsons


def create_agrdis_objects(ad, jsons, mode="agree", start_pk_from=1):
    """
    Create the db objects for AgrDis table
    @param ag: agreeing props dict
    @param dgr: disagreeing props dict
    @param jsons: json object where propositions have names, not just pk,
    obtained with L{enrich_json_propositions} in this module.
    """
    assert mode in ("agree", "disagree")
    print "Creating agreee-disagree objects [type={}]".format(mode)
    # example input
    # >>> dagr.keys()[0]
    # (u'Japan', u'Tanzania')
    # >>> dagr[dagr.keys()[0]]
    # set([(u'any discussion on capacity building related to the GEF report should be included under the agenda item on the financial mechanism rather than under the item on capacity building related to the Convention', u'enb12282e.txt-12'),
    # (u'the establishment of an international capacity-building mechanism', u'enb12613e.html-99')])
    adout = {}
    props = [ob for ob in jsons if ob["model"] == "ui.proposition"]
    pks = start_pk_from
    dones = 0
    for (am1, am2), infos in ad.items():
        for (pt, sid) in infos:
            pr4sid = [pr for pr in props if
                      pr["fields"]["sentence_name"] == sid]
            am1pr = [pr for pr in pr4sid
                     if pr["fields"]["actor_mention_label"] == am1]
            am2pr = [pr for pr in pr4sid
                     if pr["fields"]["actor_mention_label"] == am2]
            # assert only if working with whole dataset
            assert am1pr
            assert am2pr
            for pr1 in am1pr:
                for pr2 in am2pr:
                    if pr1["fields"]["point_mention_text"] == \
                       pr2["fields"]["point_mention_text"]:
                        assert pks not in adout
                        # create agrdis obj
                        #TODO: rels are undirected, may need to duplicate
                        #TODO: (here or in querying ...)
                        # (Canada agrees Tanzania is same as Tanzania agrees Canada)
                        adout[pks] = {"fields": {
                            "actorMention1": pr1["fields"]["actorMention"],
                            "actorMention2": pr2["fields"]["actorMention"],
                            "pointMention": pr1["fields"]["pointMention"],
                            "reltype": mode
                        }, "model": "ui.agrdis", "pk": pks}
                        pks += 1
            dones += 1
            if not dones % 1000:
                print "  Done {}, {}".format(
                    dones, time.strftime("%H:%M:%S", time.localtime()))
    return adout, pks


def write_infos(agrs, dagrs, old, newout):
    """
    Write out in fixture format appended to previous version of file
    """
    print "Writing out to: {}".format(newout)
    oldj = json.load(codecs.open(old, "r", "utf8"))
    print " - adding agreers"
    for ag, infos1 in sorted(agrs.items(), key=lambda it: it[1]["pk"]):
        oldj.append(infos1)
    print " - adding disagreers"
    for dg, infos2 in sorted(dagrs.items(), key=lambda it: it[1]["pk"]):
        oldj.append(infos2)
    print " - json srlz"
    #json.dump(oldj, codecs.open(newout, "w", "utf8"))
    # more readable than json.dump
    with codecs.open(newout, "w", "utf8") as outfd:
        outfd.write("[")
        outfd.write(",\n".join([json.dumps(jsobj) for jsobj in oldj]))
        outfd.write("]")


def main(resf, fmt, jsnf, outfn):
    ## debug
    global s2p
    global agr
    global dagr
    global ag2write
    global disag2write
    ##
    print "Start, {}".format(time.strftime("%H:%M:%S", time.localtime()))
    s2p = find_props_by_sentence_from_export(resf, fmt)
    agr, dagr = find_agreement_disagreement(s2p)
    ejson = enrich_json_propositions(jsnf)
    ag2write, lastpk = create_agrdis_objects(agr, ejson)
    disag2write, _ = create_agrdis_objects(dagr, ejson, mode="disagree",
                                           start_pk_from=lastpk)
    write_infos(ag2write, disag2write, jsnf, outfn)
    print "Prop file: {}".format(resf)
    print "Fixture I: {}".format(jsnf)
    print "Fixture O: {}".format(outfn)
    print "End, {}".format(time.strftime("%H:%M:%S", time.localtime()))


if __name__ == "__main__":
    #resufi = "/home/pablo/projects/ie/wk/db/all_corpus_export_format_2.txt"
    resufi = "/home/pablo/projects/ie/out/pasrl/test_pickle_out_08_avril_contains_new_sentences_and_props_all_types_on_top_of_30_jan_export.txt"
    # jsonfi = ("/home/pablo/projects/ie/wk/ui_wireframe/uibo/webuibo" + \
    #           "/ext_data/json/data_all_2000_new_wtype_sent_name_sorted_final.json")
    assert len(sys.argv) == 1 or len(sys.argv) == 4
    try:
        jsonfi = sys.argv[1]
    except IndexError:
        jsonfi = ("/home/pablo/projects/ie/wk/ui_wireframe/uibo/webuibo" +
                  "/ext_data/json/data_all_new_meta.json")
    try:
        mynewout = sys.argv[2]
    except IndexError:
        mynewout = ("/home/pablo/projects/ie/wk/ui_wireframe/uibo/webuibo" +
                    "/ext_data/json/data_all_new_final.json")
    try:
        rfmt = sys.argv[3]
    except IndexError:
        rfmt = "types"
    main(resufi, rfmt, jsonfi, mynewout)