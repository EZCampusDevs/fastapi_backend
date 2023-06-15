#!/bin/sh

log_dir="$HOME/log/jenkins-ssh"
mkdir -p $log_dir

log_file="$log_dir/fastapi_backend-dockerrun-log.out"
touch log_file

exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>$log_file 2>&1

container_name="fastapi_backend-instance"

echo "Stopping container..."

docker stop $container_name || true

while [ "$(docker inspect -f '{{.State.Running}}' "$container_name" 2>/dev/null)" = "true" ]; do
    echo "Waiting for container to stop..."
    sleep 1
done

echo "Running build..."

docker run -itd --rm -p 8000:8000 --network EZnet --name $container_name fastapi_backend

echo "Deploy done."
