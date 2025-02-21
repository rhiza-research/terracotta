#!/bin/bash

MOUNT_POINT="/mnt/sheerwater-datalake"
GCS_BUCKET="gs://sheerwater-datalake/rasters"
SLEEP_TIME=1800

# Check if the mount point exists
if [ ! -d "$MOUNT_POINT" ]; then
    echo "Error: Mount point $MOUNT_POINT does not exist"
    exit 1
fi

# Test write permissions using -w test
if [ ! -w "$MOUNT_POINT" ]; then
    echo "Volume is mounted read-only on $HOSTNAME, skipping raster sync"
    exit 0
else
    echo "Volume is mounted read-write on $HOSTNAME, proceeding with raster sync"
fi

# Proceed with sync if we have write access
while true; do
    echo "Starting raster sync at $(date)"
    gcloud storage rsync -r -u "$GCS_BUCKET" "$MOUNT_POINT"
    sync_status=$?
    
    if [ $sync_status -eq 0 ]; then
        echo "Sync completed successfully at $(date)"
    else
        echo "Sync failed with status $sync_status at $(date)"
    fi
    
    echo "Sleeping for $SLEEP_TIME seconds..."
    sleep $SLEEP_TIME
done
