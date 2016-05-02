#!/bin/bash
#
# Convert wikipedia's MySQL dump to csv file on preserving only vertices' and edges' information

file=$1
if [ "$#" -le 2 ]; then
    >&2 echo "All namespaces will be selected"
    namespace=-1
else
    namespace=${@:2}
    >&2 echo "Namespace "${namespace}" will be selected" 
fi
sed -n '/INSERT INTO `.*` VALUES /p' $file \
    | sed 's/INSERT INTO `.*` VALUES //' \
    | sed 's/),(/)\n(/g' \
    | sed -r "s/^\(//;s/\)$//;s/\\\'/\a/g" \
    | awk -v OFS='\t' -v FPAT="([^,]+)|('[^']*')" -v namespace="${namespace}"\
    'BEGIN{split(namespace, namespaces, " ");}\
    {if(namespaces[0] == -1)
        print $1, $3;
     else{
         for(name in namespaces){
             if($2==name){
                 print $1, $3
                 break;
             }
         }
     }
    }'\
    | sed "s/\t'/\t/;s/'$//;s/\a/'/g" \
    | sed 's/\\\"//g'
