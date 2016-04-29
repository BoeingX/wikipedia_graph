#!/bin/bash
#
# Convert wikipedia's MySQL dump to csv file on preserving only vertices' and edges' information

file=$1
if [ "$#" -ne 2 ]; then
    >&2 echo "All namespaces will be selected"
    namespace=-1
else
    namespace=$2
    >&2 echo "Namespace "$2" will be selected" 
fi
sed -n '/INSERT INTO `.*` VALUES /p' $file \
    | sed 's/INSERT INTO `.*` VALUES //' \
    | sed 's/),(/)\n(/g' \
    | sed 's/^(//;s/)$//;' \
    | sed -r "s/\\\'/\a/g"\
    | awk -v OFS='\t' -v FPAT="([^,]+)|('[^']*')" -v namespace=$namespace\
        'namespace == -1 || namespace == $2 {print $1, $3;}'\
    | sed "s/'//g" \
    | sed -r "s/\a/\\\'/g"
