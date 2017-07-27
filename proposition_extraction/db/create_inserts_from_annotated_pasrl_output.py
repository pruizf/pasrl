"""
Based on the pasrl output as post-proccessed with L{scripts/add_empty_sentences_to_pasrl_output.py},
get sentences that had no output, and, if their doc is in DB, create an insert for it.
"""

__author__ = 'Pablo Ruiz'
__date__ = '18/04/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs


export = "/home/pablo/projects/ie/out/pasrl/test_pickle_out_30_jan_accept_incomplete_added_sents_w_dones.txt"
dbdocids = "/home/pablo/projects/ie/wk/db/docids_in_db_01302016.txt"
outfi = "/home/pablo/projects/ie/wk/db/db_queries_for_sentences_wo_props.txt"


def sqlesc(st):
    """Avoid sql errors"""
    st = st.replace("'", r"\'")
    st = st.replace('"', r'\"')
    return st


def get_ids(idf):
    """Return set of ids in db"""
    print "Getting ids"
    name2id ={}
    with codecs.open(idf, "r", "utf8") as dids:
        for ll in dids.readlines():
            sl = ll.strip().split("\t")
            name2id[sl[1]] = sl[0]
    return name2id


def hash_export(ef, docname2id):
    """Read export file to find out sentences not in db and their doc id"""
    print "Hashing export file"
    out = []
    with codecs.open(ef, "r", "utf8") as ifd:
        dones = 0
        line = ifd.readline()
        while line:
            if "\tN\t" in line:
                sl = line.strip().split("\t")
                sname = sl[0]
                txt = sl[-1]
                docname = sl[0].split("-")[0]
                assert docname
                if docname in docname2id:
                    out.append(dict(sname=sname, txt=sqlesc(txt),
                                    docid=docname2id[docname]))
            line = ifd.readline()
            if dones and not dones % 5000:
                print "Done {} lines".format(dones)
            dones += 1
    return out


def write_out(sents, outfn):
    """Write out the insert queries"""
    print "Writing out"
    with codecs.open(outfn, "w", "utf8") as outfd:
        for sen in sents:
            q = u"insert into ui_sentence (name, text, document_id)" + \
                u" values ('{}', '{}', '{}');\n".format(
                    sen["sname"], sen["txt"], sen["docid"])
            outfd.write(q)


def main(docids, exportfn, outfn):
    """
    Find doc ids in db, find sentences not in db.
    Create insert queries for the sentences not in db
    """
    dids = get_ids(docids)
    sentences_wo_props = hash_export(exportfn, dids)
    write_out(sentences_wo_props, outfn)


if __name__ == "__main__":
    main(dbdocids, export, outfi)