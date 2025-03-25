#!/bin/bash

#PJM -L rscgrp=all
#PJM -o /path/out/fq{{INDEXNUMBER}}.out
#PJM -e /path/err/fq{{INDEXNUMBER}}.err

source setup_env.sh
cd /path


/disk03/usr8/schen/software/fiTQun/runfiTQunWC -p ${FITQUN_ROOT}/ParameterOverrideFiles/HyperK.parameters.dat -r /disk03/usr8/schen/workspace/HKFDML/MCstorage/fitqun-root/fq_e_0_range2gev_{{INDEXNUMBER}}.root /disk03/usr8/schen/workspace/HKFDML/MCstorage/root/e_0_range2gev_{{INDEXNUMBER}}.root
