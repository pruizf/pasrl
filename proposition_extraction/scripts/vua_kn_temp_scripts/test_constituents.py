#!/usr/bin/env python


from KafNafParserPy import KafNafParser
#from VUA_pylib.feature_extractor.constituency import Cconstituency_extractor
from KafNafParserPy.feature_extractor.constituency import Cconstituency_extractor

#file='naf_examples/10007YRK-H1B1-2SFM-K2HY.txt_8795bbbd2f30103f0ef2f098a183c457.naf'
file='/home/pablo/projects/ie/iewk/scripts/vua_kn_temp_scripts/naf_examples/10007YRK-H1B1-2SFM-K2HY.txt_8795bbbd2f30103f0ef2f098a183c457.naf'
#file = 'example.naf'

naf_obj = KafNafParser(file)
extractor = Cconstituency_extractor(naf_obj)

print 'Deepest phrases for termid: t363'
print extractor.get_deepest_phrase_for_termid('t363')

print 'Path for termid to root : t363'
print extractor.get_path_for_termid('t363')

print 'Path from to t363 to t365'
print extractor.get_path_from_to('t363','t365')

print 'Deepest phrase for termid t363'
print extractor.get_deepest_phrase_for_termid('t363')
print extractor.get_deepest_phrase_for_termid('t413')
print extractor.get_deepest_phrase_for_termid('t414')

# participation from ... is in the same noun phrase
print "Least common subsumer for t413 (participation) and t414 (from)"
lcs = extractor.get_least_common_subsumer('t413', 't414')
print lcs
print "Path from t413 to t414"
print extractor.get_path_from_to('t413','t414')


#for ch in extractor.get_chunks('NP'):
#    print ch
#    print [naf_obj.get_term(i).get_lemma() for i in ch]
#    print '-'*10

#for type_chunk, list_ids in extractor.get_all_chunks_for_term('t713'):
#    print type_chunk, list_ids

