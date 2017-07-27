#!/usr/bin/env bash

# creates django webuibo fixture based on export of iewk workflow results

propfile="$1"
add_a_types="$2" # [yes|no]


if [ "$#" -ne 2 ]; then
    echo "Usage: $0 propositions_file add_actor_types[yes|no]"
    exit
fi

inifixture=../ext_data/json/$(basename "$propfile").json
tempfixture=${inifixture/%.json/_meta7.json}
finalfixture=${tempfixture/%_meta7.json/_final.json}


# script to create initial fixture
if [ "$2" = "yes" ] ; then
    ini_fixture_creator="txt2json_with_ptype_with_atype.pl"
  elif [ "$2" = "no" ] ; then
    ini_fixture_creator="txt2json_with_ptype.pl"
fi

# script to add keyphrases, entities and doc metadata
temp_fixture_creator="complement_txt2json.py"
# script to add agree-disagree table data
final_fixture_creator="create_agree_disagree_data.py"

echo "**Raw data: $propfile**"

# initial fixture
echo -e "\n** INITIAL FIXTURE: $inifixture **\n"
perl "$ini_fixture_creator" "$propfile" > "$inifixture"
if [ ! -f "$inifixture" ] ||  [ ! -s "$inifixture" ]; then
    echo -e "\nError running $ini_fixture_creator\n"
    exit
  else echo -e "\n**Created $inifixture**\n"
fi

# temp fixture
echo -e "\n** TEMPORARY FIXTURE: $tempfixture **\n"
python "$temp_fixture_creator" "$inifixture"
if [ ! -f "$tempfixture" ] || [ ! -s "$tempfixture" ]; then
    echo -e "\nError running $temp_fixture_creator\n"
    exit
  else echo -e "\n**Created $tempfixture**\n"
fi

# final fixture
echo -e "\n** FINAL FIXTURE: $finalfixture **\n"
#  result reader is different whether actor types are considered or not
if [ "$add_a_types" == "yes" ]; then
    python "$final_fixture_creator" "$tempfixture" "$finalfixture" "types"
  else
    python "$final_fixture_creator" "$tempfixture" "$finalfixture" "notypes"
fi

if [ ! -f "$finalfixture" ] || [ ! -s "$finalfixture" ]; then
    echo -e "\nError running $final_fixture_creator\n"
  else echo -e "**\nCreated $finalfixture**\n"
fi
