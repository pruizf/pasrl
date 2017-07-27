"""Parse Open IE 4 column results and import in a sql db"""

import inspect
import MySQLdb as sql
import os
import sys

here = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(
    os.path.join(here, os.pardir), os.pardir))


import config as cfg


def create_tables(con):
    with con:
        cur = con.cursor()

        # sentences ----------------------------------------------------
        print "Creating sentences"
        qy = """CREATE TABLE IF NOT EXISTS `sentences` (
                `sentId` varchar(200) NOT NULL,
                `sentNbr` INT(11) NOT NULL,
                `docId` varchar(200) NOT NULL,
                `text` varchar(10000) NOT NULL,
                 PRIMARY KEY (`sentId`)
                 ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        try:
            cur.execute(qy)
        except sql.IntegrityError:
            print "Error with table sentences"

        # mentions4rels ---------------------------------------------------
        # this will be replaced by refs to existing mentions from EL
        print "Creating mentions4rels"
        qy = """CREATE TABLE IF NOT EXISTS `mentions4rels` (
                `menId` varchar(250) NOT NULL,
                `menStr` varchar(200) NOT NULL,
                `eLabel` varchar(250) NOT NULL,
                `doc` varchar(100) NOT NULL,
                `start` int(11) NOT NULL,
                `end` int(11) NOT NULL,
                `sentId` int(11) NOT NULL COMMENT 'sentence number',
                PRIMARY KEY (`menID`),
                UNIQUE KEY `menId` (`menId`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        try:
            cur.execute(qy)
        except sql.IntegrityError:
            print "Error with table rel_mentions"

        # entities4rels ---------------------------------------------------
        # this will be replaced by refs to existing entities from EL
        print "Creating entities4rels"
        qy = """CREATE TABLE IF NOT EXISTS `entities4rels` (
                `eLabel` varchar(250) NOT NULL,
                PRIMARY KEY (`eLabel`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        try:
            cur.execute(qy)
        except sql.IntegrityError:
            print "Error with table entities4rels"

        # trigger_mentions ------------------------------------------
        print "Creating trigger_mentions"
        qy = """CREATE TABLE IF NOT EXISTS `trigger_mentions` (
                `trigStr` varchar(200) NOT NULL,
                `trigMenId` VARCHAR(200) NOT NULL,
                `start` int(11) NOT NULL,
                `end` int(11) NOT NULL,
                `trigId` varchar(100) NOT NULL,
                `confidence` float,
                `docId` varchar(200) NOT NULL,
                 PRIMARY KEY (`trigMenId`)
                 ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        try:
            cur.execute(qy)
        except sql.IntegrityError:
            print "Error with table trigger_mentions"

        # triggers ----------------------------------------------------
        print "Creating trigger"
        qy = """CREATE TABLE IF NOT EXISTS `triggers` (
                `trigLabel` varchar(200) NOT NULL,
                `confidence` float,
                 PRIMARY KEY (`trigLabel`)
                 ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        try:
            cur.execute(qy)
        except sql.IntegrityError:
            print "Error with table triggers"

        # relation instances ------------------------------------------
        print "Creating relation_instances"
        qy = """CREATE TABLE IF NOT EXISTS `relation_instances` (
                `m1` varchar(100) NOT NULL,
                `m2` varchar(200),
                `m3` varchar(200),
                `trigMenId` varchar(200) NOT NULL,
                `relId` varchar(200) NOT NULL,
                `relInstId` varchar(255) NOT NULL,
                `confidence` float NOT NULL,
                `docId` varchar(200) NOT NULL,
                `sentId` varchar(200),
                 PRIMARY KEY (`relInstId`)
                 ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        try:
            cur.execute(qy)
        except sql.IntegrityError:
            print "Error with table relation_instances"

        # relations ----------------------------------------------------
        print "Creating relations"
        qy = """CREATE TABLE IF NOT EXISTS `relations` (
                `e1` varchar(100) NOT NULL,
                `e2` varchar(200),
                `e3` varchar(200),
                `trigId` varchar(200) NOT NULL,
                `relId` varchar(255) NOT NULL,
                `confidence` float,
                 PRIMARY KEY (`relId`)
                 ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        try:
            cur.execute(qy)
        except sql.IntegrityError:
            print "Error with table relations"

        con.commit()


def main():
    con = sql.connect(cfg.host, cfg.user, cfg.pw, cfg.db)
    create_tables(con)


if __name__ == "__main__":
    main()