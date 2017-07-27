"""
Analysis to see which sentences are being skipped by L{parse_srl}
Corpus sentences must have same "ids" as those output by L{parse_srl}
"""

__author__ = 'Pablo Ruiz'
__date__ = '31/01/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import os
import re
import sys


SENT = ur"^(enb[0-9]+e\.(?:txt|html))-([0-9]+)\t(.+)"
ANNOT = ur"^(enb[0-9]+e\.(?:txt|html))-([0-9]+)\t([YN])\t(.+)"
# in the corridors section for ENB corpus
CRDS = re.compile(ur"(?:corridors|breezeways)", re.I)


def hash_sentence_texts_by_id(sfi):
    """Get file sfi with sentence texts and ids, hash it"""
    sid2txt = {}
    with codecs.open(sfi, "r", "utf8") as fid:
        for ll in fid:
            sl = ll.split("\t")
            assert sl[-1].strip() == u"{}-{}".format(sl[0], sl[1])
            sid2txt.setdefault(sl[0], {})
            sid2txt[sl[0]].update({int(sl[1]): sl[2]})
    return sid2txt


def write_out_sentences_after_pasrl_max(sentdi, myfn, myidx, mydones, myout):
    """
    Writes out sentences in sentence hash whose id is higher than the last
    sentnece-id in the pasrl results
    @param sentdi: sentence hash
    @param myfn: filename we're working with
    @param idx: index to check for
    @param mydones: hash with done fn-sentence_id combinations
    @param myout: output file
    """
    if max(sentdi[myfn].keys()) >= myidx:
        ids4out = [ke for ke in sentdi[myfn] if int(ke) >= myidx]
        for ke in ids4out:
            if (myfn, ke) in mydones:
                continue
            myout.write(u"{}-{}\t{}\t{}\n\n".format(myfn, ke, "N",
                                                    sentdi[myfn][ke]))
        myout.write("\n")


def parse_outputs(ofi, nfi, sd):
    """
    Go over pasrl outputs adding sentences with no results as needed
    """
    dones = {}
    prev_id = 0
    prev_fn = ""
    with codecs.open(ofi, "r", "utf8") as ofd,\
         codecs.open(nfi, "w", "utf8") as nfd:
        line = ofd.readline()
        while line:
            has_start = re.match(SENT, line)
            if has_start:
                # filename is group 1, id is group 2
                sid = (has_start.group(1), int(has_start.group(2)))
                # reset previous id to 0 when filename changes
                if prev_fn != "" and sid[0] != prev_fn:
                    prev_id = 0
                    # write out empty sentences after srl's LAST sentence
                    # last file in srl results requires special treatment
                    write_out_sentences_after_pasrl_max(sd, prev_fn, idx,
                                                        dones, nfd)
                # sentence ids not sequential
                if sid[-1] != prev_id:
                    idx = prev_id
                    # write out from sentence hash until find
                    # next match in actual results
                    while idx <= sid[-1]:
                        if idx == 0:
                            idx += 1
                            continue
                        elif idx < sid[-1]:
                            if (sid[0], idx) in dones:
                                idx += 1
                                continue
                            nfd.write(u"{}\t{}\t{}\n\n".format(
                                u"{}-{}".format(sid[0], idx), "N",
                                sd[sid[0]].get(idx)))
                            idx += 1
                        else:
                            myfn, mysid, mytxt = re.match(SENT, line).groups()
                            nfd.write(u"{}\t{}\t{}\n".format(
                                u"{}-{}".format(myfn, mysid), "Y", mytxt))
                            idx += 1
                # sentence ids are sequential
                else:
                    myfn, mysid, mytxt = re.match(SENT, line).groups()
                    nfd.write(u"{}\t{}\t{}\n".format(
                        u"{}-{}".format(myfn, mysid), "Y", mytxt))
                    dones[(myfn, int(mysid))] = True
                try:
                    prev_id = idx
                    prev_fn = sid[0]
                except NameError:
                    # if first line does not match SENT
                    continue
            else:
                nfd.write(line)
            line = ofd.readline()
        # last line in srl file requires checking if sentences from
        # that file still not written out from sentence hash
        write_out_sentences_after_pasrl_max(sd, prev_fn, idx, dones, nfd)


