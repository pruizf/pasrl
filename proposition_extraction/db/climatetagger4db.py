"""
Format climatetagger output in a way that results can be read for fixture creation
"""

__author__ = 'Pablo Ruiz'
__date__ = '10/05/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import gzip
import os
import pickle
import simplejson as js
import time


RPREF = "http://reegle.info/glossary/"
FPKL = True

ptmdir = "/home/pablo/projects/ie/corpora/pointmentions_04252016"
entdir = "/home/pablo/projects/ie/out/el/pointmentions_04252016"
fixture = "/home/pablo/projects/ie/uibo/webuibo/ext_data/json/fixture_20160416.json.gz"
outfn = "/home/pablo/projects/ie/wk/db/enb_reegle_4db_compact.txt"
outfnv = "/home/pablo/projects/ie/wk/db/enb_reegle_4db.txt"

f2tpkl = "/home/pablo/projects/ie/wk/db/enb_reegle_f2t.pkl"
t2fpkl = "/home/pablo/projects/ie/wk/db/enb_reegle_t2f.pkl"


def get_pointmentions_for_points(fxfn):
    """
    Return a hash with pointmention pks for each point
    @param fxfn: the fixture
    """
    print "Get pointmention pk for point pk"
    p2pm = {}
    fd = gzip.open(fxfn)
    for idx, ll in enumerate(fd):
        if '\"ui.pointmention\"' in ll:
            jso = js.loads(ll.strip().strip(","))
            p2pm.setdefault(jso["fields"]["point"], set()).add(jso["pk"])
        if idx and not idx % 10000:
            print "- Done {} lines, {}".format(idx, time.strftime("%H:%M:%S",
                time.localtime()))
    return p2pm


def get_pointmention_pk_for_point_text(fxfn, ptk2ptmk):
    """
    Return a hash point-text to point pk, and point-pk to pointmention pk
    @param fxfn: the fixture
    @param ptk2ptmk: hash of point keys to pointmention keys,
    created with L{get_pointmentions_for_points} above
    """
    print "Get point pk for point texts"
    ptext2pk = {}
    fd = gzip.open(fxfn)
    for idx, ll in enumerate(fd):
        if '\"ui.point\"' in ll:
            jso = js.loads(ll.strip().strip(","))
            assert jso["fields"]["name"].strip() not in ptext2pk
            ptext2pk[jso["fields"]["name"].strip()] = \
                {jso["pk"]: ptk2ptmk[jso["pk"]]}
        if idx and not idx % 10000:
            print "- Done {} lines, {}".format(idx, time.strftime("%H:%M:%S",
                time.localtime()))
    return ptext2pk


def get_sentence_id_for_pointmentions(fxfn):
    print "Getting sentence id for pointmentions, {}".format(
        time.strftime("%H:%M:%S", time.localtime()))
    jsons = js.load(gzip.open(fxfn))
    # get 'tables' from db
    props = [ob for ob in jsons if ob["model"] == "ui.proposition"]
    pmt2sid = {}
    print "- ptmentions: [{} todo] {}".format(len(props),
        time.strftime("%H:%M:%S", time.localtime()))
    for idx, prop in enumerate(props):
        pmt2sid[int(prop["fields"]["pointMention"])] = int(prop["fields"]["sentence"])
        if idx and not idx % 1000:
            print "- Done {} point mentions, {}".format(
                idx, time.strftime("%H:%M:%S", time.localtime()))
    return pmt2sid


def get_filenames_for_point_text(indir):
    """
    Since called climatetagger with the pointmentions, there will
    be repetition in the results.
    See which filenames are for equivalent content
    @note: the filenames are normalized to just the number (all the rest
    is always the same!)
    """
    print "Get filenames for point"
    txt2fn = {}
    fn2txt = {}
    # populate txt2fn
    for idx, fn in enumerate(os.listdir(indir)):
        ffn = os.path.join(indir, fn)
        with codecs.open(ffn, "r", "utf8") as ifd:
            txt = ifd.read().strip()
        txt2fn.setdefault(txt, set()).add(fn.replace("pointmention_nbr_", ""))
        if idx and not idx % 10000:
            print "- Done {} point files, {}".format(
                idx, time.strftime("%H:%M:%S", time.localtime()))
    # populate fn2txt
    print "+ Inverse the dictionary"
    for idx, (txtstring, fnameset) in enumerate(txt2fn.items()):
        for fname in fnameset:
            if fname in fn2txt:
                assert fn2txt[fname] == txtstring
                continue
            fn2txt[fname] = txtstring
        if idx and not idx % 10000:
            print "- Done {} point texts (i), {}".format(
                idx, time.strftime("%H:%M:%S", time.localtime()))
    return txt2fn, fn2txt


