while true
do
    gcloud storage rsync -r -u gs://sheerwatch-benchmarking/rasters /mnt/sheerwater-datalake
    sleep 60
done
