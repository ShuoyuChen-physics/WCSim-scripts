#!/bin/bash

#PJM -L rscgrp=all
#PJM -o /your/output/path/root2h5{{INDEXNUMBER}}.out
#PJM -e /your/output/path/root2h5{{INDEXNUMBER}}.err

source setup_env.sh

cd $WORKSPACE_PATH
python3 $WORKSPACE_PATH/FCroot2npz.py /your/rootstorage/path/e_0_range2gev_{{INDEXNUMBER}}.root -d /your/rootstorage/path/
python3 $WORKSPACE_PATH/FCnpz2h5.py /your/rootstorage/path/e_0_range2gev_{{INDEXNUMBER}}.npz  -o //your/h5storage/path/e_0_range2gev_{{INDEXNUMBER}}.h5
rm /your/rootstorage/path/e_0_range2gev_{{INDEXNUMBER}}.npz


