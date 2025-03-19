#!/bin/bash

#PJM -L rscgrp=all
#PJM -o /your/output/path/wcsim{{INDEXNUMBER}}.out
#PJM -e /your/error/path/wcsim{{INDEXNUMBER}}.err

source setup_env.sh
cd $WORKSPACE_PATH
WCSim $WORKSPACE_PATH/e_temp_{{INDEXNUMBER}}.mac $WCSIMDIR/macros/tuning_parameters.mac

rm $WORKSPACE_PATH/e_temp_{{INDEXNUMBER}}.mac


