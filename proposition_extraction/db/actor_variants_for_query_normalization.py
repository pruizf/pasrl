"""Get actor variants in our config, so that can normalize queries in django app"""

__author__ = 'Pablo Ruiz'
__date__ = '10/11/15'

import codecs
from lxml import etree


def find_variants(infi):
    norm2var = {}
    tree = etree.parse(infi)
    elems = tree.xpath("//country | //observer | //other")
    for elem in elems:
        # try:
        #     label = elem.attrib["display"]
        # except KeyError:
        label = elem.attrib["dbpedia"]
        norm2var[label] = list(set([
            ele.xpath("./text()")[0] for ele in elems
            if "display" in ele.attrib and ele.attrib["display"] == label
            or "dbpedia" in ele.attrib and ele.attrib["dbpedia"] == label]))
        norm2var[label].append(label)
        norm2var[label].append(label.replace("_", " "))
    return norm2var


def flip_variants(vardict):
    var2norm = {}
    for norm, varlist in vardict.items():
        for var in varlist:
            var2norm[var] = norm
    return var2norm


def write_norm2variants(vardict, myout):
    with codecs.open(myout, "w", "utf8") as outf:
        for label in sorted(vardict):
            outl = u"{}\t{}\n".format(label, "; ".join(vardict[label]))
            outf.write(outl)

def write_variants2norm(vardict, myout):
    with codecs.open(myout, "w", "utf8") as outf:
        for variant in sorted(vardict, key=lambda k:vardict[k]):
            outl = u"{}\t{}\n".format(variant, vardict[variant])
            outf.write(outl)


def main(myxml, myout):
    print "In: {}".format(myxml)
    print "Out: {}".format(myout)
    actor2variants = find_variants(myxml)
    variants2actor = flip_variants(actor2variants)
    #write_norm2variants(actor2variants, myout)
    write_variants2norm(variants2actor, myout)


if __name__ == "__main__":
    axml = "/home/pablo/projects/ie/iewk/data/actors.xml"
    outf = "/home/pablo/projects/ie/wk/db/actor_variants_for_db_queries.txt"
    main(axml, outf)