#!/bin/bash
#
# Convert wikipedia's MySQL dump to csv file on preserving only vertices' and edges' information

file=$1
sed -n '/INSERT INTO `.*` VALUES /p' $file \
    | sed 's/INSERT INTO `.*` VALUES //' \
    | sed 's/),(/)\n(/g' \
    | sed 's/^(//;s/)$//;' \
    | sed -r "s/\\\'/\a/g"\
    | awk -v OFS='\t' -v FPAT="([^,]+)|('[^']*')"\
        '$2 == 0 {print $1, $3;}'\
    | sed "s/'//g" \
    | sed -r "s/\a/\\\'/g"
