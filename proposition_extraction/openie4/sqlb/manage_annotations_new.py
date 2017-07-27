import codecs
import inspect
import MySQLdb as sql
import os
import re
import sys


here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(
    os.path.join(here, os.pardir), os.pardir))


import config as cfg
import utils as ut


def parse_file(fn):
    """Read open ie column-format output, extracting infos we store"""
    arg_re = re.compile(ur"""
                         ^[A-Z][^A-Z]+Argument\(
                         ([^,)]+),List\(
                         \[([0-9]+),[ ]([0-9]+)\)\)
                         \)+$""", re.VERBOSE)
    rel_re = re.compile(ur"""
                          ^Relation\(
                          ([^,)]+),List\(
                          \[([0-9]+),[ ]([0-9]+)\)\)
                          \)+$""", re.VERBOSE)
    extractions = {}
    with codecs.open(fn, "r", "utf8") as fi:
        todo = 10000000000
        done = 0
        line = fi.readline()
        lnbr = 0
        while line:
            # skip empty cols
            sl = [x for x in line.split("\t") if x]
            args = {}
            rel = {}
            argnbr = 1
            conf = float(sl[0])
            sent = sl[-1]
            for col in sl[1:-1]:
                is_arg = re.match(arg_re, col)
                if is_arg:
                    args[argnbr] = {"arg": is_arg.group(1),
                                    "start": int(is_arg.group(2)),
                                    "end": int(is_arg.group(3))}
                    argnbr += 1
                else:
                    is_rel = re.match(rel_re, col)
                    if is_rel:
                        rel[is_rel.group(1)] = {"start": int(is_rel.group(2)),
                                                "end": int(is_rel.group(3))}
            if cfg.DBG:
                print "ARGS", args, conf, sent.strip()
                print "REL", rel, "\n"
            extractions[lnbr] = (args, rel, conf, sent)
            lnbr += 1
            done += 1
            if done == todo:
                sys.exit()
            line = fi.readline()
    return extractions


def insert_sentence(xt, fn, con):
    """
    Insert sentence info
    @param xt: info extracted from openie output
    @param fn: used as document id
    @param con: sql connection
    """
    # verify max sent nbr
    snqy = "SELECT MAX(`sentNbr`) as maxnbr from `sentences`"
    cur = con.cursor(sql.cursors.DictCursor)
    cur.execute(snqy)
    # if table empty set to 1
    try:
        sn = cur.fetchone()["maxnbr"] + 1
    except TypeError:
        sn = 1
    sent_id = "{}_{}".format(fn, sn)
    # stackoverflow.com/questions/3164505
    qy = u"INSERT INTO `sentences` (`sentId`, `sentNbr`, `docId`, `text`) " + \
         u"SELECT * FROM (SELECT '{}', '{}', '{}', '{}') AS tmp ".format(
             sent_id, sn, fn, ut.sqlesc(xt[-1])) + \
         u"WHERE NOT EXISTS (SELECT `text` FROM `sentences` " + \
         u"WHERE `text` LIKE '{}') LIMIT 1".format(ut.sqlesc(xt[-1]))
    cur.execute(qy.encode("utf8"))


def insert_mentions4rels_and_entities4rels(xt, fn, con):
    """
    Insert the arguments that take part in relations,
    as mention and as entity (no normalization for now)
    @param xt: info extracted from openie output
    @param fn: used as document id
    @param con: sql connection
    """
    cur = con.cursor()
    argus = xt[0]
    for argnbr, arg in argus.items():
        qymen = u"INSERT IGNORE INTO `mentions4rels` (`menId`, " \
                u"`menStr`, `eLabel`, " \
                u"`doc`, `start`, `end`) " \
                u"VALUES ('{}~{}~{}~{}', '{}', '{}', '{}', '{}', '{}') ".format(
                    fn, ut.sqlesc(arg["arg"]), arg["start"], arg["end"],
                    ut.sqlesc(arg["arg"]), ut.sqlesc(arg["arg"]),
                    fn, arg["start"], arg["end"])
        qyent = u"INSERT IGNORE INTO `entities4rels` (`eLabel`) " \
                u"VALUES ('{}')".format(ut.sqlesc(arg["arg"]))
        cur.execute(qymen.encode("utf8"))
        cur.execute(qyent.encode("utf8"))


