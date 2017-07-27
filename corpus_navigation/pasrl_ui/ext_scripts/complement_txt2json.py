"""
Takes output of L{txt2json_with_ptype.pl} and adds infos to it
Usage: python complement_txt2json.py INPUTFILE.xxx
Creates output file named INPUTFILE_meta.json
"""

__author__ = 'Pablo Ruiz'
__date__ = '11/11/15'


import codecs
import inspect
import json
import os
import re
from os import remove
import simplejson
import sys
import time

here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))

datadir = os.path.join(here, "../ext_data/txt")
entifn = os.path.abspath(os.path.join(datadir, "enb_entities_4db.txt"))
kpfn = os.path.abspath(os.path.join(datadir, "enb_keyphrases_4db.txt"))
doc_metadata = os.path.abspath(os.path.join(datadir, "document_metadata.txt"))


DBG = False

def rgescape(st):
    """Avoid regex errors (unbalanced parenthesis, escaping etc)"""
    st = st.replace("(", r"\(")
    st = st.replace(")", r"\)")
    st = st.replace("[", r"\[")
    st = st.replace("]", r"\]")
    st = st.replace("+", r"\+")
    st = st.replace("*", r"\*")
    return st


def get_sentence_id_for_pointmentions(injson):
    print "Getting sentence id for pointmentions, {}".format(
        time.strftime("%H:%M:%S", time.localtime()))
    jsons = simplejson.load(codecs.open(injson, "r", "utf8"), strict=False)
    # get 'tables' from db (this takes long) based on json input file
    props = [ob for ob in jsons if ob["model"] == "ui.proposition"]
    pmt2sid = {}
    print " - ptmentions: [{} todo] {}".format(len(props),
        time.strftime("%H:%M:%S", time.localtime()))
    for idx, prop in enumerate(props):
        pmt2sid[int(prop["fields"]["pointMention"])] = int(prop["fields"]["sentence"])
        if idx and not idx % 1000:
            print "   - Done {} point mentions, {}".format(
                idx, time.strftime("%H:%M:%S", time.localtime()))
    return pmt2sid


def hash_json_for_sentences(infn):
    """Find out the primary key of ui.sentence objs"""
    sname2pk = {}
    with codecs.open(infn, "r", "utf8") as infd:
        line = infd.readline()
        while line:
            if '"ui.sentence"' in line:
                sobj = json.loads(re.sub(r",$", "", line))
                if sobj["model"] != "ui.sentence":
                    print "Weird line: {}".format(line)
                    line = infd.readline()
                    continue
                sname2pk.setdefault(sobj["fields"]["name"],
                                    {"pk": int(sobj["pk"])})
            line = infd.readline()
    return sname2pk


def hash_json_for_pointmentions(infn):
    """Return dict of pointMention text by pointMention id."""
    pmtid2txt = {}
    with codecs.open(infn, "r", "utf8") as infd:
        line = infd.readline()
        while line:
            if '"ui.pointmention"' in line:
                pmtobj = json.loads(re.sub(r"[,\]]$", "", line))
                if pmtobj["model"] != "ui.pointmention":
                    print "Weird line: {}".format(line)
                    line = infd.readline()
                    continue
                pmtid2txt.setdefault(int(pmtobj["pk"]),
                                     pmtobj["fields"]["text"])
            line = infd.readline()
    return pmtid2txt


def hash_keyphrases_from_txt(dbinfos, ptmentions, ptmi2si, inf=kpfn):
    """
    Hash corpus keyphrases and assign their sentence foreign key
    based on the db info.
    @param dbinfos: a dict created from a json file in django loaddata format
    @param ptmentions: dict of pointmentions (i.e their text) by pointmention id
    @param ptmi2si: dict of sentence-id by pointmention id
    """
    print "Hashing keyphrases"
    kp2m = {}
    kpkey2ptmkey = {}
    with codecs.open(inf, "r", "utf8") as infd:
        line = infd.readline()
        dones = 0
        while line:
            if line.startswith("#"):
                line = infd.readline()
                continue
            sl = line.strip().split("\t")
            mention, start, end, sent_id = \
                sl[1], int(sl[2]), int(sl[3]), sl[-1]
            try:
                sent_fk = dbinfos[sent_id]["pk"]
            except KeyError:
                sent_fk = -1
            kp2m.setdefault(sl[1], []).append({"sent_id": sent_id,
                                               "start": start, "end": end,
                                               "sentence_fk": sent_fk,
                                               "pk": dones + 1})
            # if find kp in a pointmention for the kp's sentence, store
            # ptm-id as value for kp-id in the kp2ptm hash
            kpkey2ptmkey.setdefault(kp2m[sl[1]][-1]["pk"], [])
            for ptmid, ptmention in ptmentions.items():
                if sent_fk != ptmi2si[ptmid]:
                    continue
                if re.search(re.compile(ur"\b{}\b".format(
                             rgescape(mention)), re.I),
                             ptmention):
                    #import pdb;pdb.set_trace()
                    #kpkey2ptmkey[dones + 1].append(ptmid)
                    kpkey2ptmkey[kp2m[sl[1]][-1]["pk"]].append(ptmid)
                else:
                    if DBG:
                        print "NOT FOUND: [{}] in [{}]".format(
                            ur"\b{}\b".format(rgescape(mention)),
                            ptmention)
                    else:
                        pass
            line = infd.readline()
            dones += 1
            if not dones % 1000:
                print "Done {} lines, {}".format(
                    dones, time.strftime("%H:%M:%S", time.localtime()))
    # add to kp2m pointmention keys tied to each kp mention
    # sort i guess not needed, may help debug
    for kpme, dilist in sorted(kp2m.items()):
        for di in dilist:
            di.update({"pointmentionlist": []})
            if di["pk"] in kpkey2ptmkey:
                di["pointmentionlist"].extend(kpkey2ptmkey[di["pk"]])
    return kp2m


