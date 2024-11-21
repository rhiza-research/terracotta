while true
do
    gcloud storage rsync -r -u gs://sheerwatch-datalake/rasters /mnt/sheerwater-datalake
    sleep 60
done
