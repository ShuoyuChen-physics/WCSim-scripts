#!/bin/bash

IFS=$'\n\t'
LOG_FILE="massprolog/submission_$(date +%Y%m%d_%H%M%S).log"
echo "===== Batch Submission Script Started at $(date) =====" | tee -a "$LOG_FILE"

submit_job() {
    local job_id=$1
    
    ./submit_ana_npz_fitqun.sh "$job_id"
    if [ $? -eq 0 ]; then
        echo "$(date): Successfully submitted job ID $job_id." | tee -a "$LOG_FILE"
    else
        echo "$(date): Failed to submit job ID $job_id." | tee -a "$LOG_FILE" >&2
    fi
}

START_JOB_ID=500000        
TOTAL_JOBS=200
END_JOB_ID=$((START_JOB_ID + TOTAL_JOBS -1))
MAX_ACTIVE_JOBS=100
SLEEP_TIME=60

CURRENT_JOB_ID=$START_JOB_ID
SUBMISSION_COUNT=0

while [ "$CURRENT_JOB_ID" -le "$END_JOB_ID" ]; do

    active_jobs=$(pjstat | grep -E 'schen' | wc -l)
    echo "$(date): Current active jobs: $active_jobs" | tee -a "$LOG_FILE"
    available=$(( MAX_ACTIVE_JOBS - active_jobs ))
    
    if [ "$available" -gt 0 ]; then
        for ((i=0; i < available && CURRENT_JOB_ID <= END_JOB_ID; i++)); do
            submit_job "$CURRENT_JOB_ID"
            CURRENT_JOB_ID=$((CURRENT_JOB_ID +1))
            SUBMISSION_COUNT=$((SUBMISSION_COUNT +1))
        done
    else
        echo "$(date): Active job limit reached ($MAX_ACTIVE_JOBS). Waiting..." | tee -a "$LOG_FILE"
    fi
    echo "$(date): Sleeping for $SLEEP_TIME seconds before next check." | tee -a "$LOG_FILE"
    sleep "$SLEEP_TIME"
done

echo "$(date): All $SUBMISSION_COUNT jobs have been submitted." | tee -a "$LOG_FILE"
echo "===== Continuous Submission Script Ended at $(date) =====" | tee -a "$LOG_FILE"
