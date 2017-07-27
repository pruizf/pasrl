#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models import Count
from django.shortcuts import render
from django.http import JsonResponse
from urllib2 import urlopen, quote, unquote

from .models import Proposition, EntityMention, KeyPhrase, Sentence,\
    Document, AgrDis, ActorMention, PointMention, Point

import utils as ut
import codecs
import json
import logging
import math
import re
import time

logger = logging.getLogger(__name__)
pager = 50

VDBG = True  # to debug these views


sortKey2Param = {
    'actor':'actorMention__actor__name',
    'action':'predicateMention__predicate__name',
    'actiontype':'predicateMention__predicate__name',
    'point':'pointMention__text',
    'cop':'sentence__document__cop',
    'year':'sentence__document__copyear',
    'conf':'conf',
    }


# Create your views here.
def index(request):
    request.session.set_test_cookie()
    request.session['first'] = 0
    request.session['last'] = pager
    request.session['sort'] = "actor"
    request.session['sort_order'] = "asc"
    # hardcoding total number of sentences for now
    request.session["allsentnames"] = 15394
    # json escapes info
    if not "jsesc" in request.session or len(request.session["jsesc"]) == 0:
        request.session["jsesc"] = ut.load_json_escapes()
        # import pdb;pdb.set_trace()
    return render(request, 'ui/index.html')


def index_agd(request):
    request.session.set_test_cookie()
    request.session['first'] = 0
    request.session['last'] = pager
    return render(request, 'ui/index_agd_only.html')


def solrdoc(request):
    data = request.GET
    doc_id = data["doc_id"]
    sent_id = data["sent_id"]
    res = _get_solr_documents([doc_id])

    sent = Sentence.objects.get(id=sent_id)
    regex_sent = re.sub('``', r'\\u201c', sent.text) #handle quote marks variations
    regex_sent = re.sub('\'\'', r'\\u201d', regex_sent) #handle quote marks variations
    regex_sent = re.sub('\'', r'\\u2019', regex_sent) #handle quote marks variations
    #regex_sent = re.sub(r'\(', '\(', regex_sent) #escape parentheses
    #regex_sent = re.sub(r'\)', '\)', regex_sent) #escape parentheses
    # other json escapes
    # for ke in request.session["jsesc"]:
    #     regex_sent = re.sub(ke, re.escape(request.session["jsesc"][ke]),
    #                          regex_sent)
        #regex_sent = regex_sent.replace(ke, request.session["jsesc"][ke])
    finalre = re.compile(r"(" + re.escape(regex_sent) + ')', re.I|re.U)
    highlighted_res = re.sub(finalre, r'<mark>\g<1></mark>', res)
    return JsonResponse(highlighted_res, safe=False)


def dbsen(request):
    """
    Get sentence with sentence id, FROM DB, not from Solr.
    @note: now used to get sentence for a proposition in div #records_table
    """
    data = request.GET
    sent_id = data["sent_id"]

    sent = Sentence.objects.get(id=sent_id)
    text = sent.text
    cop = sent.document.cop
    year = sent.document.copyear
    name = sent.name

    return JsonResponse(dict(text=text, cop=cop, year=year,
                             name=name), safe=False)


def pager_reset(request):
    request.session['first'] = 0
    request.session['last'] = pager
    return JsonResponse(request.session['first'], safe=False)


def pager_next(request):
    if (int(request.session.get('first', 0)) + pager) < int(request.session['nb_records']):
        first = int(request.session.get('first', 0)) + pager
        request.session['first'] = first
        request.session['last'] = first + pager
    else:
        request.session['last'] = int(request.session['nb_records'])
    return JsonResponse(request.session['first'], safe=False)


def pager_prev(request):
    if (int(request.session.get('first', 0)) - pager) >= 0:
        first = int(request.session.get('first', 0)) - pager
        request.session['first'] = first
        request.session['last'] = first + pager
    return JsonResponse(request.session['first'], safe=False)


def actors(request, tab, sort=None):
    """
    Called by main form and ajax requests
    Finds records in db according to GET params
    Orders by actors
    Returns JSON
    """
    data = request.GET
    logger.warn("Sort : {}".format(sort))

    res = {}
    if sort:
        if sort == "default":
            request.session['sort'] = "actor"
        elif request.session['sort'] == sort:
            request.session['sort_order'] = "asc" if request.session['sort_order'] == "desc" else "desc"
        else:
            request.session['sort'] = sort

    logger.warn("Sort : {}".format(request.session['sort']))

    # sentence.name is the solr id for the sentence
    (records, docs, sen_infos, counts) = _find_propositions(
        request, data, (request.session['sort_order'],
                        sortKey2Param[request.session['sort']],
                        'predicateMention__predicate__name',
                        'sentence__document__cop'))
    # left panel ------------------------------------------
    res['db_response'] = records
    # counters info
    res['totalprops'] = counts["totprops"]
    res['totaldocs'] = counts["nb_docs"]
    res['totalsentences'] = counts["nb_sentences"]
    res['curpage'] = counts["curpage"]
    res['totpages'] = counts["totpages"]
    # right panel -----------------------------------------
    if tab == "sen":
        res['docs'] = _get_solr_sentences(sen_infos, request)
        if not _query_is_empty_ignore_date_and_confidence(data):
            res['totalsentences_for_solrq'] = request.session["sents_for_solrq"]
        else:
            res["totalsentences_for_solrq"] = request.session["allsentnames"]
    elif tab == "doc":
        res['docs'] = _get_solr_documents(docs)
    elif tab == "dbp":
        res['docs'] = _find_dbpedia(request, data)
    elif tab == "rgl":
        #res['docs'] = _find_dbpedia(request, data, linker="rgl")
        res['docs'] = _find_dbpedia(request, data, linker="rgl")
    elif tab == "kp":
        res['docs'] = _find_kps(request, data)
    return JsonResponse(res, safe=False)


def actions(request, tab, sort=None):
    """
    Called by main form and ajax requests
    Finds records in db according to GET params
    Orders by predicates
    Returns JSON
    """
    data = request.GET
    preds = request.GET.getlist('predicate')
    res = {}
    logger.warn("Sort : {}".format(sort))

    sort_order = "asc"
    if sort:
        if sort == "default":
            request.session['sort'] = "actiontype"
        elif request.session['sort'] == sort:
            request.session['sort_order'] = "asc" if request.session['sort_order'] == "desc" else "desc"
        else:
            request.session['sort'] = sort

    logger.warn("Sort : {}".format(request.session['sort']))
    (records, docs, sen_infos, counts) = _find_propositions(
        request, data, (request.session['sort_order'],
                        sortKey2Param[request.session['sort']],
                        'actorMention__actor__name',
                        'sentence__document__cop'), preds)
    # left panel
    res['db_response'] = records
    # counters info
    res['totalprops'] = counts["totprops"]
    res['totaldocs'] = counts["nb_docs"]
    res['totalsentences'] = counts["nb_sentences"]
    res['curpage'] = counts["curpage"]
    res['totpages'] = counts["totpages"]
    # right panel
    # sentence.name is the solr id for the sentence
    if tab == "sen":
        res['docs'] = _get_solr_sentences(sen_infos, request)
        if not _query_is_empty_ignore_date_and_confidence(data):
            res['totalsentences_for_solrq'] = request.session["sents_for_solrq"]
        else:
            res["totalsentences_for_solrq"] = request.session["allsentnames"]
    elif tab == "doc":
        res['docs'] = _get_solr_documents(docs)
    elif tab == "dbp":
        res['docs'] = _find_dbpedia(request, data)
    elif tab == "rgl":
        #res['docs'] = _find_dbpedia(request, data, linker="rgl")
        res['docs'] = _find_dbpedia(request, data, linker="dbp")
    elif tab == "kp":
        res['docs'] = _find_kps(request, data)
    return JsonResponse(res, safe=False)


