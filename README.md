PASRL
=====

Proposition Acquisition with SRL


Why do this?
------------

Co-occurrence-based methods have yielded very useful results for analyzing social science corpora. However, for a negotiation corpus, it is relevant to know not only what concepts or actors co-occur within a given text window, but also, where those actors stand with respect to each other and regarding those concepts. For instance:

- _Who's opposing whom?_
- _Who's siding with whom?_
- _About what issues?_

A Natural Language Processing Pipeline (NLP) was applied to climate negotiation reports, from the [Earth Negotiations Bulletin](http://enb.iisd.org/enb/vol12/), which covers climate summits where treaties like the Kyoto Protocol or the Paris Agreement got negotiated. 

Actors, their concerns, and their relation to other actors was identified based on the outputs of the NLP pipeline.


System Architecture
-------------------
![System Workflow Diagram](./.img/ch7_system_workflow.png)

The app consists in two projects. A short description follows; see each project's directory for details:
- [proposition_extraction](./proposition_extraction)
    - Workflow to extract triples (**propositions**) for the speakers, their messages, and the predicate (reporting expression) relating both. An NLP pipeline, based on [IXA Pipes](http://ixa2.si.ehu.es/ixa-pipes/), provides Semantic Role Labeling, dependency parsing and coreference chains. Based on the NLP output, propositions are identified with rules.
    - The proposition's messages are enriched with **NLP-based metadata**: keyphrases, generic entities from DBpedia, and domain-specific entities from a climate thesaurus.
    - Basic **inference** is performed to find actors who agree or disagree with other actors, and over which issues, based on the propositions and their NLP-based metadata.
    - The propositions and metadata are made navigable in the [corpus\_navigation](https://github.com/pruizf/pasrl/tree/master/corpus_navigation) project.
- [corpus_navigation](./corpus_navigation)
    - This project is a [Django app](https://www.djangoproject.com/) to navigate the Earth Negotiations Bulletin corpus, enriched with propositions, i.e. triples of shape actor, predicate, message triples, and metadata extracted from the messages. All triples and metadata are made navigable.
    - Besides a **structured search** based on the proposition extraction workflow, **full-text search** with Solr is provided.


Publications
------------

- Ruiz Fabo, Pablo, Clément Plancq, and Thierry Poibeau. (2016). [More than Word Cooccurrence : Exploring Support and Opposition in International Climate Negotiations with Semantic Parsing](http://www.lrec-conf.org/proceedings/lrec2016/pdf/636_Paper.pdf). In _Proceedings of LREC, Tenth International Conference on Language Resources and Evaluation_, pp. 1902-1907. Portorož, Slovenia.

- Ruiz Fabo, Pablo. (2017). [Concept-based and Relation-based Corpus Navigation : Applications of Natural Language Processing in Digital Humanities](https://sites.google.com/site/thesisrf/thesis_prf_final.pdf). PhD Dissertation. Ecole Normale Supérieure, PSL Research University, Paris. 

- Ruiz Fabo, Pablo, Clément Plancq, and Thierry Poibeau. (2016). [Climate Negotiation Analysis](http://dh2016.adho.org/abstracts/81). In _Digital Humanities Conference (DH 2016)_. Kraków, Poland.