def insert_trigger_mentions_and_triggers(xt, fn, con):
    """
    Insert the arguments that take part in relations,
    as mention and as entity (no normalization for now)
    @param xt: info extracted from openie output
    @param fn: used as document id
    @param con: sql connection
    """
    cur = con.cursor()
    trigs = xt[1]
    for trig in trigs:
        qymen = u"INSERT IGNORE INTO `trigger_mentions` (`trigMenId`, " \
                u"`trigStr`, `docId`, `start`, `end`) " \
                u"VALUES ('{}~{}~{}~{}', '{}', '{}', '{}' ,'{}')".format(
                    fn, ut.sqlesc(trig), trigs[trig]["start"], trigs[trig]["end"],
                    ut.sqlesc(trig), fn, trigs[trig]["start"], trigs[trig]["end"])
        qytrg = u"INSERT IGNORE INTO `triggers` (`trigLabel`) " \
                u"VALUES ('{}')".format(ut.sqlesc(trig))
        cur.execute(qymen.encode("utf8"))
        cur.execute(qytrg.encode("utf8"))


def insert_relation_instances_and_relations(xt, fn, con):
    """
    Insert relation instances and relations using informative keys
    @param xt: info extracted from openie output
    @param fn: used as document id
    @param con: sql connection
    @note:
      - men key: fn~menStr~start~end
      - ent key: eLabel (the mention string, no normalization now)
      - trig mention key: fn~trigMenStr~start~end
      - trig key: trigLabel (the mention string, no normalization now)
      - rel instance key: fn###menStr~start~end###menStr~start~end###trigMenStr~start~end
      - rel key: eLabel###eLabel(###eLabel)###trigLabel
    """
    cur = con.cursor()
    argus = xt[0]
    trig = xt[1]
    conf = xt[-2]
    if not argus or not trig:
        return
    assert len(argus) <= 3
    # ALL CASES ===============================================================
    trig_men_id = u"{}~{}~{}~{}".format(fn, ut.sqlesc(trig.keys()[0]),
                                       int(trig.values()[0]["start"]),
                                       int(trig.values()[0]["end"]))
    trig_id = u"{}".format(ut.sqlesc(trig.keys()[0]))
    # men1_id = u"{}~{}~{}~{}".format(fn, ut.sqlesc(argus[1]["arg"]),
    #                                 int(argus[1]["start"]),
    #                                 int(argus[1]["end"]))
    men1_id = u"{}".format(ut.sqlesc(argus[1]["arg"]))
    # ONE ARG ===============================================================
    if len(argus) == 1:
        rel_inst_id = u"{}###{}~{}~{}###{}~{}~{}".format(fn,
            ut.sqlesc(argus[1]["arg"]),
                      int(argus[1]["start"]), int(argus[1]["end"]),
            ut.sqlesc(trig.keys()[0]),
                      trig.values()[0]["start"], trig.values()[0]["end"]
            )
        rel_id = u"{}###{}".format(ut.sqlesc(argus[1]["arg"]),
                                   ut.sqlesc(trig.keys()[0]))
        qyins = u"INSERT IGNORE INTO `relation_instances` " \
                u"(`relInstId`, `relId`, `m1`, `trigMenId`, " \
                u"`confidence`, `docId`) " \
                u"VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(
                    rel_inst_id, rel_id, men1_id, trig_men_id, conf, fn)
        qyrel = u"INSERT IGNORE INTO `relations` " \
                u"(`relId`, `e1`, `trigId`, `confidence`) " \
                u"VALUES ('{}', '{}', '{}', '{}')".format(
                    rel_id, men1_id, trig_id, conf)
    # TWO ARG ===============================================================
    elif len(argus) == 2:
        # men2_id = u"{}~{}~{}~{}".format(fn, ut.sqlesc(argus[2]["arg"]),
        #                                 int(argus[2]["start"]),
        #                                 int(argus[2]["end"]))
        men2_id = u"{}".format(ut.sqlesc(argus[2]["arg"]))
        rel_inst_id = u"{}###{}~{}~{}###{}~{}~{}###{}~{}~{}".format(fn,
            ut.sqlesc(argus[1]["arg"]),
                      int(argus[1]["start"]), int(argus[1]["end"]),
            ut.sqlesc(argus[2]["arg"]),
                      int(argus[2]["start"]), int(argus[2]["end"]),
            ut.sqlesc(trig.keys()[0]),
                      trig.values()[0]["start"], trig.values()[0]["end"]
            )
        rel_id = u"{}###{}###{}".format(ut.sqlesc(argus[1]["arg"]),
                                        ut.sqlesc(argus[2]["arg"]),
                                        ut.sqlesc(trig.keys()[0]))
        qyins = u"INSERT IGNORE INTO `relation_instances` " \
                u"(`relInstId`, `relId`, `m1`, `m2`, `trigMenId`, " \
                u"`confidence`, `docId`) " \
                u"VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                    rel_inst_id, rel_id, men1_id, men2_id, trig_men_id,
                    conf, fn)
        qyrel = u"INSERT IGNORE INTO `relations` " \
                u"(`relId`, `e1`, `e2`, `trigId`, `confidence`) " \
                u"VALUES ('{}', '{}', '{}', '{}', '{}')".format(
                    rel_id, men1_id, men2_id, trig_id, conf)
    # THREE ARG ============================================================
    else:
        # men2_id = u"{}~{}~{}~{}".format(fn, ut.sqlesc(argus[2]["arg"]),
        #                                 int(argus[2]["start"]),
        #                                 int(argus[2]["end"]))
        # men3_id = u"{}~{}~{}~{}".format(fn, ut.sqlesc(argus[3]["arg"]),
        #                                 int(argus[3]["start"]),
        #                                 int(argus[3]["end"]))
        men2_id = u"{}".format(ut.sqlesc(argus[2]["arg"]))
        men3_id = u"{}".format(ut.sqlesc(argus[3]["arg"]))
        rel_inst_id = u"{}###{}~{}~{}###{}~{}~{}###{}~{}~{}###{}~{}~{}".format(fn,
            ut.sqlesc(argus[1]["arg"]),
                      int(argus[1]["start"]), int(argus[1]["end"]),
            ut.sqlesc(argus[2]["arg"]),
                      int(argus[2]["start"]), int(argus[2]["end"]),
            ut.sqlesc(argus[3]["arg"]),
                      int(argus[3]["start"]), int(argus[3]["end"]),
            ut.sqlesc(trig.keys()[0]),
                      trig.values()[0]["start"], trig.values()[0]["end"]
            )
        rel_id = u"{}###{}###{}###{}".format(ut.sqlesc(argus[1]["arg"]),
                                             ut.sqlesc(argus[2]["arg"]),
                                             ut.sqlesc(argus[3]["arg"]),
                                             ut.sqlesc(trig.keys()[0]))
        qyins = u"INSERT IGNORE INTO `relation_instances` " \
                u"(`relInstId`, `relId`, `m1`, `m2`, `m3`, `trigMenId`, " \
                u"`confidence`, `docId`) " \
                u"VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                    rel_inst_id, rel_id, men1_id, men2_id, men3_id, trig_men_id,
                    conf, fn)
        qyrel = u"INSERT IGNORE INTO `relations` " \
                u"(`relId`, `e1`, `e2`, `e3`, `trigId`, `confidence`) " \
                u"VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(
                    rel_id, men1_id, men2_id, men3_id, trig_id, conf)

    cur.execute(qyins.encode("utf8"))
    cur.execute(qyrel)


