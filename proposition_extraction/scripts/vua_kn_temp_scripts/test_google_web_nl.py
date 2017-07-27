#!/usr/bin/env python

from VUA_pylib.corpus_reader import Cgoogle_web_nl

google = Cgoogle_web_nl()

google.query('interessante *')

for res in google.get_items():
    print res
    print res.get_hits()
    print res.get_word()
    print res.get_tokens()
