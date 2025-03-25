#!/bin/bash

INDEXNUMBER=$1
cd /path
TEMP_SCRIPT="ana_npz_fitqun_submit_temp_${1}.sh"
cp tempscript/ana_npz_fitqun_submit_temp.sh $TEMP_SCRIPT
sed -i "s|{{INDEXNUMBER}}|$INDEXNUMBER|g" $TEMP_SCRIPT


pjsub -N ana_npz_fq_${INDEXNUMBER} $TEMP_SCRIPT

rm $TEMP_SCRIPT

unset INDEXNUMBER
unset TEMP_SCRIPT

