#!/bin/bash
#
# Replace page title in `pagelink` file by its corresponding id

# file1: page
# file2: pagelink
file1=$1
file2=$2
awk -v FS='\t' -v OFS='\t'\
    '{
        if(FNR==NR){
            d1[$1] = 1;
            d2[$2] = $1;
            next;
        }
        else{
            tmp = d1[$1];
            if(tmp != ""){
                tmp = d2[$2];
                if(tmp != "")
                    print $1, tmp;
            }
        }
    }' $file1 $file2
