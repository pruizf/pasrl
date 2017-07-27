"""
Output propositions whose message (aka 'negotiation point' or 'point') is empty.
Output descriptive stats: how many sentences with a canonical actor? how many with
an empty message? Etc.
"""

__author__ = 'Pablo Ruiz'
__date__ = '08/02/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs
from lxml import etree
import time

# I/O ==
# sentence-ids for sentences containing non-canonical propositions only
myids = "/home/pablo/projects/ie/wk/srl/sentence_ids_in_incomplete_propositions_only.txt"
# file with all propositions
allprops = "/home/pablo/projects/ie/out/pasrl/test_pickle_out_30_jan_accept_incomplete_added_sents_w_dones.txt"
# outfile for selected ones
outprops = "/home/pablo/projects/ie/wk/srl/propositions_with_empty_message.txt"

# Data ==
actors = "/home/pablo/projects/ie/iewk/data/actors.xml"


def hash_ids(idf):
    with codecs.open(idf, "r", "utf8") as infd:
        return [ll.strip() for ll in infd]


def get_actors():
    di = {}
    tree = etree.parse(actors)
    acnodes = [c for c in tree.xpath("//country | //other | //observer")]
    for nd in acnodes:
        di.setdefault(nd.attrib["dbpedia"], 1)
    return di


def check_proposition(inf, actrs):
    """
    Go over results sentence by sentence and, if the sentence has any
    empty message, keep it along with the sentence.
    """
    sel = []
    done_sents = 0
    # sentence and proposition type counts
    # analyzed
    sents_with_some_output = 0
    # analyzed and with message
    props_with_some_message = 0
    # emtpy messages
    sents_with_empty_messages = 0
    nbr_of_props_with_empty_messages = 0
    # canonical actors
    sents_with_canonical_actors = 0
    props_with_canonical_actors = 0
    # other actors
    sents_with_other_actors = 0
    props_with_other_actors = 0
    with codecs.open(inf, "r", "utf8") as ifd:
        line = ifd.readline()
        while line:
            sl = line.strip("\n").split("\t")
            # new sentence
            if len(sl) > 0 and sl[0] != "" and sl[1] == "Y":
                done_sents += 1
                # why this flag? guess it is cos, if a sent has > 1 props
                # with canonical actors, you still want to count it ONCE only
                counted_sentence_for_actors = False
                # collect the props
                temp = []
                # strip the newline only otherwise can't split on tabs!
                line2 = ifd.readline().strip("\n")
                while line2:
                    sl2 = line2.split("\t")
                    # actor type
                    if not counted_sentence_for_actors:
                        if sl2[0] in actrs:
                            sents_with_canonical_actors += 1
                        else:
                            sents_with_other_actors += 1
                        counted_sentence_for_actors = True
                    # message status
                    if len(sl2) > 0 and sl[0] != "":
                        if sl2[-1] == "":
                            temp.append(line2)
                        else:
                            props_with_some_message += 1
                        if sl2[0] in actrs:
                            props_with_canonical_actors += 1
                        else:
                            props_with_other_actors += 1
                    else:
                        break
                    line2 = ifd.readline().strip("\n")
                if len(temp) > 0:
                    sel.append([line.strip("\n")])
                    sel[-1].extend(temp)
                    sents_with_empty_messages += 1
                    nbr_of_props_with_empty_messages += len(temp)
                else:
                    sents_with_some_output += 1
            if done_sents % 5000 == 0:
                print "Done {} sentences {}".format(
                    done_sents, time.strftime("%H:%M:%S", time.localtime()))
            line = ifd.readline()
    # note (03072016): variable names are not very telling ...
    # looking at my last outputs:
    #   - sents_with_some_output: looks like sents without empty messages,
    #     that's why sents_with_some_output + sents_with_emtpy_message
    #     equals done_sents, and that's why the count was printed out with label
    #     'props w some message'; the *variable name* sents_with_some_output is
    #     a bit of a misnomer: done_sents is the sents with output, and
    #     sents_with_some_output is the sents without an empty message.
    #   - done_sents is ALL the sents that the system
    #     had some output for, see L{add_empty_sentences_to_pasrl_output.py},
    #     any sentence tagged 'Y' has some output, and this script here further
    #     describes those outputs: what types of actors/empty messages or not)
    # some of the props had a message
    print "= STATS ="
    print "total sents w output: {}".format(done_sents)
    print "sents w some message: {}".format(sents_with_some_output)
    print "props w some message: {}".format(props_with_some_message)
    print "sents w empty messages: {}".format(sents_with_empty_messages)
    print "props w empty messages: {}".format(nbr_of_props_with_empty_messages)
    print "sents w canonical actors: {}".format(sents_with_canonical_actors)
    print "props w canonical actors: {}".format(props_with_canonical_actors)
    print "sents w other actors: {}".format(sents_with_other_actors)
    print "props w other actors: {}".format(props_with_other_actors)
    assert sents_with_some_output + sents_with_empty_messages == done_sents
    assert sents_with_canonical_actors + sents_with_other_actors == done_sents
    return sel


def write_out(snps, ofn):
    with codecs.open(ofn, "w", "utf8") as ofd:
        for snp in snps:
            ofd.write(u"{}\n\n".format("\n".join(snp)))


def main():
    global myactors
    ids2check = hash_ids(myids)
    myactors = get_actors()
    selprops = check_proposition(allprops, myactors)
    write_out(selprops, outprops)


if __name__ == "__main__":
    main()