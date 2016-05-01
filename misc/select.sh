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
            d[$1] = 1;
            next;
        }
        else{
            tmp = d[$1];
            if(tmp != ""){
                tmp = d[$2];
                if(tmp != ""){
                    print $0;
                }
            }
        }
    }' $file1 $file2
