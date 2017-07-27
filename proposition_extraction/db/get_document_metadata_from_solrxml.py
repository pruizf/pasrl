"""Get enb issue number, cop name, city etc. for a doc id, print tabsep and sql"""

__author__ = 'Pablo Ruiz'
__date__ = '08/11/15'

import codecs
from lxml import etree
import os
import re

xmldir = "/home/pablo/projects/clm/enb_corpus/ie/enbxml"
outfn = "/home/pablo/projects/ie/ui/document_metadata.txt"
outsqln = "/home/pablo/projects/ie/ui/document_metadata.sql"

table = "ui_document"


def get_data_from_xml_and_write(xdir, outf, outsql):
    with codecs.open(outf, "w", "utf8") as ofd, \
         codecs.open(outsql, "w", "utf8") as osql:
        for fn in os.listdir(xdir):
            print fn
            ffn = os.path.join(xdir, fn)
            tree = etree.parse(ffn)
            fileid, cop, vol, city, mydate = (
                tree.xpath("//field[@name='id']/text()")[0],
                re.sub(" .*", "", tree.xpath("//field[@name='cop']/text()")[0]),
                tree.xpath("//field[@name='vol']/text()")[0],
                tree.xpath("//field[@name='city']/text()")[0],
                re.sub("T.*", "", tree.xpath("//field[@name='date']/text()")[0]))
            ofd.write(u"{}\t{}\t{}\t{}\t{}\n".format(fileid, vol, cop, city, mydate))
            osql.write(
                u"update `{}` set volume='{}', city='{}', cop='{}', date='{}' ".format(
                    table, vol, city, cop, mydate) + \
                u"where name='{}';\n".format(fileid))


if __name__ == "__main__":
    get_data_from_xml_and_write(xmldir, outfn, outsqln)