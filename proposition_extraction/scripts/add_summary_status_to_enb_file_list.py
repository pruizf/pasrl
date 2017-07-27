"""Add to the file metadata list whether the issue is a daily or a summary"""

__author__ = 'Pablo Ruiz'
__date__ = '04/04/16'
__email__ = 'pabloruizfabo@gmail.com'


import codecs

#TODO: the summarylist missed many of the summaries

summarylist = "/home/pablo/projects/ie/wk/issue_filenames_for_summaries.txt"
metadata = "/home/pablo/projects/ie/wk/ui_wireframe/uibo/webuibo/ext_data/txt/document_metadata.txt"
new_metadata = "/home/pablo/projects/ie/wk/cop_metadata_with_summary_status_2.txt"

summaries = set([ll.strip() for ll in codecs.open(summarylist, "r", "utf8")
                 if ll.strip() and not ll.startswith("#")])


with codecs.open(metadata, "r", "utf8") as infd,\
     codecs.open(new_metadata, "w", "utf8") as oufd:
    line = infd.readline()
    while line:
        sl = line.strip().split("\t")
        if sl[0] in summaries:
            nl = sl + ["summary"]
        else:
            nl = sl + ["daily"]
        oufd.write("\t".join(nl))
        oufd.write("\n")
        line = infd.readline()

print "Summaries: ", summarylist
print "In: ", metadata
print "Out: ", new_metadata