def fullsent(request, sid):
    """
    Given a sentence id, return sentence text and name attribute
    @note: Not used. This was for tests and even if ajax.js has
    a function calling this, the function itself is activated by
    an element that is no longer in the templates.
    """
    res = {}
    txt = Sentence.objects.filter(id=sid).values('text', 'name')
    res['name'] = txt[0]['name']
    res['text'] = txt[0]['text']
    return JsonResponse(res, safe=False)


def eksent(request, sidstr, ek):
    """
    For a given search term and series of sentence id, returns sentence
    and related infos
    @param sidstr: sentence id series, separated by a period
    @param ek: entity or keyphrase
    @note: used in agree disagree tab, to get the sentence for a kp or dbp term
    """
    # logger.warn(sidstr)
    res = []
    idlist = set(sidstr.split("."))
    #logger.warn(idlist)
    stobs= Sentence.objects.filter(id__in=idlist)
    # logger.warn("stobs len: {}".format(len(stobs)))
    for sto in stobs:
        sid = sto.id
        name = sto.name
        text = sto.text
        docid = sto.document.id
        cop = sto.document.cop
        year = sto.document.date.year
        # logger.warn("COP: {}, YEAR: {}".format(cop, year))
        res.append(dict(sid=sid, name=name, text=text, docid=docid,
                        cop=cop, year=year, ek=ek))
    return JsonResponse(res, safe=False)


def agrdis(request):
    """
    Can be used to populate DBpedia and KeyPhrase tables of
    AgreeDisagree View tab
    """
    data = request.GET
    res = {}
    (res['entis'], res['rgls'], res['kps'],
     res['entid'], res['rgld'], res['kpd']) = _find_agrdis_annots(request, data)
    return JsonResponse(res, safe=False)


def ekprop(request, ptmidstr, mode="ek", tohl=None):
    """
    Called by clicking on an entity, keyphrase, or sentence, returns
    propositions whose pointmention contain the keyphrase or
    an entity mention for the entity
    @param mode: 'ek' for req from entity, reegle or kp tabs, 'sen'
    for sentence tab
    @param tohl: string to highlight in the proposition texts
    """
    # logger.warn(ptmidstr)
    res = []
    idlist = set([id_ for id_ in ptmidstr.split(".") if int(id_) >= 0])
    #logger.warn(idlist)
    if mode == "ek":
        propobs = Proposition.objects.filter(pointMention__in=idlist)
    elif mode == "sen":
        propobs = Proposition.objects.filter(id__in=idlist)
    # logger.warn("propobs len: {}".format(len(propobs)))
    for prop in propobs:
        actor = prop.actorMention.actor.name
        predicate = prop.predicateMention.text
        point = prop.pointMention.text
        # highlight kp, dbp, rgl
        if tohl is not None and len(tohl) > 0:
            point = _hl(tohl, point)
        # highlight solrq term if click on sentence
        if mode == "sen":
            if "lastqd" in request.session:
                try:
                    assert ("solrq" in request.session["lastqd"] and
                            len(request.session["lastqd"]["solrq"]) > 0)
                    print request.session["lastqd"]["solrq"]
                    point = _hl(request.session["lastqd"]["solrq"], point)
                except AssertionError:
                    print "<><> NO LASTQD"
        doc = prop.sentence.document.name
        predtype = prop.predicateMention.predicate.ptype
        year = prop.sentence.document.date.year
        cop = prop.sentence.document.cop
        city = prop.sentence.document.city
        sid = prop.sentence.id
        confid = prop.conf
        res.append(dict(actor=actor, predicate=predicate, point=point,
                        ptype=predtype, year=year, cop=cop, city=city,
                        sid=sid, doc=doc, conf=confid))
    #import pdb;pdb.set_trace()
    return JsonResponse(res, safe=False)


def _hl(sq, txt):
    """
    Highlight the sequence of characters sq in text txt
    respecting original case in txt
    """
    hlfmt = ur"<span class='hldef'>{}</span>"
    sqpp = unquote(sq).replace("_", " ")
    sqre = re.compile(ur"\b({})\b".format(sqpp), re.I)
    sqintxt = re.search(sqre, txt)
    if sqintxt and len(sqintxt.groups()) > 0:
        return re.sub(sqre, hlfmt.format(sqintxt.group(1)), txt)
    else:
        return txt


def _find_dbpedia(request, data, linker="def"):
    #sids = set()
    # create session variables if needed
    request.session.setdefault('ptmids_dbp', {})
    # create filter
    if VDBG:
        logger.warn("\n== START DBP QUERY ==")
    filter = _create_proposition_filter(data, request)
    uifilter = _load_entity_filter()
    esubs = _load_entity_subs()
    if VDBG:
        logger.warn("my DBP_FILTER: {}".format(filter))
    # apply filter
    do_new_query = True
    if not filter or filter['actorMention__actor__name__icontains'] == '':
        if ('pointMention__point__name__icontains' in filter and
            filter['pointMention__point__name__icontains'] == '' or
            'pointMention__point__name__icontains' not in filter):
            if VDBG:
                logger.warn("EL v2 NOFILTER get all props for query {}".format(
                    time.asctime(time.localtime())))
                logger.warn("EL v2 NOFILTER, F [{}]".format(repr(filter)))
            try:
                #sids = request.session['sids']
                ptmids = request.session['ptmids_dbp'][repr(filter)]
                if VDBG:
                    logger.warn("    From SESSION\n")
            except KeyError:
                if VDBG:
                    logger.warn("    List NEW\n")
                # fof session, use values cos dict is json serializable, QuerySet isn't
                # https://stackoverflow.com/questions/23596433/
                #sids = [ob["sentence_id"] for ob in Proposition.objects.all().values()]
                #ptmids = [ob["pointMention_id"] for ob in Proposition.objects.all().values()]
                ptmids = [ob["pointMention_id"] for ob in
                          Proposition.objects.filter(**filter).values()]
                #request.session['sids'] = sids
                request.session['ptmids_dbp'][repr(filter)] = ptmids
            #logger.warn("done {}".format(time.asctime(time.localtime())))
            do_new_query = False
        else:
            do_new_query = True
    if do_new_query:
        if VDBG:
            logger.warn("EL v2 FILTER get SOME props for query {}".format(
                time.asctime(time.localtime())))
            logger.warn("EL Will use this filter: {}".format(repr(filter)))
        #sids = set()
        ptmids = set()
        propositions = Proposition.objects.filter(**filter)
        for prop in propositions:
            #sids.add(prop.sentence)
            ptmids.add(prop.pointMention)
        #logger.warn("done {}".format(time.asctime(time.localtime())))

    entires = []
    #logger.warn("v2 get entities {}".format(time.asctime(time.localtime())))
    #entis = EntityMention.objects.filter(sentence__in=sids,

    # the counts are neutralized below cos sorting by (and giving as count) the nbr
    # of propositions; i could just not count here
    if linker == "def":
        entis = EntityMention.objects.filter(pointmentions__in=ptmids, linker="def",
            confidence__gt=0.05, active=True).values('entity__name').annotate(
            enticount=Count('text')).order_by('-enticount')
    else:
        entis = EntityMention.objects.filter(pointmentions__in=ptmids, linker="rgl",
            confidence__gt=0.05, active=True).values(
                'entity__name', 'entity__eurl').annotate(
            enticount=Count('text')).order_by('-enticount')

    if linker == "def":
        emids = EntityMention.objects.filter(pointmentions__in=ptmids,
            linker="def", confidence__gt=0.05, active=True).values('entity__name',
                                                                   #'id')
                                                                   'pointmentions__id')
    else:
        emids = EntityMention.objects.filter(pointmentions__in=ptmids, linker="rgl",
            confidence__gt=0.05, active=True).values('entity__name',
                                                     #'id')
                                                     'pointmentions__id',
                                                     'entity__eurl')

    emid2ptmid = {}
    for em in emids:
        emid2ptmid.setdefault(em["entity__name"], set())
        #emid2ptmid[em["entity__name"]].add(em["id"])
        emid2ptmid[em["entity__name"]].add(em["pointmentions__id"])

    #logger.warn("done {}".format(time.asctime(time.localtime())))
    # sorting by decreasing nbr of pointmentions
    for enti in sorted([eob for eob in entis
                        if eob['entity__name'] not in uifilter],
                       key=lambda ent: -len(emid2ptmid[ent['entity__name']])):
        try:
            if linker == "def":
                label = esubs[enti['entity__name']]
            else:
                label = esubs[enti['entity__name']]
                eurl = enti['entity__eurl']
        except KeyError:
            if linker == "def":
                label = enti['entity__name']
            else:
                label = enti['entity__name']
                eurl = enti['entity__eurl']
        ecount = enti['enticount']
        if linker == "def":
            wurl = u"http://en.wikipedia.org/wiki/{}".format(label)
        else:
            # still called 'wurl' even if the 'w' stood for 'wikipedia' before
            wurl = u"http://reegle.info/glossary/{}".format(eurl)
        ptmidstr = ".".join([str(s) for s in emid2ptmid[enti["entity__name"]]])
        #entires.append(dict(label=label, ecount=ecount, wurl=wurl,
        entires.append(dict(label=label,
                            ecount=len(emid2ptmid[enti["entity__name"]]),
                            wurl=wurl,
                            ptmidstr=ptmidstr))
        #logger.warn(u"{}\t{}".format(label, ecount))
    #import pdb;pdb.set_trace()
    return json.dumps(entires)


