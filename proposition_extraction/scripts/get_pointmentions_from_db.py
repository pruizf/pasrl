"""Some tests to get the pointmention text out of DB"""

__author__ = 'Pablo Ruiz'
__date__ = '25/04/16'
__email__ = 'pabloruizfabo@gmail.com'

import django
import time
import ui

from ui.models import PointMention, Proposition, Sentence


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


props = Proposition.objects.all()

s2ptm = {}

print "Hash sentences to pointmentions"
for idx, prop in enumerate(props):
    #propid = ptm.proposition
    sid = prop.sentence
    ptm = prop.pointMention
    s2ptm.setdefault(sid, []).append(ptm.text)
    if not idx % 5000:
        print "Done {} pointmentions, {}".format(
            idx, time.asctime(time.localtime()))


print "Dedup pointmentions"
for idx, sid in enumerate(sorted(s2ptm)):
    s2ptm[sid] = dedup_list_keep_order(s2ptm[sid])
    if not idx % 5000:
        print "Done {} pointmentions, {}".format(
            idx, time.asctime(time.localtime()))



