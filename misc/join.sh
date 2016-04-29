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
            dict[$2] = $1;
            next;
        }
        else{
            tmp = dict[$2];
            if(tmp != "")
                print $1, dict[$2];
        }
    }' $file1 $file2
