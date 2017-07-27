"""To select some propositions (to import into UI for tests)"""

__author__ = 'Pablo Ruiz'
__date__ = '08/11/15'


import codecs
import random
import re


def get_sent_nbrs(res):
    """Get ids to select from"""
    print "- Getting sentence numbers"
    ids = {}
    with codecs.open(res, "r", "utf8") as rfd:
        line = rfd.readline()
        while line:
            test = re.match(r"^(enb[^\t]+)\t", line)
            if test:
                ids[test.group(1)] = 1
            line = rfd.readline()
    return ids


def choose_ids(allids, idmax, chosen_id_file):
    """Select ids randomly to a max choices"""
    print "- Choosing ids"
    chosen = {}
    while len(chosen) <= idmax:
        rd = random.randint(0, len(allids) - 1)
        chosen[sorted(allids)[rd]] = 1
    with codecs.open(chosen_id_file, "w", "utf8") as cif:
        for id_ in chosen:
            cif.write(u"{}\n".format(id_))
    return chosen


def get_props(res, out, chosen_ids):
    """Write out propositions for those ids"""
    print "- Writing selected propositions"
    dones = {}
    with codecs.open(res, "r", "utf8") as rfd, \
         codecs.open(out, "w", "utf8") as ofd:
        line = rfd.readline()
        while line:
            test = re.match(r"^(enb[^\t]+)\t", line)
            if (test and test.group(1) in chosen_ids and
                   test.group(1) not in dones):
                dones[test.group(1)] = 1
                ofd.write(line)
                line2 = rfd.readline()
                while not line2.startswith("enb"):
                    ofd.write(line2)
                    line2 = rfd.readline()
                ofd.write("\n")
            #TODO: doesn't matter for selection, but this may skip sentences
            line = rfd.readline()


def main(resf, outf, maxnbr, outidfile):
    global ids
    global chosen
    print "In: {}".format(resf)
    print "Out: {}".format(outf)
    ids = get_sent_nbrs(resf)
    chosen = choose_ids(ids, maxnbr, outidfile)
    get_props(resf, outf, chosen)

if __name__ == "__main__":
    maxprops = 2000
    # resfi = "/home/pablo/projects/ie/out/all_corpus_test_export_format/" + \
    #       "all_corpus_test_export_format_all_files.txt"
    resfi = "/home/pablo/projects/ie/out/test_pickle_out_2.txt"
    outfn = "/home/pablo/projects/ie/ui/selected_propositions_2000_wtype.txt"
    chosen_id_file = "/home/pablo/projects/ie/ui/chosen_ids_2000_wtype.txt"
    main(resfi, outfn, maxprops, chosen_id_file)
