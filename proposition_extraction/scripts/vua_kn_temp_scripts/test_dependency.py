#!/usr/bin/env python

import KafNafParserPy as knp
from KafNafParserPy import KafNafParser as np
#from VUA_pylib.feature_extractor.constituency import Cconstituency_extractor
#from VUA_pylib.feature_extractor.dependency import Cdependency_extractor

#file='/home/pablo/projects/ie/iewk/scripts/vua_kn_test_scripts/naf_examples/10007YRK-H1B1-2SFM-K2HY.txt_8795bbbd2f30103f0ef2f098a183c457.naf'
file = '/home/pablo/projects/ie/out/testdeps/srl/test_deps.txt.par.coref.srl.naf'
naf_obj = np(file)

# My beautiful bear gave the amazing book to Johnny in the park last night.
# 1      2      3     4   5     6      7   8    9   10  11  12   13    14


extractor = knp.feature_extractor.dependency.Cdependency_extractor(naf_obj)
#sp = extractor.get_shortest_path('t446','t453')
sp = extractor.get_shortest_path('t5','t4')
print sp

# this will give ['PMOD', 'NMOD', 'SBJ', 'VC', 'VC', 'LGS']
#   see if can use this to figure out if a chunk is inside the
#   subject, inside the object, or were
#sp2 = extractor.get_shortest_path_spans(['t444','t445','t446'], ['t451','t452','t454'])
sp2 = extractor.get_shortest_path_spans(['t5','t6','t7'], ['t1','t2','t3'])
print sp2

# or maybe you can serialize stretches in their order to get the surface rep
# like, if the path is PMOD, NMOD, SBJ,
# look in the deps what terms are involved in those deps, and output
# the span from the lowest to the highest index

#print 'Path to root for one token', extractor.get_path_to_root('t460')
print 'Path to root for one token', extractor.get_path_to_root('t7')


#print 'Shortest Path to root for span',extractor.get_shortest_path_to_root_span(['t444','t445','t446'])
print 'Shortest Path to root for span',extractor.get_shortest_path_to_root_span(['t5','t6','t7'])
#extractor = Cconstituency_extractor(naf_obj)
#===============================================================================
# print extractor.get_deepest_phrase_for_termid('t363')
# print extractor.get_path_for_termid('t363')
# print extractor.get_deepest_phrase_for_termid('t359')
# print extractor.get_path_for_termid('t359')
# print extractor.get_deepest_phrase_for_termid('t567')
# print extractor.get_path_for_termid('t567')
# print extractor.get_deepest_phrase_for_termid('t717')
# print extractor.get_path_for_termid('t717')
#===============================================================================

#print extractor.get_path_from_to('t363','t365')



