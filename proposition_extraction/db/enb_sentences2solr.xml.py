"""
Takes tsv file with ENB sentences as split by IXA Pipes and creates solr xml update documents.
Only using text and the sentence-id.
The sentence-id is the same as in the Django webapp
"""

__author__ = 'Pablo Ruiz'
__date__ = '19/03/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import inspect
from lxml import etree
import os
import sys


sentences = "/home/pablo/projects/clm/enb_corpus/sentences/" + \
            "ixa_sentence_tokenization/enb_sentences_4db.txt"
outdir = "/home/pablo/projects/clm/enb_corpus/sentences/solr_format"

here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)


def text2xml(infn, odir):
    with codecs.open(infn, "r", "utf8") as infd:
        line = infd.readline()
        while line:
            # get infos
            sl = line.strip().split("\t")
            sid = sl[-1]
            stxt = sl[2]
            # create xml nodes
            root = etree.Element("add")
            doc = etree.SubElement(root, "doc")
            title = etree.SubElement(doc, "field", name="title")
            #    'fid' for file-id, even if it is the sentence-id
            fid = etree.SubElement(doc, "field", name="id")
            text = etree.SubElement(doc, "field", name="description")
            # populate nodes
            fid.text = sid
            title.text = sid
            text.text = stxt
            # serialize
            sertree = etree.tostring(root, xml_declaration=True,
                                     encoding="utf8", pretty_print=True)
            ofn = os.path.join(odir, sid + ".xml")
            with open(ofn, "w") as ofh:
                # print "=> {}".format(os.path.basename(ofn))
                ofh.write(sertree)
            line = infd.readline()


def main():
    print "> Infn: {}".format(sentences)
    print "> Outdir: {}".format(outdir)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    text2xml(sentences, outdir)


if __name__ == "__main__":
    main()