def insert_extractions(fex, fn, con):
    """
    Insert infos from open ie output into db
    @param fex: open ie extractions for one file
    @param fn: filename, used as doc id
    @param con: sql connection
    """
    for ll, ex in sorted(fex.items()):
        insert_sentence(ex, fn, con)
        insert_mentions4rels_and_entities4rels(ex, fn, con)
        insert_trigger_mentions_and_triggers(ex, fn, con)
        insert_relation_instances_and_relations(ex, fn, con)

def parse_dir(dr, con):
    """Apply insertion function to a directory"""
    todo = 10000000000000000000
    done = 0
    for fn in sorted(os.listdir(dr)):
        print "{} {} {}".format("="*10, fn, "="*10)
        ffn = os.path.join(dr, fn)
        exts = parse_file(ffn)
        with con:
            insert_extractions(exts, fn, con)
            con.commit()
        done += 1
        if done == todo:
            sys.exit()


def main():
    #I/O
    try:
        indir = sys.argv[1]
    except IndexError:
        #indir = r"/home/pablo/projects/ie/corpora/aoc_out"
        indir = r"/home/pablo/projects/ie/out/enb_openie4_out"
    con = sql.connect(cfg.host, cfg.user, cfg.pw, cfg.db)
    parse_dir(indir, con)


if __name__ == "__main__":
    main()