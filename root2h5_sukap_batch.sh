#!/bin/bash
###
 # @Author: Shuoyu Chen shuoyuchen.physics@gmail.com
 # @Date: 2025-03-19 16:41:16
 # @LastEditors: Shuoyu Chen shuoyuchen.physics@gmail.com
 # @LastEditTime: 2025-03-19 16:41:16
 # @FilePath: /schen/workspace/HKFDML/WCSim-scripts/root2h5_sukap_batch.sh
 # @Description: 
### 


INDEXNUMBER=$1

TEMP_SCRIPT="root2h5_temp_${1}.sh"

cp tempscript/root2h5_temp.sh $TEMP_SCRIPT
sed -i "s|{{INDEXNUMBER}}|$INDEXNUMBER|g" $TEMP_SCRIPT


pjsub -N root2h5_${INDEXNUMBER} $TEMP_SCRIPT

rm $TEMP_SCRIPT


unset INDEXNUMBER
unset TEMP_SCRIPT

