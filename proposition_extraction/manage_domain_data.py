"""To treat domain-related infos like country list etc."""

__author__ = 'Pablo Ruiz'
__date__ = '12/09/15'


import codecs
import inspect
from lxml import etree
import os
import sys


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(here)


import config as cfg


def parse_actors_simple(fn=cfg.actors):
    """Get actors from location specified in config
    (countries or whatever applies to domain)"""
    tree = etree.parse(fn)
    ai = [c.text.lower() for c in tree.xpath("//country[@type='AI']")]
    nai = [c.text.lower() for c in tree.xpath("//country[@type='NAI']")]
    return {"AI": ai, "NAI": nai}


def parse_actors(fn=cfg.actors):
    """Get actors from location specified in config
    (countries or whatever applies to domain)"""
    tree = etree.parse(fn)
    ai = {}
    nai = {}
    other = {}
    observers = {}
    ai_nodes = [c for c in tree.xpath("//country[@type='AI']")]
    nai_nodes = [c for c in tree.xpath("//country[@type='NAI']")]
    other_nodes = [c for c in tree.xpath("//other")]
    observer_nodes = [c for c in tree.xpath("//observer")]
    for node in ai_nodes:
        ai.setdefault(node.attrib["dbpedia"], []).extend((
            node.text.lower(),
            node.attrib["dbpedia"].replace("_", " ").lower()))
    for node in nai_nodes:
        nai.setdefault(node.attrib["dbpedia"], []).extend((
            node.text.lower(),
            node.attrib["dbpedia"].replace("_", " ").lower()))
    for node in other_nodes:
        other.setdefault(node.attrib["dbpedia"], []).extend((
            node.text.lower(),
            node.attrib["dbpedia"].replace("_", " ").lower()))
    for node in observer_nodes:
        observers.setdefault(node.attrib["dbpedia"], []).extend((
            node.text.lower(),
            node.attrib["dbpedia"].replace("_", " ").lower()))
    return {"AI": ai, "NAI": nai, "OTHER": other, "OBSERVERS": observers}


def return_set_of_actor_labels():
    """
    Return only the DBpedia labels for actors, as a set, LOWERCASED
    """
    di = set()
    tree = etree.parse(cfg.actors)
    acnodes = [c for c in tree.xpath("//country | //other | //observer")]
    for nd in acnodes:
        di.add(nd.attrib["dbpedia"].lower())
        try:
            di.add(nd.attrib["display"].lower())
        except KeyError:
            continue
        di.add(nd.xpath("./text()")[0])
    return di


def return_set_of_generic_labels():
    """
    Return labels for generic roles like "delegates", "participants" ...
    """
    tree = etree.parse(cfg.actors)
    gens = set([c[0] for c in tree.xpath("//generic/text()")])
    return gens


def parse_verbal_predicates(fn=cfg.verb_preds):
    """
    Get predicates from for the domain location specified in config
    In these tests, we're modeling support/opposition/general statement
    """
    tree = etree.parse(fn)
    sup = [c.text.lower() for c in tree.xpath("//pred[@rtype='sup']")]
    opp = [c.text.lower() for c in tree.xpath("//pred[@rtype='opp']")]
    rep = [c.text.lower() for c in tree.xpath("//pred[@rtype='rep']")]
    return {"sup": sup, "opp": opp, "rep": rep}


def parse_nominal_predicates(fn=cfg.noun_preds):
    """
    Get predicates from for the domain location specified in config
    In these tests, we're modeling support/opposition/general statement
    """
    tree = etree.parse(fn)
    sup = [c.text.lower() for c in tree.xpath(
        "//pred[@rtype='sup' and @active='1']")]
    opp = [c.text.lower() for c in tree.xpath(
        "//pred[@rtype='opp' and @active='1']")]
    rep = [c.text.lower() for c in tree.xpath(
        "//pred[@rtype='rep' and @active='1']")]
    return {"sup": sup, "opp": opp, "rep": rep}


def parse_coref_blockers(fn=cfg.coref_blockers):
    """Return dict with sequences containing an expletive 'it'"""
    out = {}
    with codecs.open(fn, "r", "utf8") as blockers:
        for bl in blockers:
            if not bl.startswith("#"):
                out[bl.strip()] = 1
    return out


if __name__ == "__main__":
    mya = parse_actors()
    myp = parse_verbal_predicates()
    mynomp = parse_nominal_predicates()