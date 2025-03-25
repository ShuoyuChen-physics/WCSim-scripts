#!/bin/bash

#PJM -L rscgrp=all
#PJM -o /path/out/ananpzfq{{INDEXNUMBER}}.out
#PJM -e /path/err/ananpzfq{{INDEXNUMBER}}.err

source setup_env.sh
cd /path

python3 FCfqroot.py /disk03/usr8/schen/workspace/HKFDML/MCstorage/root/e_0_range2gev_{{INDEXNUMBER}}.root -f /disk03/usr8/schen/workspace/HKFDML/MCstorage/fitqun-root/fq_e_0_range2gev_{{INDEXNUMBER}}.root -o /disk03/usr8/schen/workspace/HKFDML/MCstorage/fitqun-ana/fq_e_0_range2gev_{{INDEXNUMBER}}.npz


