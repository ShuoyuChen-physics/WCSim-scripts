<!--
 * @Author: Shuoyu Chen shuoyuchen.physics@gmail.com
 * @Date: 2025-03-19 16:21:08
 * @LastEditors: Shuoyu Chen shuoyuchen.physics@gmail.com
 * @LastEditTime: 2025-03-25 11:05:04
 * @FilePath: /schen/workspace/HKFDML/WCSim-scripts/README.md
 * @Description: 
-->
This repository contains scripts for generating datasets using WCSim for WatChMaL. (only works for sukap)

Please set your own paths by modifying the following lines:

- `e_temp.sh`: Line 471  
- `wcsim_submit_temp.sh`: Lines 4 and 5  
- `root2h5_temp.sh`: Lines 4, 5, 10, 11
- `setup_env.sh`: Line 3  

### Step 1: Generate root files using WCSim

I wrapped them into a shell script, which you can execute by running:

./sub_wcsim_masspro.sh

to perform mass WCSim data production.

We should modified the following parameters:

- **`START_EVENT`**: the starting event index.
- **`TOTAL_JOBS`**: the total number of jobs you want to submit.
- **`MAX_ACTIVE_JOBS`**: the maximum number of active jobs allowed simultaneously.
- **`SLEEP_TIME`**: time interval between checks (in seconds).

The script will submit jobs until the total number (`TOTAL_JOBS`) is reached. Every `SLEEP_TIME` seconds, it checks whether the number of currently active jobs is less than `MAX_ACTIVE_JOBS`. If yes, it automatically submits new jobs up to this limit, continuing this process until all jobs are submitted and completed. Each job generates one corresponding ROOT file.

The script calls submit_WCSim.sh, which copies templates (tempscript/e_500_temp.mac and tempscript/wcsim_submit_temp.sh) and then submits the job. (I'm not sure if there's a better way, but at least this method is straightforward and functional.)

If you need to modify the macro file, edit `e_temp.mac`.


### Step 2: Convert root files into h5 files

I also wrapped them into a shell script,

./root2h5_masspro.sh

It's similar with the `sub_wcsim_masspro.sh`.

This script calls `root2h5_sukap_batch.sh`, which copies the template script (`tempscript/root2h5_temp.sh`) and submits a job using `pjsub`. Within each submitted job, the scripts `FCroot2npz.py` and `FCnpz2h5.py` are executed to convert ROOT files into h5 format.

### Step 3: Merge h5 files

Merge individual h5 files into a single npz file:
./merge_h5.py /your/h5/file1 /your/h5/file2 /your/h5/file3 ... -o /your/output/path

Assigning labels to identify their train/validation/test splits.
./gen_split.py
(modify Line 12)

Then you can have h5 files and npz files, which can be used for WatChMaL.




### Others:

./sub_fitqun_masspro.sh used for submitting jobs to sukap nodes to run fiTQun.

./sub_ana_npz_fitqun_masspro.sh used for extracting the reconstruction result from the fiTQun result root file and write the result into a npz file which is easier for the later analysis.