def _find_kps(request, data):
    #sids = set()
    # create session vars if needed
    request.session.setdefault('sids_kp', {})
    request.session.setdefault('ptmids_kp', {})
    # create filter
    if VDBG:
        logger.warn("\n== START KP QUERY ==")
    filter = _create_proposition_filter(data, request)
    uifilter = _load_kp_filter()
    if VDBG:
        logger.warn("my KP_FILTER: {}".format(filter))
    # apply filter
    do_new_query = True
    if not filter or filter['actorMention__actor__name__icontains'] == '':
        if ('pointMention__point__name__icontains' in filter and
            filter['pointMention__point__name__icontains'] == '' or
            'pointMention__point__name__icontains' not in filter):
            if VDBG:
                logger.warn("KP v2 NOFILTER get all props for query {}".format(
                    time.asctime(time.localtime())))
                logger.warn("KP v2 NOFILTER, F [{}]".format(repr(filter)))
            try:
                #sids = request.session['sids'][repr(filter)]
                ptmids = request.session['ptmids_kp'][repr(filter)]
                if VDBG:
                    logger.warn("    From SESSION\n")
            except KeyError:
                if VDBG:
                    logger.warn("    List NEW\n")
                # for session, use values cos dict is json serializable, QuerySet isn't
                # https://stackoverflow.com/questions/23596433/

                #sids = [ob["sentence_id"] for ob in Proposition.objects.all().values()]
                #ptmids = [ob["pointMention_id"] for ob in Proposition.objects.all().values()]
                ptmids = [ob["pointMention_id"] for ob in
                          Proposition.objects.filter(**filter).values()]
                #request.session['sids'] = sids
                request.session['ptmids_kp'][repr(filter)] = ptmids
            #logger.warn("done {}".format(time.asctime(time.localtime())))
            do_new_query = False
        else:
            do_new_query = True
    if do_new_query:
        logger.warn("KP v2 FILTER get SOME props for query {}".format(
            time.asctime(time.localtime())))
        logger.warn("KP Will use this filter: {}".format(repr(filter)))
        #sids = set()
        ptmids = set()
        propositions = Proposition.objects.filter(**filter)
        for prop in propositions:
            #sids.add(prop.sentence)
            ptmids.add(prop.pointMention)
        #logger.warn("done {}".format(time.asctime(time.localtime())))

    kpres = []
    #logger.warn("v2 get entities {}".format(time.asctime(time.localtime())))
    # kps = KeyPhrase.objects.filter(sentence__in=sids).values('text').annotate(
    #     kpcount=Count('text')).order_by('-kpcount')
    kpids = KeyPhrase.objects.filter(pointmentions__in=ptmids)
    #kps = KeyPhrase.objects.filter(sentence__in=sids).values('text').annotate(
    #    kpcount=Count('text')).order_by('-kpcount')

    # below sorting by nbr of pointmentions attached to kp,
    # which neutralizes whatever i count here ... could remove the count in fact
    kps = KeyPhrase.objects.filter(id__in=kpids).values('text').annotate(
        kpcount=Count('text')).order_by('-kpcount', 'text')
        #kpcount=Count('pointmentions', distinct=True)).order_by('-kpcount', 'text')
    #logger.warn("done {}".format(time.asctime(time.localtime())))FOR SELE

    kpids4sents = KeyPhrase.objects.filter(pointmentions__in=ptmids).values(
        'text', 'pointmentions__id')
    kpid2ptmid = {}
    for kpm in kpids4sents:
        kpid2ptmid.setdefault(kpm["text"], set())
        kpid2ptmid[kpm["text"]].add(kpm["pointmentions__id"])

    # sorting by decreasing number of pointmentions attached to the kp
    for kp in sorted([kob for kob in kps if kob['text'] not in uifilter],
                      key=lambda kph: -len(kpid2ptmid[kph["text"]])):
        kptext = kp['text']
        # kpcount = kp['kpcount']
        ptmidstr = ".".join([str(s) for s in kpid2ptmid[kp["text"]]])
        # kpres.append(dict(label=kptext, ecount=kpcount,
        #                   ptmidstr=ptmidstr))
        kpres.append(dict(label=kptext, ecount=len(kpid2ptmid[kp["text"]]),
                          ptmidstr=ptmidstr))
        #logger.warn(u"{}\t{}".format(label, ecount))
    #import pdb;pdb.set_trace()
    return json.dumps(kpres)


def _find_dbpedia_sentence_level(request, data):
    #sids = set()
    filter = _create_proposition_filter(data, request)
    uifilter = _load_entity_filter()
    esubs = _load_entity_subs()
    #logger.warn("my FILTER: {}".format(filter))

    do_new_query = True
    if not filter or filter['actorMention__actor__name__icontains'] == '':
        if ('pointMention__point__name__icontains' in filter and
            filter['pointMention__point__name__icontains'] == '' or
            'pointMention__point__name__icontains' not in filter):
            #logger.warn("EL v2 NOFILTER get all props for query {}".format(time.asctime(time.localtime())))
            #sids = request.session.get('sids', [ob["sentence_id"] for ob in Proposition.objects.all()])
            try:
                sids = request.session['sids']
                #logger.warn("from session")
            except KeyError:
                #logger.warn("new")
                # use values cos dict is json serializable, QuerySet isn't
                # https://stackoverflow.com/questions/23596433/
                sids = [ob["sentence_id"] for ob in
                        Proposition.objects.all().values()]
                request.session['sids'] = sids
            #logger.warn("done {}".format(time.asctime(time.localtime())))
            do_new_query = False
        else:
            do_new_query = True
    if do_new_query:
        #logger.warn("EL v2 FILTER get props for query {}".format(time.asctime(time.localtime())))
        sids = set()
        propositions = Proposition.objects.filter(**filter)
        for prop in propositions:
            sids.add(prop.sentence)
        #logger.warn("done {}".format(time.asctime(time.localtime())))

    entires = []
    #logger.warn("v2 get entities {}".format(time.asctime(time.localtime())))
    entis = EntityMention.objects.filter(sentence__in=sids,
        confidence__gt=0.05, active=True).values('entity__name').annotate(
        enticount=Count('text')).order_by('-enticount')
    #logger.warn("done {}".format(time.asctime(time.localtime())))
    for enti in [eob for eob in entis if eob['entity__name'] not in uifilter]:
        try:
            label = esubs[enti['entity__name']]
        except KeyError:
            label = enti['entity__name']
        ecount = enti['enticount']
        wurl = u"http://en.wikipedia.org/wiki/{}".format(label)
        entires.append(dict(label=label, ecount=ecount, wurl=wurl))
        #logger.warn(u"{}\t{}".format(label, ecount))
    return json.dumps(entires)


