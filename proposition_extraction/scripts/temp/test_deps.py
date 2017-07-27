"""Test dep on KAF/NAF, seeing if can access nodes dependent on a given function (OBJ etc)"""

__author__ = 'Pablo Ruiz'
__date__ = '25/09/15'

import codecs
import inspect
from lxml.etree import XMLSyntaxError
from nltk import stem
import os
import re
import sys
import time

from KafNafParserPy import KafNafParser as np

# app-specific imports --------------------------------------------------------
here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)
sys.path.append(os.path.join(here, os.pardir))
sys.path.append(os.path.join(os.path.join(here, os.pardir),
                os.pardir))


from string import zfill

import config as cfg
import manage_domain_data as mdd
import model as md
import utils as ut

#naf = "/home/pablo/projects/ie/out/enb_testset_srl/srl/srl_enb_testset.txt.par.coref.srl.naf"
naf = "/home/pablo/projects/ie/out/testdeps2/srl/test_deps2.txt.par.coref.srl.naf"
# My beautiful bear gave the amazing book to Johnny in the park last night.
# 1      2      3     4   5     6      7   8    9   10  11  12   13    14


# try:
#     tree = np(naf)
# except XMLSyntaxError:
#     print "!! Document is empty {}".format(os.path.basename(naf))
#
# deps = list(tree.get_dependencies())
# for dep in deps:
#     if dep.get_function() == "OBJ":
#         #verb_term = dep.get_from()
#         obj_term = dep.get_to()
#     elif dep.get_function() == "SBJ":
#         subj_term = dep.get_to()
#
# print "OBJ", obj_term
# print "SBJ", subj_term
#
# #obj_and_terms_linked = [obj_term]
# linkable_to_obj = sorted(["t{}".format(zfill(dep.get_to().replace("t", ""), 5))
#                           for dep in deps if dep.get_from() == obj_term] + \
#                          ["t{}".format(zfill(obj_term.replace("t", ""), 5))])
# linkable_to_subj = sorted(["t{}".format(zfill(dep.get_to().replace("t", ""), 5))
#                            for dep in deps if dep.get_from() == subj_term] + \
#                           ["t{}".format(zfill(subj_term.replace("t", ""), 5))])
#
# print "Rel2_OBJ", linkable_to_obj
# print "Rel2_SBJ", linkable_to_subj

#t39 is ref
# all_links = []
# link = [dep for dep in deps if dep.get_from() == "t39"]
# print link[0].get_from(), link[0].get_to()
# link2 = [dep for dep in deps if dep.get_from() == link[0].get_to()]
# print link2[0].get_from(), link2[0].get_to()

# all_links.append(link[0])
# print "B", link
# while len(link) > 0:
#     link = [dep for dep in deps if dep.get_to() == all_links[-1].get_to()]
#     all_links.append(link[0])
#     print "A", link

# book written by Sue

# if __name__ == "__main__":
#     #naf = "/home/pablo/projects/ie/out/enb_testset_srl/srl/srl_enb_testset.txt.par.coref.srl.naf"
#     naf = "/home/pablo/projects/ie/out/testdeps2/srl/test_deps2.txt.par.coref.srl.naf"
#
#     try:
#         tree = np(naf)
#     except XMLSyntaxError:
#         print "!! Document is empty {}".format(os.path.basename(naf))
#
#     bla  = []
#     deps = list(tree.get_dependencies())
#     def iterate_deps(initial_term):
#         global bla
#         depnos = []
#         #import pdb;pdb.set_trace()
#         for no in deps:
#             if no.get_from() == initial_term:
#                 depnos.append(no)
#         print "DEPNOS", ["H {} D {}".format(x.get_from(), x.get_to()) for x in depnos]
#         bla.extend(["H {} D {}".format(x.get_from(), x.get_to()) for x in depnos])
#         #for dno in depnos:
#         #yield [iterate_deps(dno.get_from()) for dno in depnos]
#         #yield depnos
#         try:
#             #bla.append(iterate_deps(depnos[-1].get_to()))
#             return iterate_deps(depnos[-1].get_to())
#         except IndexError:
#             return False
#
#
#     #for nl in list(iterate_deps("t7")):
#     #    pass
#         #for x in list(nl):
#         #    print "x, nl", x, nl
#         #    #print x.get_to()
#         #print nl.get_to(), nl.get_from(), nl.get_function()
#     #for x in (iterate_deps("t7")): pass
#     #while list(iterate_deps("t7")) != []
#     #    for x in iterate_deps("t7")
#     iterate_deps("t7")

if __name__ == "__main__":
    #naf = "/home/pablo/projects/ie/out/enb_testset_srl/srl/srl_enb_testset.txt.par.coref.srl.naf"
    naf = "/home/pablo/projects/ie/out/testdeps3/srl/test_deps3.txt.par.coref.srl.naf"

    try:
        tree = np(naf)
    except XMLSyntaxError:
        print "!! Document is empty {}".format(os.path.basename(naf))

    alldeps  = []
    alldeps_n = []
    alldeps_p = []
    deps = list(tree.get_dependencies())
    def iterate_deps(initial_term):
        global alldeps
        depnos = []
        for no in deps:
            if no.get_from() == initial_term:
                depnos.append(no)
        print "DEPNOS", ["H {} D {}".format(x.get_from(), x.get_to()) for x in depnos]
        alldeps_p.extend(["H {} D {}".format(x.get_from(), x.get_to()) for x in depnos])
        #alldeps.extend([x.get_to() for x in depnos])
        alldeps.append([(x.get_to(), x.get_from()) for x in depnos])
        alldeps_n.append([x for x in depnos])
        try:
            return iterate_deps(depnos[-1].get_to())
        except IndexError:
            return False

    iterate_deps("t8")
    for x in alldeps:
        for y in x:
            iterate_deps(y[0])

    # alldeps2 = []
    # deps = list(tree.get_dependencies())
    # def iterate_deps_gen(initial_term):
    #     global alldeps2
    #     depnos = []
    #     for no in deps:
    #         if no.get_from() == initial_term:
    #             depnos.append(no)
    #     print "DEPNOS", ["H {} D {}".format(x.get_from(), x.get_to()) for x in depnos]
    #     alldeps2.extend(["H {} D {}".format(x.get_from(), x.get_to()) for x in depnos])
    #     for dn in depnos:
    #         #iterate_deps_gen(dn.get_to())
    #         #yield alldeps2
    #         yield iterate_deps(dn.get_to())
    #
    # for x in iterate_deps_gen("t7"):
    #     print "x"