def hash_entities_from_txt(dbinfos, ptmentions, ptmi2si, inf=entifn):
    """
    Hash corpus entities and assign their sentence foreign key
    based on the db info.
    @param dbinfos: a dict created from a json file in django loaddata format
    """
    print "Hashing entities"
    e2m = {}
    ekey2ptmkey = {}
    done_pks = {}
    with codecs.open(inf, "r", "utf8") as infd:
        line = infd.readline()
        dones = 0
        while line:
            if line.startswith("#"):
                line = infd.readline()
                continue
            sl = line.strip().split("\t")
            fn, mention, start, end, label, confid, snbr = \
                sl[0], sl[1], int(sl[2]), int(sl[3]), sl[4], \
                float(sl[6]), sl[7]
            e2m.setdefault(label, {"mentions": {}})
            if "pk" not in e2m[label]:
                assert len(e2m) + 1 not in done_pks
                e2m[label]["pk"] = len(e2m) + 1
                done_pks[len(e2m) + 1] = True
            # hash per label, then per mention-string, then a list of dict
            # with infos for each occurrence of that mention string (sentence,
            # start, end, ...). Point mention keys containing the mention
            # will be added to the dicts in this list
            e2m[label]["mentions"].setdefault(mention, []).append({
                "sent_name": u"{}-{}".format(fn, snbr), "confid": confid,
                "start": start, "end": end, "pk": dones + 1})
            try:
                e2m[label]["mentions"][mention][-1]["sentence_fk"] = \
                dbinfos[e2m[label]["mentions"][mention][-1]["sent_name"]]["pk"]
            except KeyError:
                # working with a small sample many entities won't find a sentence
                e2m[label]["mentions"][mention][-1]["sentence_fk"] = -1

            ekey2ptmkey.setdefault(
                e2m[label]["mentions"][mention][-1]["pk"], [])
            #TODO: cd speed up if skip cases whose offsets make it not work
            #(i.e the entity mention is not inside the point mention based on offsets)
            for ptmid, ptmention in ptmentions.items():
                if e2m[label]["mentions"][mention][-1]["sentence_fk"] != \
                        ptmi2si[ptmid]:
                    continue
                if re.search(re.compile(ur"\b{}\b".format(
                             rgescape(mention)), re.I),
                             ptmention):
                    #import pdb;pdb.set_trace()
                    #kpkey2ptmkey[dones + 1].append(ptmid)
                    ekey2ptmkey[e2m[label]["mentions"]\
                        [mention][-1]["pk"]].append(ptmid)
                else:
                    if DBG:
                        print "NOT FOUND: [{}] in [{}]".format(
                            ur"\b{}\b".format(rgescape(mention)),
                            ptmention)
                    else:
                        pass
            line = infd.readline()
            dones += 1
            if not dones % 1000:
                print "Done {} lines, {}".format(
                    dones, time.strftime("%H:%M:%S", time.localtime()))

    # add pointMention keys to the dicts in the mention occurrences list for
    # each entity label, based on common entitymention key
    # 'sort' not needed, but may help debug to do it always in same order
    #import pdb;pdb.set_trace()
    for elbl, mdict in sorted(e2m.items()):
        for mtn, dilist in mdict["mentions"].items():
            for di in dilist:
                di.update({"pointmentionlist": []})
                if di["pk"] in ekey2ptmkey:
                    di["pointmentionlist"].extend(ekey2ptmkey[di["pk"]])
    return e2m


def hash_document_metadata(infn=doc_metadata):
    # metadata format
    # enb1297e.txt	97	04	Buenos Aires	1998-11-13
    print "Hashing doc metadata"
    fn2infos = {}
    with codecs.open(infn, "r", "utf8") as infi:
        line = infi.readline()
        while line:
            # itype = issue type (daily | summary)
            fn, issue, cop, city, date, itype = line.strip().split("\t")
            fn2infos[fn] = {
                "issue": int(issue), "cop": cop, "city": city,
                "copyear": re.match(r"[0-9]{4}-", date), "date": date,
                "itype": itype}
            line = infi.readline()
    return fn2infos