def _find_dbpedia_slow(request, data, sort_params):
    #logger.warn("get all props for query {}".format(time.asctime(time.localtime())))
    all_records, _, _, _ = _find_propositions(request, data, sort_params, paginate=False)
    #logger.warn("done {}".format(time.asctime(time.localtime())))

    #records, _ = _find_propositions(request, data, sort_params, paginate=True)
    sids = [int(it["sid"]) for it in json.loads(all_records)]
    entires = []

    #logger.warn("get entities {}".format(time.asctime(time.localtime())))
    entis = EntityMention.objects.filter(sentence__in=sids,
        confidence__gt=0.05, active=True).values('entity__name').annotate(
        enticount=Count('text')).order_by('-enticount')
    #logger.warn("done {}".format(time.asctime(time.localtime())))
    for enti in entis:
        label = enti['entity__name']
        ecount = enti['enticount']
        wurl = u"http://en.wikipedia.org/wiki/{}".format(label)
        entires.append(dict(label=label, ecount=ecount, wurl=wurl))
        #logger.warn(u"{}\t{}".format(label, ecount))
    return json.dumps(entires)


def _find_kps_sentence_level(request, data):
    #sids = set()
    filter = _create_proposition_filter(data, request)
    uifilter = _load_kp_filter()
    #logger.warn("my FILTER: {}".format(filter))

    do_new_query = True
    if not filter or filter['actorMention__actor__name__icontains'] == '':
        if ('pointMention__point__name__icontains' in filter and
            filter['pointMention__point__name__icontains'] == '' or
            'pointMention__point__name__icontains' not in filter):
            #logger.warn("KP v2 NOFILTER get all props for query {}".format(time.asctime(time.localtime())))
            #sids = request.session.get('sids', [ob["sentence_id"] for ob in Proposition.objects.all()])
            try:
                sids = request.session['sids']
                #logger.warn("from session")
            except KeyError:
                #logger.warn("new")
                # use values cos dict is json serializable, QuerySet isn't
                # https://stackoverflow.com/questions/23596433/
                sids = [ob["sentence_id"] for ob in Proposition.objects.all().values()]
                request.session['sids'] = sids
            #logger.warn("done {}".format(time.asctime(time.localtime())))
            do_new_query = False
        else:
            do_new_query = True
    if do_new_query:
        #logger.warn("KP v2 FILTER get props for query {}".format(time.asctime(time.localtime())))
        sids = set()
        propositions = Proposition.objects.filter(**filter)
        for prop in propositions:
            sids.add(prop.sentence)
        #logger.warn("done {}".format(time.asctime(time.localtime())))

    kpres = []
    #logger.warn("v2 get entities {}".format(time.asctime(time.localtime())))
    kps = KeyPhrase.objects.filter(sentence__in=sids).values('text').annotate(
        kpcount=Count('text')).order_by('-kpcount')
    #logger.warn("done {}".format(time.asctime(time.localtime())))
    for kp in [kob for kob in kps if kob['text'] not in uifilter]:
        kptext = kp['text']
        kpcount = kp['kpcount']
        kpres.append(dict(label=kptext, ecount=kpcount))
        #logger.warn(u"{}\t{}".format(label, ecount))
    return json.dumps(kpres)


def _find_agrdis_annots(request, data):
    """
    Find the DBpedia entis and KeyPhrase objs for sentences who have a
    pointMention matching AgrDis objects whose actor mentions and reltype
    match the query.
    """
    # find actor mentions ---------------------------------
    a1 = data["actor1"]
    a2 = data["actor2"]
    rtype = data["rtype"]
    ids_a1 = ActorMention.objects.filter(
        actor__name=a1).values_list('id', flat=True)
    ids_a2 = ActorMention.objects.filter(
        actor__name=a2).values_list('id', flat=True)
    ids_a1a2 = list(ids_a1) + list(ids_a2)
    #logger.warn("actor1: {}\nactor2: {}\nrtype: {}".format(
    #    a1, a2, rtype))
    #logger.warn("actor mention ids: {}".format(ids_a1a2))

    # find sentence ids for the actor mentions ------------
    # note: session not v useful, could do without
    try:
        #sids = request.session['ad_sids'][u"{}-{}-{}".format(
        point_mtn_ids = request.session['ad_ptmids'][u"{}-{}-{}".format(
            str(a1), str(a2), str(rtype))]
        #logger.warn("from session agd")
    except KeyError:
        #logger.warn("new agd")
        point_mtn_ids = AgrDis.objects.filter(
            reltype=rtype,
            actorMention1__in=ids_a1a2,
            actorMention2__in=ids_a1a2).values_list('pointMention', flat=True)
        #logger.warn("point mention ids: {}".format(point_mtn_ids))
        # sids = Proposition.objects.filter(
        #     pointMention__in=point_mtn_ids).values_list('sentence', flat=True)
        #request.session['ad_sids'] = {}
        #request.session['ad_ptmids'] = {}
        # https://stackoverflow.com/questions/6720121/
        # serializing-result-of-a-queryset-with-json-raises-error
        # request.session['ad_sids'][fmtkey] = list(sids)
        #request.session['ad_sids'][fmtkey] = list(point_mtn_ids)
        request.session.setdefault('ad_ptmids', {})
        fmtkey = u"{}-{}-{}".format(str(a1), str(a2), str(rtype))
        request.session['ad_ptmids'].setdefault(fmtkey, list(point_mtn_ids))
    #logger.warn("sids: {}".format(sids))

    # load ui filters -------------------------------------
    enti_filter = _load_entity_filter()
    kp_filter = _load_kp_filter()

    # find dbpedia entities -------------------------------
    entires = []
    ed = {}
    #logger.warn("agd get entities {}".format(time.asctime(time.localtime())))
    #entis = EntityMention.objects.filter(sentence__in=sids,
    # counts neutralized below (counting nbr of sentences now)
    # (i.e. could also not count)
    entis = EntityMention.objects.filter(
        pointmentions__in=point_mtn_ids, linker="def",
        confidence__gt=0.05, active=True).values('entity__name').annotate(
        enticount=Count('entity__name')).order_by('-enticount', 'entity__name')
    e4sents = EntityMention.objects.filter(
        pointmentions__in=point_mtn_ids, linker="def",
        confidence__gt=0.05, active=True).values('entity__name', 'sentence')

    #logger.warn("done {}".format(time.asctime(time.localtime())))
    for enti in [eob for eob in entis if eob['entity__name'] not in enti_filter]:
        # figure out all sentence ids for each entity label
        ed.setdefault(enti['entity__name'], set())
        esids = [val['sentence'] for val in e4sents
                 if val['entity__name'] == enti['entity__name']]
        for esid in esids:
            ed[enti['entity__name']].add(esid)
        # aggregated mentions
        label = enti['entity__name']
        # count nbr of sentences attached to an enti (via the pointmention ids
        # in those sentences)
        #ecount = enti['enticount']
        ecount = len(set(esids))
        wurl = u"http://en.wikipedia.org/wiki/{}".format(label)
        entires.append(dict(label=label, ecount=ecount, wurl=wurl))
        #logger.warn(u"{}\t{}".format(label, ecount))
    for enti, eids in ed.items():
        eidstr = ".".join([str(s) for s in eids])
        ed[enti] = eidstr

    # find reegle entities --------------------------------
    rglres = []
    rgld = {}
    rglterms = EntityMention.objects.filter(
        pointmentions__in=point_mtn_ids, linker="rgl",
        confidence__gt=0.05, active=True).values(
        'entity__name', 'entity__eurl').annotate(
        enticount=Count('entity__name')).order_by('-enticount', 'entity__name')
    rgl4sents = EntityMention.objects.filter(
        pointmentions__in=point_mtn_ids, linker="rgl",
        confidence__gt=0.05, active=True).values('entity__name', 'sentence')

    #logger.warn("done {}".format(time.asctime(time.localtime())))
    for term in [tmob for tmob in rglterms if tmob['entity__name'] not in enti_filter]:
        # figure out all sentence ids for each entity label
        rgld.setdefault(term['entity__name'], set())
        rglsids = [val['sentence'] for val in rgl4sents
                   if val['entity__name'] == term['entity__name']]
        for rglsid in rglsids:
            rgld[term['entity__name']].add(rglsid)
        # aggregated mentions
        label = term['entity__name']
        eurl = term['entity__eurl']
        # count nbr of sentences attached to a rgl term (via the pointmention ids
        # in those sentences)
        #rglcount = term['enticount']
        rglcount = len(set(rglsids))
        wurl = u"http://reegle.info/glossary/{}".format(eurl)
        rglres.append(dict(label=label, ecount=rglcount, wurl=wurl))
        #logger.warn(u"{}\t{}".format(label, ecount))
    for term, sids in rgld.items():
        sidstr = ".".join([str(s) for s in sids])
        rgld[term] = sidstr

    # find keyphrases -------------------------------------
    kpres = []
    kpd = {}
    #logger.warn("agd get kps {}".format(time.asctime(time.localtime())))
    # counts neutralized below (count nbr of sentences now)
    # (i.e. could also not count)
    kps = KeyPhrase.objects.filter(pointmentions__in=point_mtn_ids).values(
        'text').annotate(kpcount=Count('text')).order_by('-kpcount', 'text')
    kp4sents = KeyPhrase.objects.filter(
       pointmentions__in=point_mtn_ids).values('text', 'sentence')
    #logger.warn("done {}".format(time.asctime(time.localtime())))
    for kp in [kob for kob in kps if kob['text'] not in kp_filter]:
        # figure out sentence-ids for each keyphrase
        kpd.setdefault(kp['text'], set())
        kpsids = [val['sentence'] for val in kp4sents
                  if val['text'] == kp['text']]
        for kpsid in kpsids:
            kpd[kp['text']].add(kpsid)
        # aggregated counts per kp
        kptext = kp['text']
        # count nbr of sentences attached to a kp (via the pointmention ids
        # in those sentences)
        # kpcount = kp['kpcount']
        kpcount = len(set(kpsids))
        # workaround NO LONGER NEEDED cos counts were sometimes one too many
        # limiting to nbr of sentences avoids this problem
        # if len(kpd[kp['text']]) <= kpcount:
        #     kpcount = len(kpd[kp['text']])
        kpres.append(dict(label=kptext, ecount=kpcount)),
        #logger.warn(u"{}\t{}".format(label, ecount))
    for kp, kpids in kpd.items():
        kpidstr = ".".join([str(s) for s in kpids])
        kpd[kp] = kpidstr
    # sort responses for display
    entires = sorted(entires, key=lambda er: (-er["ecount"], er["label"]))
    rglres = sorted(rglres, key=lambda rgr: (-rgr["ecount"], rgr["label"]))
    # yes, the kp count is called ecount (easier in ajax if same name)
    kpres = sorted(kpres, key=lambda kr: (-kr["ecount"], kr["label"]))
    return (json.dumps(entires), json.dumps(rglres), json.dumps(kpres),
            json.dumps(ed), json.dumps(rgld), json.dumps(kpd))


