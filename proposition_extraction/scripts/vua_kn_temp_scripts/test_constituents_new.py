"""
More tests on how to exploit NAF constituency trees, done while doing manual error analysis
on the enjambment detection tool
"""

from __future__ import print_function


__author__ = 'Pablo Ruiz'
__date__ = '14/07/17'
__email__ = 'pabloruizfabo@gmail.com'


import sys

from KafNafParserPy import KafNafParser
from KafNafParserPy.feature_extractor.constituency import Cconstituency_extractor


# IO
fname = sys.argv[1]
term1 = sys.argv[2]
try:
    term2 = sys.argv[3]
except IndexError:
    term2 = None


naf_obj = KafNafParser(fname)
ext = Cconstituency_extractor(naf_obj)

print(u"Path for term1 [{}] to root".format(
    [tok.get_text() for tok in naf_obj.get_tokens()
     if tok.get_id() == naf_obj.get_term(term1).get_span().get_span_ids()[0]][0]))
print(ext.get_path_for_termid_as_label_nonterid_pair(term1))


if term2 is not None:
    print(u"Path for term2 [{}] to root".format(
        [tok.get_text() for tok in naf_obj.get_tokens()
         if tok.get_id() == naf_obj.get_term(term2).get_span().get_span_ids()[0]][0]))
    print(ext.get_path_for_termid_as_label_nonterid_pair(term2))
