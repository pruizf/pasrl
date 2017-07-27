PASRL
=====

**Proposition Acquisition from SRL**: From our [LREC 2016 paper](http://www.lrec-conf.org/proceedings/lrec2016/pdf/636_Paper.pdf) (also [DH 2016](http://dh2016.adho.org/abstracts/81)). Also covered in my thesis [(Ruiz Fabo, 2017)](https://sites.google.com/site/thesisrf/thesis_prf_final.pdf). 

**Proposition Extraction** based on different relation sources, mainly [PropBank](https://propbank.github.io/) and [NomBank](http://nlp.cs.nyu.edu/meyers/NomBank.html) semantic roles.

A proposition is defined as a triple of shape _⟨actor, predicate, message⟩_, where the predicate is a reporting verb or noun. The actor emits a message via the predicate.

The SRL-based workflow described in the references above relies on the following materials (but see at the end of the list for alternative sources of relational information that we also tested).

- **[data](./data)**: domain data like actors and predicates
- **[db](./db)**: scripts to help format results in way required by django app that allows to navigate the extractions
     - getting keyphrase and entity offsets (and sentence) to match IXA Pipes tokenization
     - getting sentence offsets according to IXA Pipes sentence-splitting
     - etc.
- **[kp](./kp)**: keyphrase extraction (used to extract keyphrases from the propositions' messages)
- **[scripts](./scripts)**: scripts to start module or general data parsing and analyses
     - _temp_: temporary scripts
     - _vua_kn_temp_scripts_: testing KafNafParserPy from VUA
- **[srl](./srl)**: to exploit ixa-pipes dependencies and SRL layers
  The modules to run this workflow are `parse_srl.py` and `parse_srl_from_pickle.py`
     - `parse_srl.py`: reads NAF files to arrive at propositions, optionally stores pickle with results
     - `parse_srl_from_pickle.py`: reads propositions off a pickle, and outputs them in configurable formats (options are set in the module directly).
         - _exp_: evaluable format
         - _exp_free_: accepts incomplete propositions,
         - _exp_free_at_: accepts incomplete and adds actor types
- **[testsets](./testsets)**: different testsets created to test the srl-based extraction
   - _annotations_: golden sets (i.e. sentences annotated with propositions)
   - _dev_: devsets to work on different problems
   - _l6_: 100 raw (unannotated) sentences for lrec 2016 test-set
   - _test_eval_scripts_: cases to test evaluation script
- **[config.py](./config.py)**: config for several of the modules
- **[evalprops.py](./evalprops.py)**: proposition extraction evaluation with F1, and error analysis
- **[manage_domain_data.py](./manage_domain_data.py)**: parses the data in the data directory so that rest of modules can use it
- **[model.py](./model.py)**: basic objects for proposition extraction (`Proposition`, `Actor`, `Predicate` etc.)
- **[utils](./utils.py)**: general utility functions


Other sources of relational information that we also tested:

- **[madios](./madios)**: to work with the grammar induction algorithm [ADIOS](http://www.pnas.org/content/102/33/11629.full.pdf) by Z. Solan, using this [implementation](https://github.com/shaobohou/madios).
- **[openie4](./openie4)**: to work with [Open IE 4](https://knowitall.github.io/openie/), an _Open Information Extraction_ toolkit