def get_stats_for_annots(di):
    """Descriptive stats on annotation Y/N"""
    stats = {}
    for fn, s2ann in di.items():
        stats.setdefault(fn, {"Y": len([(se, ann) for (se, ann) in
                                        s2ann.items() if ann == "Y"])})
        stats[fn]["N"] = len([(se, ann) for (se, ann) in s2ann.items()
                              if ann == "N"])
        assert stats[fn]["Y"] + stats[fn]["N"] == len(di[fn])
        stats[fn]["%Y"] = float(stats[fn]["Y"]) / len(di[fn])
        stats[fn]["%N"] = float(stats[fn]["N"]) / len(di[fn])
    return stats


def analyze_parsed_outputs(ifn, ofn):
    """
    Get some descriptive stats on outputs of L{parse_outputs}
    """
    infos = {}        # all sentences
    crds = {}         # sentence after seeing "corridors" in a sentence
    sorter = []
    # hash the infos
    done_fns = {}
    with codecs.open(ifn, "r", "utf8") as fdi:
        start_crds = False
        for line in fdi:
            has_sent = re.match(ANNOT, line)
            if has_sent:
                fn, sid, ann, txt = has_sent.groups()
                if fn not in done_fns:
                    start_crds = False
                done_fns.setdefault(fn, 1)
                infos.setdefault(fn, {})
                try:
                    assert int(sid) not in infos[fn]
                except AssertionError:
                    # this file had problems
                    if fn == "enb1201e.txt" and sid in (
                        43, 45, 46, 48, 49, 51, 52, 53):
                        pass
                infos[fn][int(sid)] = ann
                sorter.append(fn)
                # corridors section
                if re.search(CRDS, line):
                    # flag once
                    start_crds = True
                if start_crds:
                    crds.setdefault(fn, {})
                    try:
                        assert int(sid) not in crds[fn]
                    except AssertionError:
                        # this file had problems
                        if fn == "enb1201e.txt" and sid in (
                            43, 45, 46, 48, 49, 51, 52, 53):
                            pass
                    crds[fn][int(sid)] = ann

    # compute stats ===========================================================
    sall = get_stats_for_annots(infos)
    scrd = get_stats_for_annots(crds)  # /!\ confusing names: crds vs. srcd !
    ratios = {}
    # ratio between corridors sentences and whole text
    for ke, va in crds.items():
        ratios[ke] = float(len(va)) / len(infos[ke])
    # add default values for docs that have no corridors section
    for ke in infos:
        scrd.setdefault(ke, {"Y": 0, "N": 0})
        ratios.setdefault(ke, "n/a")
    assert set(sall.keys()) == set(scrd.keys()) == set(ratios.keys())

    # create output lines =====================================================
    outlines = []
    for ke, va in sorted(infos.items(), key=lambda x: sorter.index(x[0])):
        outl = [ke, sall[ke]["Y"], sall[ke]["N"], sall[ke]["Y"] + sall[ke]["N"],
                sall[ke]["%Y"], sall[ke]["%N"],
                scrd[ke]["Y"], scrd[ke]["N"], ratios[ke]]
        outlines.append("\t".join([unicode(it) if type(it) != float
                                   else u"{0:.2f}".format(it) for it in outl]))
    # write
    with codecs.open(ofn, "w", "utf8") as ofd:
        ofd.write("\t".join(["fn", "Y", "N", "T", "%Y", "%N",
                             "YC", "NC", "%C"]))
        ofd.write("\n")
        ofd.write("\n".join(outlines))


def main():
    # IO ------------------------------
    try:
        assert len(sys.argv) == 3 or len(sys.argv) == 1
    except AssertionError:
        print "python {} $SRL_OUTPUTS $CORPUS_SENTENCES".format(sys.argv[0])
    try:
        inf = sys.argv[1]
        senf = sys.argv[2]
    except IndexError:
        inf = ("/home/pablo/projects/ie/out/pasrl/" +
               "test_pickle_out_30_jan_accept_incomplete.txt")
        senf = ("/home/pablo/projects/clm/enb_corpus/sentences/" +
                "ixa_sentence_tokenization/enb_sentences_4db.txt")
    # w_dones means that i added a flag Y/N to see if the sentence had been
    # provided some sort of annotation by the system (Y) or not (N)
    ouf = os.path.splitext(inf)[0] + "_added_sents_w_dones.txt"
    smy = os.path.splitext(inf)[0] + "_summary_stats.txt"
    # Proc ----------------------------
    si2txt = hash_sentence_texts_by_id(senf)
    parse_outputs(inf, ouf, si2txt)
    analyze_parsed_outputs(ouf, smy)


if __name__ == "__main__":
    main()