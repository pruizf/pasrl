"""Call climatetagger API"""
__author__ = 'Pablo Ruiz'
__date__ = '25/04/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
import os
import requests
import simplejson
import time

#curl "http://api.reegle.info/service/extract?text=this+is+a+text+about+mitigation+and+adaptation+and+rise+in+sea+level+and+it+also+talks+about+carbon+dioxide+concentrations+and+something+called+halocarbons&token=mettre_son_token_obtenu_chez_api.climatetagger.net"
# &format=json&locale=en"
#98ec02dd8bc94631844a51f9e1212e02

# IO
indir = "/home/pablo/projects/ie/corpora/pointmentions_04252016"
outdir = os.path.join("/home/pablo/projects/ie/out/el",
                      os.path.basename(indir))

# Config
token = "CLIMATETAGGER API TOKEN"

endpoint = "http://api.reegle.info/service/extract"

params = {"format": "json", "locale": "en",
          "token": token}
sleepfor = 1 #secs


# Process
if not os.path.exists(outdir):
    os.makedirs(outdir)

dones = 0
for fn in os.listdir(indir):
    try:
        if os.stat(os.path.join(outdir, fn)):
            print "- skip [{}]".format(fn)
            continue
    except OSError:
        pass
    print "- {}".format(fn)
    with codecs.open(os.path.join(indir, fn), "r", "utf8") as infd:
        txt = infd.read()
    params.update(dict(text=txt))
    res = requests.get(endpoint, params)
    with codecs.open(os.path.join(outdir, fn), "w", "utf8") as outfd:
        outfd.write(simplejson.dumps(res.json()))
    dones += 1
    if not dones % 1000:
        print "== Done [{}], {} ==".format(
            dones, time.strftime("%H:%M:%S", time.localtime()))
    time.sleep(sleepfor)