def _find_agrdis_annots_bkp(request, data):
    """
    Find the DBpedia entis and KeyPhrase objs for sentences who have a
    pointMention matching AgrDis objects whose actor mentions and reltype
    match the query.
    @note: this is an approximation, since the real answer would be restricting
    entities and keyphrases to the pointMention, not using the whole sentence.
    """
    # find actor mentions ---------------------------------
    a1 = data["actor1"]
    a2 = data["actor2"]
    rtype = data["rtype"]
    ids_a1 = ActorMention.objects.filter(
        actor__name=a1).values_list('id', flat=True)
    ids_a2 = ActorMention.objects.filter(
        actor__name=a2).values_list('id', flat=True)
    ids_a1a2 = list(ids_a1) + list(ids_a2)
    #logger.warn("actor1: {}\nactor2: {}\nrtype: {}".format(
    #    a1, a2, rtype))
    #logger.warn("actor mention ids: {}".format(ids_a1a2))

    # find sentence ids for the actor mentions ------------
    # note: session not v useful, could do without
    try:
        sids = request.session['ad_sids'][u"{}-{}-{}".format(
            str(a1), str(a2), str(rtype))]
        #logger.warn("from session agd")
    except KeyError:
        #logger.warn("new agd")
        point_mtn_ids = AgrDis.objects.filter(
            reltype=rtype,
            actorMention1__in=ids_a1a2,
            actorMention2__in=ids_a1a2).values_list('pointMention', flat=True)
        #logger.warn("point mention ids: {}".format(point_mtn_ids))
        sids = Proposition.objects.filter(
            pointMention__in=point_mtn_ids).values_list('sentence', flat=True)
        request.session['ad_sids'] = {}
        fmtkey = u"{}-{}-{}".format(str(a1), str(a2), str(rtype))
        # https://stackoverflow.com/questions/6720121/
        # serializing-result-of-a-queryset-with-json-raises-error
        request.session['ad_sids'][fmtkey] = list(sids)
    #logger.warn("sids: {}".format(sids))

    # load ui filters -------------------------------------
    enti_filter = _load_entity_filter()
    kp_filter = _load_kp_filter()

    # find dbpedia entities -------------------------------
    entires = []
    ed = {}
    #logger.warn("agd get entities {}".format(time.asctime(time.localtime())))
    entis = EntityMention.objects.filter(sentence__in=sids,
        confidence__gt=0.05, active=True).values('entity__name').annotate(
        enticount=Count('entity__name')).order_by('-enticount', 'entity__name')
    e4sents = EntityMention.objects.filter(sentence__in=sids,
        confidence__gt=0.05, active=True).values('entity__name', 'sentence')

    #logger.warn("done {}".format(time.asctime(time.localtime())))
    for enti in [eob for eob in entis if eob['entity__name'] not in enti_filter]:
        # figure out all sentence ids for each entity label
        ed.setdefault(enti['entity__name'], set())
        esids = [val['sentence'] for val in e4sents
                 if val['entity__name'] == enti['entity__name']]
        for esid in esids:
            ed[enti['entity__name']].add(esid)
        # aggregated mentions
        label = enti['entity__name']
        ecount = enti['enticount']
        wurl = u"http://en.wikipedia.org/wiki/{}".format(label)
        entires.append(dict(label=label, ecount=ecount, wurl=wurl))
        #logger.warn(u"{}\t{}".format(label, ecount))
    for enti, eids in ed.items():
        eidstr = ".".join([str(s) for s in eids])
        ed[enti] = eidstr

    # find keyphrases -------------------------------------
    kpres = []
    kpd = {}
    #logger.warn("agd get kps {}".format(time.asctime(time.localtime())))
    kps = KeyPhrase.objects.filter(sentence__in=sids).values('text').annotate(
        kpcount=Count('text')).order_by('-kpcount', 'text')
    kp4sents = KeyPhrase.objects.filter(sentence__in=sids).values('text', 'sentence')
    #logger.warn("done {}".format(time.asctime(time.localtime())))
    for kp in [kob for kob in kps if kob['text'] not in kp_filter]:
        # figure out sentence-ids for each keyphrase
        kpd.setdefault(kp['text'], set())
        kpsids = [val['sentence'] for val in kp4sents
                  if val['text'] == kp['text']]
        for kpsid in kpsids:
            kpd[kp['text']].add(kpsid)
        # aggregated counts per kp
        kptext = kp['text']
        kpcount = kp['kpcount']
        kpres.append(dict(label=kptext, ecount=kpcount))
        #logger.warn(u"{}\t{}".format(label, ecount))
    for kp, kpids in kpd.items():
        kpidstr = ".".join([str(s) for s in kpids])
        kpd[kp] = kpidstr
    return (json.dumps(entires), json.dumps(kpres),
            json.dumps(ed), json.dumps(kpd))


