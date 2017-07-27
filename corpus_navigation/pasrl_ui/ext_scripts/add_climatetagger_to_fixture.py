"""
Add entity mentions from Climatetagger API (Reegle Thesaurus) to fixture
"""

__author__ = 'Pablo Ruiz'
__date__ = '12/05/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import gzip
import simplejson as js
import sys


def load_fixture(fxn):
    fxd = js.load(gzip.open(fxn))
    return fxd


def get_highest_entity_pk_in_fixture(fxo):
    """Get highest entity primary key from the fixture as object"""
    return max([int(ob["pk"]) for ob in fxo if ob["model"] == "ui.entity"])


def get_highest_entitymention_pk_in_fixture(fxo):
    """Get highest entity mention primary key from the fixture as object"""
    return max([int(ob["pk"]) for ob in fxo if ob["model"] ==
                "ui.entitymention"])


def assign_pointmentions_to_entity_labels_by_sentence(enfm):
    """
    Returns dict {(entity_label, uri):
        {sent-id: {"conf": conf, "ptmks": set(pointmentionpks)}}
    that will be used later by L{create_entities_and_mentions_from_txt}
    to represent one entity mention per sentence, and assigning
    this same entitymention to all of the pointmentions in the sentence
    to which that entitymention is tied.
    """
    el2ptmxs = {}
    with codecs.open(enfm, "r", "utf8") as ifd2:
        ll = ifd2.readline()
        while ll:
            if ll.startswith("#"):
                ll = ifd2.readline()
                continue
            sl = ll.strip().split("\t")
            label, uri, ptmk, sk, conf = (
                sl[0], sl[1], int(sl[2]), int(sl[3]), float(sl[4]))
            el2ptmxs.setdefault((label, uri), {})
            el2ptmxs[(label, uri)].setdefault(sk, {"conf": conf,
                                                   "ptmks": set()})
            el2ptmxs[(label, uri)][sk]["ptmks"].add(ptmk)
            ll = ifd2.readline()
    return el2ptmxs


def create_entities_and_mentions_from_txt(el2sao, lastepk, lastempk):
    """
    Create the entity and entitymention rows from file with
    climatetagger output in delimited format.
    @param el2sao: dict of entity-label to sentence to entitymention-pointmentionpk
    @param lastepk: last primary key for entities in fixture (start
    adding pks one higher than this)
    @param lastempk: last primary key for entity mentions in fixture
    (start adding pks one higher than this)
    """
    #print "epk: {}, empk: {}".format(lastepk, lastempk)
    print "Creating entity and mention rows"
    emos = []
    eos = []
    done_epks = set()
    done_empks = set()
    epkct = 1
    empkct = 1
    # Input dictionary format -------------------------------------------------
    # {(entity_label, uri):
    # {sent-id: {"conf": conf, "ptmks": set(pointmentionpks)}}
    # Create entity rows ------------------------------------------------------
    for elu, sid2ptms in sorted(el2sao.items()):
        epk = lastepk + epkct
        assert epk not in done_epks
        done_epks.add(epk)
        eo = {"fields": {"eurl": elu[1], "name": elu[0], "etype": "rgl"},
              "model": "ui.entity", "pk": epk}
        eos.append(eo)
        epkct += 1
        # Create entity mention rows ------------------------------------------
        # {sent-id: {"conf": conf, "ptmks": set(pointmentionpks)}}
        for sid, sinfos in sorted(sid2ptms.items()):
            assert epk is not None
            empk = lastempk + empkct
            assert empk not in done_empks
            done_empks.add(empk)
            empkct += 1
            emo = {"fields": {"confidence": sinfos["conf"], "sentence": sid,
                              "end": -1, "start": -1, "pointmentions": [],
                              "entity": epk, "text": elu[0], "linker": "rgl"},
                   "model": "ui.entitymention", "pk": empk}
            # add the point mentions to the entity mention
            # (chose to create one entity mention per label per sentence)
            for ptmk in sinfos["ptmks"]:
                emo["fields"]["pointmentions"].append(ptmk)
            emos.append(emo)
            empkct += 1
    out = eos + emos
    # jeos = js.dumps(eos)
    # jemos = js.dumps(emos)
    #TODO: any use of js.dumps here ?
    # couldn't i just return list and then do dumps in
    # L{add_entities_and_mentions_to_fixture} ?
    jsout = js.dumps(out)
    return jsout


def add_entities_and_mentions_to_fixture(ems, fxo, outfn):
    """
    Add new entities and entitymention rows to fixture obj
    """
    print "Creating output json"
    fxo.extend(js.loads(ems))
    #js.dump(fxo, open(outfn, "w"))
    with codecs.open(outfn, "w", "utf8") as outfd:
        outfd.write("[")
        for row in fxo[0:-1]:
            outfd.write("".join((js.dumps(row), ",\n")))
        outfd.write(js.dumps(fxo[-1]))
        outfd.write("]")


def main(fxn, emfn, ofn):
    fxd = load_fixture(fxn)
    el2axs = assign_pointmentions_to_entity_labels_by_sentence(emfn)
    maxepk = get_highest_entity_pk_in_fixture(fxd)
    maxempk = get_highest_entitymention_pk_in_fixture(fxd)
    json_rows = create_entities_and_mentions_from_txt(el2axs, maxepk, maxempk)
    add_entities_and_mentions_to_fixture(json_rows, fxd, ofn)
    #return fxd, maxepk, maxempk, el2axs


if __name__ == "__main__":
    # IO
    assert len(sys.argv) == 1 or len(sys.argv) == 4
    # fixture
    try:
        fxfn = sys.argv[1]
    except IndexError:
        fxfn = "/home/pablo/projects/ie/uibo/webuibo/ext_data/json/fixture_20160416.json.gz"
    # climate tagger output
    try:
        ctfn = sys.argv[2]
    except IndexError:
        ctfn = "/home/pablo/projects/ie/wk/db/enb_reegle_4db.txt"
    try:
        outfn = sys.argv[3]
    except IndexError:
        outfn = "/home/pablo/projects/ie/uibo/webuibo/ext_data/json/fixture_20160513-4.json"
    # run
    #fxfd, mxepk, mxempk, el2a = main(fxfn, ctfn)
    main(fxfn, ctfn, outfn)
