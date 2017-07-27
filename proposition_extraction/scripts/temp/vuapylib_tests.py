"""Testing https://github.com/cltl/VUA_pylib#vua_pyliblexicon"""

__author__ = 'Pablo Ruiz'
__date__ = '24/09/15'

import KafNafParserPy as knp
from KafNafParserPy import KafNafParser as np

#fi='/home/pablo/projects/ie/iewk/scripts/vua_kn_test_scripts/naf_examples/10007YRK-H1B1-2SFM-K2HY.txt_8795bbbd2f30103f0ef2f098a183c457.naf'
fi='/home/pablo/projects/o/enca/enca/out/noche_parsed/III_parsed.xml'
naf_obj = np(fi)

extractor = knp.feature_extractor.constituency.Cconstituency_extractor(naf_obj)
# print "=== DEEPEST PHRASE FOR TERM ID ===\n"
# print extractor.get_deepest_phrase_for_termid('t363')
# print "\n\n\n"
#
# print "=== PATH FROM TERM A TO TERM B ===\n"
# print extractor.get_path_from_to('t363','t365')
# print "\n\n\n"
#
# print "=== CHUNKS ===\n"
# for ch in sorted(extractor.get_chunks('NP'),
#     key=lambda chs: (int(naf_obj.get_term(chs[0]).get_id().replace("t", "")),
#                      len(chs))):
#     print u"CHUNK: {}".format(ch)
#     print [naf_obj.get_term(i).get_lemma() for i in ch]
#     print "\n"
# print "\n\n\n"

print "=== ALL CHUNKS FOR TERM ===\n"
# maybe could use this to get the largest NP or PP containing a term
#for type_chunk, list_ids in extractor.get_all_chunks_for_term('t713'): # cars
#for type_chunk, list_ids in extractor.get_all_chunks_for_term('t209'):  # noche II
for type_chunk, list_ids in extractor.get_all_chunks_for_term('t110'):  # noche III
    print type_chunk, list_ids
print "\n\n\n"