def _find_propositions(request, data, sort_params, paginate=True):
    """
    Finds propositions in db
    Filters by actor, predicate, point if given in request
    Returns all records otherwise
    @param request: request object
    @type request: django.http.HttpRequest
    @param data: list of http parameters
    @type data: dict
    @param sort_params: order_by argument tuple
    @type sort_params: tuple
    """

    # create filter (resetting pager as needed) -----------
    try:
        lastfilter = request.session["lastfilter"]
    except KeyError:
        lastfilter = repr({})
    #    actual filter creation
    filter = _create_proposition_filter(data, request)
    #    pager stuff
    if VDBG:
        logger.warn("{}LASTFILTER: {}".format("<" * 15, lastfilter))
        logger.warn("{}CURRFILTER: {}".format(">" * 15, filter))
    if lastfilter != repr(filter):
        first = 0
        last = pager
        request.session['first'] = first
        request.session['last'] = last
    else:
        first = request.session['first']
        last = request.session['last']
    curpage = math.floor(first / pager) + 1
    request.session["lastfilter"] = repr(filter)
    if VDBG:
        logger.warn("GIVEN TO FIND PROPS FILTER: {}".format(repr(filter)))

    #   apply filter
    propositions = Proposition.objects.filter(**filter)

    # parameters to sort results. note: Sort is applied to full unpaginated set
    if len(sort_params) > 0:
        if sort_params[0] == "asc":
            propositions = propositions.order_by(
                sort_params[1], sort_params[2], sort_params[3])
        else:
            propositions = propositions.order_by(
                "-"+sort_params[1], sort_params[2], sort_params[3])

    # result count bar / pagination info FOR ITEMS WITH PROPOSITIONS
    #   will return this dict for the counts
    counts = {}
    #   actual counts
    request.session['nb_records'] = len(propositions)
    totpages = math.floor(request.session['nb_records'] / pager)
    if request.session['nb_records'] % pager:
        totpages += 1
    if not bool(totpages):
        totpages += 1
    #   note: counting with .distinct() over a values_list won't work unless
    #   sort by sentence!
    #   https://stackoverflow.com/questions/10848809/
    #     request.session['nb_sentences'] = len(propositions.order_by(
    #         'sentence').values_list('sentence', flat=True).distinct())
    request.session['nb_docs'] = propositions.aggregate(
        Count('sentence__document', distinct=True))['sentence__document__count']
    request.session['nb_sentences'] = propositions.aggregate(
        Count('sentence', distinct=True))['sentence__count']
    #   add the infos to the dict to return
    counts["totprops"] = request.session['nb_records']
    counts["nb_docs"] = request.session['nb_docs']
    counts["nb_sentences"] = request.session['nb_sentences']
    counts["curpage"] = curpage
    counts["totpages"] = totpages

    # prepare response
    res = []
    doc_ids = set()
    # sen_names is list to sort sentences on right panel c/o proposition order
    # in L{_get_solr_sentences}
    sen_names = []

    if paginate:
        proplist = propositions[first:last]
    else:
        proplist = propositions
    for prop in proplist:
        actor = prop.actorMention.actor.name
        predicate = prop.predicateMention.text
        point = prop.pointMention.text
        doc = prop.sentence.document.name
        predtype = prop.predicateMention.predicate.ptype
        year = prop.sentence.document.date.year
        cop = prop.sentence.document.cop
        city = prop.sentence.document.city
        sid = prop.sentence.id
        sname = prop.sentence.name
        confid = prop.conf
        res.append(dict(actor=actor, predicate=predicate, point=point,
                        ptype=predtype, year=year, cop=cop, city=city,
                        sid=sid, doc=doc, conf=confid))
        doc_ids.add(doc)
        sen_names.append(sname)

    # deduplicate sen_names
    sen_names = ut.dedup_list_keep_order(sen_names)

    # SENTENCE NAMES FOR PROPOSITIONS, IN SORTING ORDER -----------------------
    if len(propositions) > 5000:
        try:
            # list of sen names so that can sort sentence panel on right
            sname4sort = request.session["sname4sort"][str(data)]
        except KeyError:
            sname4sort = _get_deduped_sentence_names_for_full_propset(
                propositions)
            request.session.setdefault("sname4sort", {})
            request.session["sname4sort"].setdefault(str(data), sname4sort)
    else:
        sname4sort = _get_deduped_sentence_names_for_full_propset(propositions)

    # SENTENCE-NAME TO PROP HASH ----------------------------------------------
    # if empty query, get sen-name to prop-id hash fr session (long to compute)
    if _query_is_empty(data):
        if ("sname2prop" in request.session and
                    len(request.session["sname2prop"]) > 0):
            sname2prop = request.session["sname2prop"]
        else:
            sname2prop = _hash_props_by_sentence_name(propositions)
            request.session["sname2prop"] = sname2prop
        # sth may be wrong if low nbr of propositions
        if len(request.session["sname2prop"]) < 5000:
            print "!!! Proposition count seems too low: {}".format(
                len(request.session["sname2prop"]))
    # also store in session for queries returning nbr of props > a threshold
    elif len(propositions) > 8000:
        try:
            sname2prop = request.session["sname2prop"][str(data)]
        except KeyError:
            sname2prop = _hash_props_by_sentence_name(propositions)
            request.session["sname2prop"][str(data)] = sname2prop
    else:
        sname2prop = _hash_props_by_sentence_name(propositions)

    # SENTENCE names from free-text query (i.e. regardless of has props or not)
    # besides sentence-names for propositions (paginated if paginate=True),
    # add sentence-names for records matching the query on the free-text field
    #     info for counts
    logger.warn("\n±± Sentence ids before free-text field: {}".format(
        len(sen_names)))
    sents_from_props = propositions.order_by('sentence').values_list(
        'sentence', flat=True).distinct()
    logger.warn("\n±± Sentence ids before free-text field 2: {}".format(
        len(set(sents_from_props))))
    #   actual sentence ids
    if "sentence__name__in" in filter and filter["sentence__name__in"]:
        sen_names.extend(filter["sentence__name__in"])
    logger.warn("±± Sentence ids after free-text field: {}\n".format(
        len(sen_names)))

    # DOC-ID for sentences from free-text query
    # add doc-names (aka Solr doc-id) for docs containing the sentences
    # from free-text field
    # note: could remove -[0-9]+$ from sentence name; may fail if doc not in DB
    logger.warn("\n§§ Document ids before free-text field: {}".format(
        len(doc_ids)))
    new_docids = Sentence.objects.filter(name__in=sen_names).values_list(
        'document', flat=True)
    new_docnames = Document.objects.filter(id__in=new_docids).values_list(
        'name', flat=True)
    doc_ids.update(list(new_docnames))
    logger.warn("§§ Document ids after free-text field: {}".format(
        len(doc_ids)))

    # sen_names: sentence name for Proposition objects, PAGINATED if
    #            paginate=True, and for Solr sentences
    #            matching the free-text query if there is one
    # sname4sort: Proposition.sentence.name for WHOLE QuerySet matching filter
    #             used later to sort displayed sentences in views
    #             following a free-text query. FIRST sents with props on current page,
    #             THEN in other pages, then sents without props
    #             List is needed cos computed over whole QuerySet, and sentences
    #             for solrq field may come from after the first page ...
    # sname2prop: hash of sentence-name to their propositions, WHOLE QuerySet
    #             used later to assign prop ids to the clickable sentences
    #TODO: not sure if needed to create sname2sort. You can pass sen_names and
    #TODO: sname2prop, sort by sen_names, move stuff in sname2prop not in sen_names
    #TODO: right after, and finally display what's not in sname2prop (no props)
    #TODO: current way you i bet you get v close to real sorting order for props c/o
    #TODO: sort_params in this function's signature

    return (json.dumps(res), doc_ids, (sen_names, sname4sort, sname2prop),
            counts)


