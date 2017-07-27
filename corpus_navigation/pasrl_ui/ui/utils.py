"""General utilities for all apps of the project"""

__author__ = 'Pablo Ruiz'
__date__ = '19/04/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
from django.conf import settings


def dedup_list_keep_order(seq, idfun=None):
    """
    Deduplicate a list (order preserving)
    http://www.peterbe.com/plog/uniqifiers-benchmark
    """
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


# def load_json_escapes(ef=settings.EXT_DATA["json_escapes"]):
#     """Return JSON escape info"""
#     rawlines = codecs.open(ef, "r", "utf8").readlines()
#     reps = {}
#     for ll in rawlines:
#         if ll.startswith("#"):
#             continue
#         try:
#             sl = ll.split("\t")
#             code = ur"\{}".format(sl[0].lower())
#             ch = sl[1].strip()
#             reps[code] = ch
#         except IndexError:
#             continue
#     return reps


def load_json_escapes(ef=settings.EXT_DATA["json_escapes"]):
    """Return JSON escape info"""
    rawlines = codecs.open(ef, "r", "utf8").readlines()
    reps = {}
    for ll in rawlines:
        if ll.startswith("#"):
            continue
        try:
            sl = ll.split("\t")
            code = ur"\{}".format(sl[0].lower())
            ch = sl[1].strip()
            reps[ch] = code
        except IndexError:
            continue
    return reps
