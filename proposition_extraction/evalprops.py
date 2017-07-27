"""
Compare reference and system propositions. Obtain metrics and error types.
"""

__author__ = 'Pablo Ruiz'
__date__ = '13/03/17'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
from collections import Counter
import re
import sys


# regexes to split the results files into result items
# result item with no propositions
nores = re.compile(r"(\n[0-9]+\t[^\n]+\n\n)")
# result item with propositions
resitem = re.compile(r"([0-9]+)\t([^\n]+)\n(.*?)\n{2,}", re.DOTALL)

# to write out error types
spellout = {"ac_pmw": "OK{actor}, KO{predicate,point}",
            "pc_amw": "OK{predicate}, KO{actor,point}",
            "mc_apw": "OK{point}, KO{actor,predicate}",
            "apc_mw": "OK{actor,predicate}, KO{point}",
            "amc_pw": "OK{actor,point}, KO{predicate}",
            "pmc_aw": "OK{predicate,point}, KO{actor}",
            "allc": "OK{all}, KO{none}",
            "allw": "OK{none}, KO{all}"}


def usage():
    print "\nUsage: python {} reference_results system_results\n".format(sys.argv[0])


def create_result_set(fn):
    """
    Read the results files into a dictionary {(itemid, sentence): set(props)}
    """
    di = {}
    with codecs.open(fn, "r", "utf8") as fd:
        txt = fd.read()
        # normalize system results when no propositions were
        # extracted for the item
        txt_norm = re.sub(nores, r"\1\n", txt)
        items = re.findall(resitem, txt_norm)
        for item in items:
            dikey = (item[0].lower().strip(),
                     item[1].lower().strip())
            di.setdefault(dikey, set())
            proplines = item[2].lower().split("\n")
            props = set([tuple(ln.split("\t")) for ln in proplines])
            # skip sents with no props
            if not list(props)[0][0]:
                print "No propositions for item nbr {}".format(dikey[0])
                continue
            di[dikey].update(props)
    return di


def compare_result_sets(ref, sys):
    """
    Compare reference and system result dictionaries and output metrics.
    Micro averaged F1.
    """
    total_tps = 0
    total_sys = 0
    total_ref = 0
    # reference and system keys must match
    assert sorted(ref) == sorted(sys)
    for ske, sva in sys.items():
        # check if all system keys in ref (for tests, if assert failed)
        if ske not in ref:
            print "SKEY missing", ske
        tps = len(sva.intersection(ref[ske]))
        total_tps += tps
        total_sys += len(sva)
        total_ref += len(ref[ske])
    # check if all reference keys in system (for tests, if assert failed)
    for rke, rva in ref.items():
        if rke not in sys:
            print "RKEY missing", rke
    prec = float(total_tps) / total_sys
    rec = float(total_tps) / total_ref
    f1 = (2 * prec * rec) / (prec + rec)
    print "\nP: {}\nR: {}\nF1: {}\n".format(prec, rec, f1)
    print "true positive: {}\ntotal system: {}\ntotal reference: {}\n".format(
        total_tps, total_sys, total_ref)


def error_analysis(ref, syr):
    """
    Obtain error types in results.
    """
    # The propositions receive scores matching the keys in types_key
    # The meaning of the values "ac_pmw" etc is in dictionary 'spellout' above
    types_key = {1: "ac_pmw", 3: "pc_amw", 5: "mc_apw",
                 4: "apc_mw", 6: "amc_pw", 8: "pmc_aw",
                 9: "allc", 0: "allw"}
    print "== Error analysis =="
    # sorted keys must match
    assert sorted(ref) == sorted(syr)
    # store proposition scores here
    prop_scos = {}
    prop_id = 0
    for ske, sprops in syr.items():
        assert ske in ref
        rprops = ref[ske]
        for sprop in sprops:
            prop_sco = 0
            # all correct
            if sprop in rprops:
                prop_scos[prop_id] = 9
                prop_id += 1
                continue
            # partially correct
            has_pc = len([rp for rp in rprops if rp[1] == sprop[1]])    # pred ok
            has_ac = len([rp for rp in rprops if rp[0] == sprop[0]])    # actor ok
            has_mc = len([rp for rp in rprops if rp[-1] == sprop[-1]])  # point ok
            if has_ac: prop_sco += 1
            if has_pc: prop_sco += 3
            if has_mc: prop_sco += 5
            prop_scos[prop_id] = prop_sco
            prop_id += 1
            # warn if proposition totally wrong
            if prop_sco == 0:
                print "Proposition {} all wrong. Item: {}".format(sprop, ske)
            # warn if only predicate ok
            if prop_sco == 3:
                print "Proposition {} only predicate ok. Item: {}".format(sprop, ske)
    counted_error_types = Counter(prop_scos.values())
    print "\n= Error types ="
    for k, v in sorted(counted_error_types.items(),
                       key=lambda tu: tu[-1], reverse=True):
        print "{}\t{}".format(spellout[types_key[k]], v)


def main():
    try:
        reffn = sys.argv[1]
    except IndexError:
        usage()
        sys.exit(2)
    try:
        sysfn = sys.argv[2]
    except IndexError:
        usage()
        sys.exit(2)
    print "- Getting reference results"
    refset = create_result_set(reffn)
    print "- Getting system results"
    sysset = create_result_set(sysfn)
    compare_result_sets(refset, sysset)
    error_analysis(refset, sysset)


if __name__ == "__main__":
    main()