def _hash_props_by_sentence_name(myprops):
    """
    Given a L{models.Proposition} QuerySet, return dict with Sentence.name
    keys and Proposition.id values for those Sentence.name
    """
    sname2prop = {}
    for prop in myprops:
        sname = prop.sentence.name
        #sname2prop.setdefault(sname2, set()).add(prop2.id)
        sname2prop.setdefault(sname, []).append(prop.id)
    return sname2prop


def _get_deduped_sentence_names_for_full_propset(propositions):
    """
    Given a L{models.Proposition} QuerySet, sorted as in L{_find_propositions},
    return the deduplicated list of Sentence.name for the rows.
    """
    sname4sort_dups = [prop.sentence.name for prop in propositions]
    sname4sort = ut.dedup_list_keep_order(sname4sort_dups)
    return sname4sort


def _solr_free_text_query(qstr):
    """
    Given query string qstr, returns ids for units matching the query
    Initially working with sentences as unit (may extend to documents.
    The goal is to be able to filter DB propositions by these sentence ids
    @note: Solr sentence.id field is DB Sentence.name field
    """
    solr_request = "{}/senenb12/browse?q={}&fl=id&wt=json&omitHeader=true&hl=off&rows=10000000".format(
        settings.SOLRURL[settings.SOLRMODE], quote(qstr))
    solr_response = urlopen(solr_request)
    solr_json = json.loads(solr_response.read())
    idlist = [doc['id'] for doc in solr_json['response']['docs']]
    # if VDBG:
    #     logger.warn("SOLR_RESP: {}".format(solr_json))
    #     logger.warn("###### ID_LIST: {}".format(idlist))
    return idlist


def _get_solr_documents(doc_ids):
    res = []
    #solr_request = "http://129.199.228.73:8983/solr/enb12/get?ids="
    # solr_request = "http://localhost:8983/solr/enb12/get?ids="
    solr_request = "{}/enb12/get?ids=".format(
        settings.SOLRURL[settings.SOLRMODE])
    solr_request += ','.join(doc_ids)
    solr_request += "&wt=json"
    solr_response = urlopen(solr_request)
    solr_json = json.loads(solr_response.read())
    for doc in solr_json['response']['docs']:
        #logger.warn(doc)
        res.append(dict(title=doc['title'], id=doc['id'], description=doc['description']))
    return json.dumps(res)


def _get_solr_sentences(sen_infos, request):
    """
    Get sentences from Solr sentence index.
    @param sen_infos: tuple (from _find_propositions) with:
      - 0: a list with the sentence names we need to get from Solr,
           starts with sentences for props for current page, then adds others
      - 1: the sentence names but in the order we want to sort them
           irrespective of pagination
      - 2: a dict of prop ids hashed by sen-name (can use for sen=>prop navig)
    @param request: the GET request that was sent to L{actors} or L{actions}
    """
    res = []
    #solr_request = "http://129.199.228.73:8983/solr/enb12/get?ids="
    # not using 'get' but could add the highlight component to the get
    # request handler too
    solr_request = "{}/senenb12/select?ids=".format(
        settings.SOLRURL[settings.SOLRMODE])
    solr_request += ','.join(sen_infos[0])
    #solr_request += ','.join(sen_infos[1])
    solr_request += "&wt=json&fl=id,description"
    # add highlighting for actor and predicate if there's any,
    # otherwise will do request without highlight
    rqd = request.GET
    if rqd["actor"] and rqd["actor"] != "":
        actor4hl = quote(rqd["actor"])
    else:
        actor4hl = ""
    if rqd["predicate"] and rqd["predicate"] != "":
        pred4hl = quote(rqd["predicate"])
    else:
        pred4hl = ""
    if "solrq" in rqd and rqd["solrq"]:
        # not removing '*' here cos then doesn't hl expansions
        #ftquery4hl = quote(rqd["solrq"].replace("*", ""))
        ftquery4hl = quote(rqd["solrq"])
    else:
        ftquery4hl = ""
    if not actor4hl and not pred4hl and not ftquery4hl:
        do_hl = False
    else:
        do_hl = True
        solr_request += "&hl=true&hl.fl=description&hl.q={}".format(actor4hl)
        solr_request += ",{}".format(pred4hl)
        solr_request += ",{}".format(ftquery4hl)
    solr_request = re.sub(r",{2,}", ",", solr_request)
    solr_request = solr_request.replace("q=,", "q=")
    # if there are two params in hl.q (i.e. sep is ','), doesn't hl with *
    if re.search(r"hl.q=[^&]+,", solr_request):
        solr_request = re.sub(r"(hl\.q)(.*)(?:\*|%2A)", r"\1\2", solr_request)
    print solr_request

    solr_response = urlopen(solr_request)
    solr_json = json.loads(solr_response.read())
    # get from the DB the data unavailable in Solr
    # (only sentence.name + sentence.text in Solr,
    # as sentence.id + sentence.description respectively)
    sids = [doc['id'] for doc in solr_json['response']['docs']]
    sobjs = Sentence.objects.filter(name__in=sids)
    sid2md = {}
    for sobj in sobjs:
        sid2md[sobj.name] = {"cop": sobj.document.cop,
                             "year": sobj.document.date.year}
    # prepare response
    # ---- with highlighting ----
    if do_hl:
        done_docs = set()
        for doc, infos in solr_json['highlighting'].items():
            if 'description' not in infos:
                continue
            solrsid = doc
            try:
                # remove Solr highlight inside links (breaks layout)
                cleanhtml = _normalize_solr_sentence(infos['description'][0])
                # the ids only used for debugging for now
                res.append(dict(sid=solrsid,
                                cop=sid2md[solrsid]["cop"],
                                year=sid2md[solrsid]["year"],
                                description=cleanhtml))
            # in case a sentence in Solr is not in DB
            except KeyError:
                #if VDBG:
                #    logger.warn("!! Sentence {} (hl) not found in DB".format(solrsid))
                continue
            done_docs.add(doc)
        # add missing (e.g. some anaphora cases trigger this, the prop is ok
        # but you only see the pronoun, not the actor)
        # (But some other anaphora cases are rendered as [Pronoun => Actor])
        for doc in solr_json['response']['docs']:
            if doc['id'] not in done_docs:
                try:
                    # the ids used for the sname2prop hash
                    res.append(dict(sid=doc['id'],
                                    cop=sid2md[doc['id']]["cop"],
                                    year=sid2md[doc['id']]["year"],
                                    description=doc['description']))
                    if VDBG:
                        logger.warn("Adding non-hl Doc: {}".format(repr(doc)))
                # in case a sentence in Solr is not in DB
                except KeyError:
                    #if VDBG:
                    #    logger.warn("!! Sentence {} (nohl) not found in DB".format(solrsid))
                    continue
    # ---- without ----
    else:
        for doc in solr_json['response']['docs']:
            solrsid = doc["id"]
            # the ids only used for debugging for now NO, NOW ALS FOR PROPS
            res.append(dict(sid=solrsid,
                            cop=sid2md[solrsid]["cop"],
                            year=sid2md[solrsid]["year"],
                            description=doc["description"]))
    print "NBR SOLR SENTS index: {}".format(solr_json["response"]["numFound"])
    print "NBR SOLR SENTS in DB: {}".format(len(res))
    # complement count info for ui. Here: Nbr of SENTS MATCHING THE FT QUERY
    request.session["sents_for_solrq"] = len(res)
    #if VDBG:
    #    logger.warn("SIDS in DB: {}".format([di["sid"] for di in res]))

    # Add proposition list for sentence
    for sen in res:
        try:
            sen.update({"propidstr": ".".join(
                [str(s) for s in sen_infos[2][sen["sid"]]])})
        except KeyError:
            sen.update({"propidstr": -1})
            if VDBG:
                logger.warn("Sen no prop info: {}".format(sen["sid"]))

    # SORT RESPONSE FOR FINAL OUTPUT
    # collect sentences without propositions
    sen_no_props = [se for se in res if se["sid"] not in sen_infos[2]]
    # add sentences for current page if have props
    res_new = sorted([se for se in res if se["sid"] in sen_infos[0]
                      and se not in sen_no_props],
                      key=lambda rs: sen_infos[0].index(rs["sid"]))
    # add sentenes for later pages if have props
    res_new.extend(sorted([se for se in res if se not in res_new
                           and se["sid"] in sen_infos[1]],
                           key=lambda rs: sen_infos[1].index(rs["sid"])))
    # add sentences with no props
    res_new.extend(sen_no_props)
    if VDBG:
       assert len(res_new) == len(res)
       # print "## LEN_RES_NEW {}, LEN_RES {}".format(len(res_new), len(res))

    # request.session["sents_for_solrq"] = len(res_new)
    return json.dumps(res_new)


