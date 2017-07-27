"""test dkpro with jython"""
__author__ = 'Pablo Ruiz'
__date__ = '09/10/15'

# import sys
# print sys.path

# for x in ['/home/pablo/usr/local/jip-0.9.6', '/home/pablo/.venvburrito/lib/python2.7/site-packages/setuptools-5.4-py2.7.egg', '/home/pablo/.venvburrito/lib/python2.7/site-packages/pip-1.4.1-py2.7.egg', '/usr/local/lib/python2.7/dist-packages/pylint-1.3.0-py2.7.egg', '/usr/local/lib/python2.7/dist-packages/astroid-1.2.0-py2.7.egg', '/usr/local/lib/python2.7/dist-packages/logilab_common-0.62.1-py2.7.egg', '/usr/local/lib/python2.7/dist-packages/PyMySQL-0.6.2-py2.7.egg', '/usr/local/lib/python2.7/dist-packages/rdfsim-0.3-py2.7.egg', '/usr/local/lib/python2.7/dist-packages/rdf-0.9a6-py2.7.egg', '/usr/local/lib/python2.7/dist-packages/pip-7.1.2-py2.7.egg', '/usr/local/lib/python2.7/dist-packages/titlecase-0.7.2-py2.7.egg', '/home/pablo/.venvburrito/lib/python2.7/site-packages', '/usr/lib/python2.7', '/usr/lib/python2.7/plat-x86_64-linux-gnu', '/usr/lib/python2.7/lib-tk', '/usr/lib/python2.7/lib-old', '/usr/lib/python2.7/lib-dynload', '/usr/local/lib/python2.7/dist-packages', '/usr/lib/python2.7/dist-packages', '/usr/lib/python2.7/dist-packages/PILcompat', '/usr/lib/python2.7/dist-packages/gtk-2.0', '/usr/lib/pymodules/python2.7', '/usr/lib/python2.7/dist-packages/ubuntu-sso-client', '/usr/lib/python2.7/dist-packages/wx-2.8-gtk2-unicode']:
#     sys.path.append(x)
# print sys.path
#!/usr/bin/env jython
# Fix classpath scanning - otherise uimaFIT will not find the UIMA types
from java.lang import Thread
from org.python.core.imp import *
Thread.currentThread().contextClassLoader = getSyspathJavaLoader()

# Dependencies and imports for DKPro modules
from jip.embed import require
require('de.tudarmstadt.ukp.dkpro.core:de.tudarmstadt.ukp.dkpro.core.opennlp-asl:1.6.2')
from de.tudarmstadt.ukp.dkpro.core.opennlp import *
require('de.tudarmstadt.ukp.dkpro.core:de.tudarmstadt.ukp.dkpro.core.languagetool-asl:1.6.2')
from de.tudarmstadt.ukp.dkpro.core.languagetool import *
require('de.tudarmstadt.ukp.dkpro.core:de.tudarmstadt.ukp.dkpro.core.maltparser-asl:1.6.2')
from de.tudarmstadt.ukp.dkpro.core.maltparser import *
require('de.tudarmstadt.ukp.dkpro.core:de.tudarmstadt.ukp.dkpro.core.io.text-asl:1.6.2')
from de.tudarmstadt.ukp.dkpro.core.io.text import *
require('de.tudarmstadt.ukp.dkpro.core:de.tudarmstadt.ukp.dkpro.core.io.conll-asl:1.6.2')
from de.tudarmstadt.ukp.dkpro.core.io.conll import *

# uimaFIT imports
from org.apache.uima.fit.pipeline.SimplePipeline import *
from org.apache.uima.fit.factory.AnalysisEngineFactory import *
from org.apache.uima.fit.factory.CollectionReaderFactory import *

runPipeline(
  createReaderDescription(TextReader,
    TextReader.PARAM_SOURCE_LOCATION, "document.txt",
    TextReader.PARAM_LANGUAGE, "en"),
  createEngineDescription(OpenNlpSegmenter),
  createEngineDescription(OpenNlpPosTagger),
  createEngineDescription(LanguageToolLemmatizer),
  createEngineDescription(MaltParser),
  createEngineDescription(Conll2006Writer,
    Conll2006Writer.PARAM_TARGET_LOCATION, "."));