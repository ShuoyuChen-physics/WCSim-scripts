#!/bin/bash
###
 # @Author: Shuoyu Chen shuoyuchen.physics@gmail.com
 # @Date: 2025-03-25 10:52:47
 # @LastEditors: Shuoyu Chen shuoyuchen.physics@gmail.com
 # @LastEditTime: 2025-03-25 10:52:48
 # @FilePath: /schen/workspace/HKFDML/WCSim-scripts/submit_fitqun.sh
 # @Description: 
### 

INDEXNUMBER=$1
cd /disk03/usr8/schen/workspace/HKFDML/tool 
TEMP_SCRIPT="fitqun_submit_temp_${1}.sh"
cp tempscript/fitqun_submit_temp.sh $TEMP_SCRIPT
sed -i "s|{{INDEXNUMBER}}|$INDEXNUMBER|g" $TEMP_SCRIPT


pjsub -N fq_${INDEXNUMBER} $TEMP_SCRIPT

rm $TEMP_SCRIPT

unset INDEXNUMBER
unset TEMP_SCRIPT