def _hash_actor_variants():
    """Creates a hash from actor variants to actor labels"""
    var2label = {}
    for line in codecs.open(settings.EXT_DATA["actor_variants"], "r", "utf8"):
        sl = line.strip().split("\t")
        var2label[sl[0].lower()] = sl[1]
    return var2label


def _load_entity_filter():
    """Loads entity labels that need to not be displayed on UI entity pane"""
    return {el.strip(): 1 for el in codecs.open(
            settings.EXT_DATA['ui_entity_filter'], "r", "utf8")}


def _load_entity_subs():
    """Displays a different label for an entity based on settings"""
    return {el.split("\t")[0]: el.strip().split("\t")[1] for el in
            codecs.open(settings.EXT_DATA['ui_entity_subs'], "r", "utf8")
            if not el.startswith("#")}


def _load_kp_filter():
    """Loads entity labels that need to not be displayed on UI entity pane"""
    return {el.strip(): 1 for el in codecs.open(
            settings.EXT_DATA['ui_kp_filter'], "r", "utf8")}


def _create_proposition_filter(data, request):
    """
    Creates the filter to retrive propositions with, based on the data
    submitted by user in the propositions form.
    @note: stripping quotations so that queries can be found in DB and in
    aux data (_hash_actor_variants) if a user enter queries with quotations
    """
    preds = request.GET.getlist('predicate')
    if VDBG:
        print "\n\n>>>>>AD: {}".format(repr(data))
        print "\n\n>>>>>PR: {}".format(repr(preds))
    # store QueryDict in session
    request.session["lastqd"] = data

    # initial values ----------------------------------------------------------
    filter = {}
    attribute_filter = {"actor": "actorMention__actor__name",
                        "predicate": "predicateMention__predicate__name",
                        "point": "pointMention__point__name"}

    # free-text ---------------------------------------------------------------

    if "solrq" in data and data["solrq"]:
        solr_snames = _solr_free_text_query(data["solrq"])
        filter["sentence__name__in"] = solr_snames

    # actor -------------------------------------------------------------------
    #logger.warn("Start normalizing actors: {}".format(time.asctime(time.localtime())))
    norm_actors = _hash_actor_variants()

    if "actor" in data and data["actor"].strip('"').lower() in norm_actors:
        norm_actor = norm_actors[data["actor"].strip('"').lower()]
    # when calling /ui/ from agd templates there's no data
    elif "actor" in data:
        norm_actor = data["actor"].strip('"')
    else:
        norm_actor = ""
    filter[attribute_filter.get("actor")+"__icontains"] = norm_actor.strip('"')
    #logger.warn("Done: {}".format(time.asctime(time.localtime())))

    # predicate and point -----------------------------------------------------
    for attribute in ['predicate', 'point']:
        if attribute in data and data[attribute]:
            # make sensitive to predicate types
            #TODO: better way to deal with multiple values?
            if attribute == 'predicate':
                got_type = False
                if "__support__" in preds:
                    filter.setdefault("predicateMention__predicate__ptype__in",
                        []).append("support")
                    got_type = True
                if '__opposition__' in preds:
                    filter.setdefault("predicateMention__predicate__ptype__in",
                        []).append("oppose")
                    got_type = True
                if '__report__' in preds:
                    filter.setdefault("predicateMention__predicate__ptype__in",
                        []).append("report")
                    got_type = True
                # no predicate type, but surface string for predicate
                if not got_type:
                    filter[attribute_filter.get(attribute)+"__istartswith"] = \
                        data[attribute].strip('"')
            elif attribute == 'point':
                # originally doing __icontains
                #filter[attribute_filter.get(attribute)+"__icontains"] = data[attribute]
                # testing with __iregex now
                #   - looks like need MySQL regex syntax (as the backend)
                #   - https://stackoverflow.com/questions/19599841
                #   - https://dev.mysql.com/doc/refman/5.7/en/regexp.html
                normq = r"[[:<:]]{0}e?s?[[:>:]]".format(data[attribute])
                filter[attribute_filter.get(attribute)+"__iregex"] = normq

    # confidence range --------------------------------------------------------
    filter["conf__range"] = (float(data["minconf"]), float(data["maxconf"]))

    #dates --------------------------------------------------------------------
    filter["sentence__document__copyear__range"] = (float(data["dstart"]),
                                                    float(data["dend"]))

    # would have possibility to exploit issue type (Document.itype)from here
    #filter["sentence__document__itype"] = "daily"

    if VDBG:
        logger.warn("CREATED FILTER: {}".format(
            repr(filter)))
    return filter


def _normalize_solr_sentence(stxt):
    """
    Remove Solr highlighting inside a link, cos breaks layout.
    @note: 'climate' is the one case of hihglighting inside a link found so far
    """
    if 'climate' in stxt:
        cleanhtml = re.sub("http:([^ ]+ style[^ ]+ )", "[URL-removed] ", stxt)
    else:
        cleanhtml = stxt
    cleanhtml = re.sub(r"={10,}", "=" * 4, cleanhtml)
    cleanhtml = re.sub(r"http://", "", cleanhtml)
    cleanhtml = re.sub(r"http:&#x2F;&#x2F;", "", cleanhtml)
    return cleanhtml


def _query_is_empty_ignore_date_and_confidence(d):
    """
    See if the QueryDict in d is for the default values, but ignore
    the values for confidence range and date range
    """
    test = (not d["actor"] and not d["predicate"] and not d["point"] and
            not d["solrq"])
            #and int(d["dstart"]) == 1995 and int(d["dend"]) == 2015
            #and int(d["minconf"]) == 5 and int(d["maxconf"]) == 5)
    return bool(test)


def _query_is_empty(d):
    """
    See if the QueryDict in d is for the default values, considering
    even the values for confidence range and date range
    """
    test = ((not d["actor"] and not d["predicate"] and not d["point"] and
            not d["solrq"])
            and int(d["dstart"]) == 1995 and int(d["dend"]) == 2015
            and int(d["minconf"]) == 5 and int(d["maxconf"]) == 5)
    return bool(test)


def _destroy_session_filters(request):
    """If want to test without the infos stored in session"""
    for ke in ['sids_kp', 'ptmids_kp', 'sids_dbp', 'ptmids_dbp', 'lastfilter']:
        if ke in request.session:
            request.session[ke] = {}

