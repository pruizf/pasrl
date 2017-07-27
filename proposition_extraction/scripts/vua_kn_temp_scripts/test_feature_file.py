#!/usr/bin/env python

from VUA_pylib.io import *

a = Cfeature_file('./data/example_feat_file.txt')

for example in a:
  print example
  
