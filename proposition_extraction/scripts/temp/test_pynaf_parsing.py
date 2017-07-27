"""
Tests NAF parsing with pynaf
@note: for now i'm using the VUA parser though
"""

__author__ = 'Pablo Ruiz'
__date__ = '18/09/15'

import pynaf as pn

tree = pn.NAFDocument("/home/pablo/projects/ie/out/enb_corefs_out_with_countries/srl/enb1204e.txt.par.coref.srl.naf")

corefs = tree.get_coreference()

for coref in corefs:
    a = tree.get_coreference_mentions(coref)
    for sp in a:
        #for t in sp:
        print tree.get_reference_span(sp)
        print tree.get_terms_words(sp)