def get_concepts_for_text(f2t, adir, ptext2ptmk, ptmk2sk):
    """
    Based on hash of texts-to-filename and on the climatetagger output,
    see which concepts belong to each text and filename
    @param f2t: hash with filenames to texts
    @param adir: dir with climatetagger annotations (same filenames
    as the text dir)
    @param ptext2ptmk: point-text to point-mention primary keys
    @param ptmk2sk: point mention pk to sentence pk, obtained with
    L{get_sentence_id_for_pointmentions} above
    """
    print "Getting concepts for texts (returns pointmention pks for a text)"
    cpco2ptmk = {}  # simple hash
    vbco2ptmk = {}  # verbose hash
    for idx, fn in enumerate(os.listdir(adir)):
        sfn = fn.replace("pointmention_nbr_", "")
        with codecs.open(os.path.join(adir, fn), "r", "utf8") as ifd:
            jso = js.loads(ifd.read().strip())
            for co in jso["concepts"]:
                txt = f2t[sfn]
                # only value is a set with the pointmention pks
                ptmpks = ptext2ptmk[txt].values()
                assert len(ptmpks) == 1
                assert isinstance(ptmpks[0], set)
                ptmpks = ptmpks[0]
                # smaller hash, all ptmkeys for a concept go in a set
                cpco2ptmk.setdefault(co["prefLabel"].strip(),
                                     {"uri": co["uri"].replace(RPREF, ""),
                                      "ptmks": set()})
                cpco2ptmk[co["prefLabel"].strip()]["ptmks"].update(ptmpks)
                # verbose hash (with sentence id and score per mention)
                for ptmpk in ptmpks:
                    curkey = (co["prefLabel"].strip(),
                              co["uri"].replace(RPREF, ""))
                    curdict = {"ptmk": ptmpk, "spk": ptmk2sk[ptmpk],
                               "sco": co["score"] / 100.0}
                    vbco2ptmk.setdefault(curkey, [])
                    if curdict not in vbco2ptmk[curkey]:
                        vbco2ptmk[curkey].append(curdict)
        if idx and not idx % 10000:
            print "- Done concepts for {} texts, {}".format(
                idx, time.strftime("%H:%M:%S", time.localtime()))
    return cpco2ptmk, vbco2ptmk


def write_out(c2ptmk, ofn):
    """
    Write the concept-to-pointmention table
    text, url, pklist
    @note: Then in fixture creation will need to add default values
    for start, end, confidence.
    In fxtr creat, will also need to add entity keys for these concepts ...
    @param c2tptmk: hash with concept strings to pointmention pks as set
    @param ofn: name of output file
    """
    print "Writing out to [{}]".format(ofn)
    with codecs.open(ofn, "w", "utf8") as ofd:
        for co, infos in sorted(c2ptmk.items()):
            ofd.write(u"{}\t{}\t{}\n".format(
                co, infos["uri"], ",".join(
                    [unicode(x) for x in infos["ptmks"]])))


def write_out_v(vc2ptmk, ofn):
    """
    Write out the concept-to-pointmention table with a single line per
    concept mention
    """
    print "Writing out verbose to [{}]".format(ofn)
    with codecs.open(ofn, "w", "utf8") as ofd:
        for (co, uri), infos in sorted(vc2ptmk.items()):
            for di in infos:
                ol = u"{}\t{}\t{}\t{}\t{}\n".format(
                    co, uri, di["ptmk"], di["spk"], di["sco"])
                ofd.write(ol)


def main(fxn, annotdir, outn, outnv):
    """Run
    @param fxn: fixture filename
    """
    ppk2ptmpk = get_pointmentions_for_points(fxn)
    ptext2ptmpk = get_pointmention_pk_for_point_text(fxn, ppk2ptmpk)
    if FPKL:
        print "Loading pickles:\n- [{}]\n- [{}]".format(t2fpkl, f2tpkl)
        text2fn = pickle.load(open(t2fpkl, "rb"))  # text-to-filename
        fn2text = pickle.load(open(f2tpkl, "rb"))  # filename-to-text
    else:
        text2fn, fn2text = get_filenames_for_point_text(ptmdir)
    ptmpk2spk = get_sentence_id_for_pointmentions(fxn)
    # simple and verbose concept to pointmention pk tables
    concept2ptmks, vbconcept2ptmks = get_concepts_for_text(
        fn2text, annotdir, ptext2ptmpk, ptmpk2spk)
    write_out(concept2ptmks, outn)
    write_out_v(vbconcept2ptmks, outnv)
    print "Done {}".format(time.strftime("%H:%M:%S", time.localtime()))
    return ppk2ptmpk, ptext2ptmpk, text2fn, fn2text, concept2ptmks, vbconcept2ptmks


if __name__ == "__main__":
    ptpk2ptmpk, ptxt2ptpk, txt2finame, finame2txt, co2ptmkeys, vco2ptmkeys = \
        main(fixture, entdir, outfn, outfnv)