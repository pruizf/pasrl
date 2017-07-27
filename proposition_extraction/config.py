"""Config for IE tests"""

import logging
import os


# BASIC =======================================================================

DBG = False
is_eval = False
skip_dones = False
batchname = "enb_retest"
#comment = "test l6 retest for writeup"
comment = "testing ENB_postAR4"
run_corefs = True
todo = 10000000000000 # limit files to treat to this
# I/O -----------------------------------------------------
basedir = "/home/pablo/projects/ie/iewk"
datadir = os.path.join(basedir, "data")
testdir = os.path.join(basedir, "testsets")
golddir = os.path.join(testdir, "annotations")
pickle_results = False
# logging
loglevel = logging.DEBUG
logsdir = os.path.join(os.path.join(basedir, os.pardir), "logs")
logfn = os.path.join(logsdir, "{}.log".format(batchname))
norm_log_fn = os.path.join(
    logsdir, "{}_pronoun_norm_6oct_role_coref3.log".format(batchname))
metrics_fn = os.path.join(logsdir, "cumulog")
log_for_points_in_sentence = os.path.join(
    logsdir, "log_points_in_sentence_{}.log".format(batchname))


# COMPONENTS ==================================================================

# oie results -----------------------------------

oieres = os.path.join(basedir, os.pardir +
                      os.sep + "out" +
                      os.sep + "enb_openie4_out")

# srl results -----------------------------------

srlsuffix = ".par.coref.srl.naf"
srlres = os.path.join(basedir, os.pardir +
                      os.sep + "out" + os.sep + "srl" +
                      ## full corpus
                      #os.sep + "en_srl_out")
                      #os.sep + "enb_corefs_out/srl")
                      #os.sep + "enb_corefs_out_norm_pronouns") #sic
                      os.sep + "enb_corefs_out_norm_pronouns_DEBUG_5oct3")
                      #os.sep + "enb_out_mix_03302016")
                      #os.sep + "enb_four_missing_to_run_pasrl_on")
                      ## DEV sets
                      #os.sep + "enb_testset_srl/srl")
                      #os.sep + "enb_testset_srl_norm_pronouns") #sic
                      #os.sep + "enb_testset_multiple_preds/srl")
                      #os.sep + "enb_testset_multiple_preds_and_support_plus_oppose/srl")
                      #os.sep + "test_metrics/srl")
                      ## TEST sets
                      #os.sep + "l6/srl")
                      #os.sep + "blind/srl")
                      # OTHER
                      #os.sep + "ENB_postAR4_txt/srl")
                      # ADDING RESULTS IN MARCH 2016
                      #os.sep + "enb_to_add")

outdir = "/home/pablo/projects/ie/out/pasrl/{}".format(batchname)
respkl = os.path.join(outdir, u"{}.pkl".format(batchname))

# common to keyphrases and entity linking
sentence_offsets = os.path.join(datadir, "enb_sentence_offsets.pkl")

# keyphrase extraction --------------------------

#kp_batchname = "enb_test_kp_yatea_5"
kp_batchname = "enb_kps_for_docs_added_04152016"
yatea_results_dir_old = "/home/pablo/projects/ie/tools/Yatea/Yatea"
yatea_results_dir = "/home/pablo/projects/ie/tools/Yatea/Yatea/docs_to_add_kps_to_04152016"
yatea_results_list = os.path.join(datadir, "yatea_output_list.txt")
yatea_textdir = os.path.join(os.path.join(yatea_results_dir_old, os.pardir),
                             "enbmid")
kp_outdir = os.path.join(os.path.join(basedir, os.pardir), "out/kp")
yatea_analyzed = os.path.join(kp_outdir, u"{}.txt".format(kp_batchname))

# srl eval --------------------------------------

golden_fn = os.path.join(golddir, "enb_l6_golden.txt")
#golden_fn = "/home/pablo/projects/ie/wk/golden_versions/enb_l6_golden_before_removing_pronouns.txt"
#golden_fn = os.path.join(golddir, "test_eval_scripts_golden.txt")
golden_exported = os.path.join(golddir, "enb_l6_golden_exported.txt")
system_exported = os.path.join(outdir, "{}_system_exported_retest.txt".format(batchname))


# DOMAIN DATA =================================================================

actors = os.path.join(datadir, "actors.xml")
verb_preds = os.path.join(datadir, "preds_verbal.xml")
noun_preds = os.path.join(datadir, "preds_nominal.xml")
# names to display predicate types
spref, opref, rpref = "support", "oppose", "report"
allowed_pred_pos = ("N", "V", None)  # allowed pos for predicates

# for predicate inversion in negated propositions
inversions = {spref: opref, opref: spref, rpref: rpref}
negations = {"not", "cannot", "can't", "won't", "couldn't", "wouldn't",
             "withdraw", "lack", "won'", "couldn'", "wouldn'"}
coref_blockers = os.path.join(datadir, "coref_blockers.txt")


# Configuration for extracted propositions ====================================

pt_tolerance = 3  # see L{utils.py}. Tolerance of 2 * pt_tolerance characters for
                  # point start and end when looking for a kw or entity in a point


# DB ==========================================================================

# Old DB for OpenIE. For IXA SRL workflow, DB is in a Django app
host = "localhost"
user = "SOME USER NAME"
pw = "SOME PASSWORD"
db = "oie4_enb"


# Logging details =============================================================

VERBOSE = False
tmf = "%H:%M:%S"
message_contains_predicate = "message contains predicate"
