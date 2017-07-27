"""
Parse a SketchEngine concordance in XML format
Output list of verbs in its kwic element
"""

from collections import Counter
from lxml import etree

import sys

try:
    tree = etree.parse(sys.argv[1])
except IndexError:
    inf = "/home/pablo/projects/clm/work/conc_enb_sketch_engine.xml"
    tree = etree.parse(inf)

bits = tree.xpath("//kwic/text()")

verbs = []
for bit in bits:
    verbs.append(bit.strip().split()[-1])

counts = Counter(verbs)
for vb in sorted(counts, key=lambda myvb: counts[myvb], reverse=True):
    print u"{}\t{}".format(vb, counts[vb])