def add_new_infos(jso, njso, kps, ents):
    """
    Add infos to the json based on the keyphrase and entities hashes
    @param jso: path to json file
    @param njso: path to new json (intermediate, before adding doc metadata)
    @param kps: dict of keyphrases
    @param ents: dict of entities
    """
    with codecs.open(jso, "r", "utf8") as infi, \
         codecs.open(njso, "w", "utf8") as outfi:
        outfi.write(infi.read()[0:-1])
        outfi.write(", \n")
        # write entities and their mentions
        for en, eninfos in ents.items():
            outfi.write("".join((json.dumps(
                {"fields": {"name": en},
                 "model": 'ui.entity', "pk": eninfos["pk"]}), ",\n")))
            for mt, mtinfolist in eninfos["mentions"].items():
                #outinfos = {"fields": {}, "model": 'ui.entity', "pk": mt["pk"]}
                for mtinfos in mtinfolist:
                    if mtinfos["sentence_fk"] != -1:
                        outfi.write("".join((json.dumps(
                            {"fields":
                                {"text": mt,
                                 "start": mtinfos["start"],
                                 "end": mtinfos["end"],
                                 "pointmentions": mtinfos["pointmentionlist"],
                                 "entity": eninfos["pk"],
                                 "confidence": mtinfos["confid"],
                                 "sentence": mtinfos["sentence_fk"]},
                             "model": 'ui.entitymention', "pk": mtinfos["pk"]}), ",\n")))
        # write keyphrases
        jsons2write = {}
        for kp, infos in kps.items():
            todo = len([i for i in infos if i["sentence_fk"] != -1])
            for info in infos:
                if info["sentence_fk"] != -1:
                    jsons2write[json.dumps(
                        {"fields": {"text": kp, "start": info["start"],
                                    "end": info["end"],
                                    "pointmentions": info["pointmentionlist"],
                                    "sentence": info["sentence_fk"]},
                         "model": 'ui.keyphrase', "pk": info["pk"]})] = 1
        outfi.write(",\n".join(jsons2write.keys()))
        outfi.write("]")


def add_metadata(njso, fjso, mdata):
    """
    Add document metadata to the doc rows in the fixture json
    @param njso: json with all infos but doc metadata
    @param fjso: final json file (with doc metadata added)
    @param mdata: hash with doc metadata info
    """
    todo = len(mdata)
    dones = 0
    with codecs.open(njso, "r", "utf8") as infd, \
         codecs.open(fjso, "w", "utf8") as outfd:
        line = infd.readline()
        while line:
            if '"ui.document"' in line:
                sobj = json.loads(re.sub(r",$", "", line))
                if sobj["model"] != "ui.document":
                    print "Weird line: {}".format(line)
                    line = infd.readline()
                    continue
                else:
                    assert sobj["fields"]["name"] in mdata
                    for fi in ("issue", "cop", "city",
                               "copyear", "date", "itype"):
                        sobj["fields"][fi] = mdata[sobj["fields"]["name"]][fi]
                    dones += 1
                    if dones == todo:
                        outfd.write("".join((json.dumps(sobj), "\n")))
                    else:
                        outfd.write("".join((json.dumps(sobj), ",\n")))
            else:
                outfd.write(line)
            line = infd.readline()
        if '"ui.document"' in line:
            outfd.write("]")


def main(injson, entis=entifn, kps=kpfn):
    global en2mtn  # debug
    global jinfos  # debug
    global kp2mtn  # debug
    outfn = os.path.splitext(injson)[0] + "_interm.json"
    outmeta = os.path.splitext(outfn)[0].replace("_interm", "") + "_meta7.json"
    print "In: {}".format(os.path.abspath(injson))
    print "Entis: {}".format(entis)
    print "KPs: {}".format(kps)
    print "Interm: {}".format(os.path.abspath(outfn))
    print "Meta: {}".format(os.path.abspath(outmeta))
    jinfos = hash_json_for_sentences(injson)
    ptmid2txt = hash_json_for_pointmentions(injson)
    ptmid2sid = get_sentence_id_for_pointmentions(injson)
    kp2mtn = hash_keyphrases_from_txt(jinfos, ptmid2txt, ptmid2sid)
    en2mtn = hash_entities_from_txt(jinfos, ptmid2txt, ptmid2sid)
    docu_metadata = hash_document_metadata()
    add_new_infos(injson, outfn, kp2mtn, en2mtn)
    add_metadata(outfn, outmeta, docu_metadata)
    os.remove(outfn)
    print "Removing intermediate output ({})".format(
        os.path.basename(outfn))


if __name__ == "__main__":
    try:
        injs = sys.argv[1]
    except IndexError:
        injs = os.path.join(here,
            "../ext_data/json/data_all_2000_wtype_sent_name_sorted.json")
    main(injs)