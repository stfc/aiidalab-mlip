#!/usr/bin/env bash
# Start the AiiDA REST API inside the AiiDAlab container.
# Binds to 0.0.0.0 so it can be reached from a proxy container.

. /opt/conda/etc/profile.d/conda.sh
conda activate base

if ! verdi profile show >/dev/null 2>&1; then
    echo "No active AiiDA profile found. Skipping REST API startup."
    exit 0
fi

pkill -f "verdi.*restapi" 2>/dev/null || true
sleep 1

PROFILE="$(verdi profile list 2>/dev/null | grep -E '^\* ' | awk '{print $2}' || true)"
if [ -n "$PROFILE" ]; then
    nohup verdi -p "$PROFILE" restapi --hostname 0.0.0.0 --port 5000 > /tmp/aiida-restapi.log 2>&1 &
else
    nohup verdi restapi --hostname 0.0.0.0 --port 5000 > /tmp/aiida-restapi.log 2>&1 &
fi
echo $! > /tmp/aiida-restapi.pid

sleep 2
# Verify it started
if ! ps -p "$(cat /tmp/aiida-restapi.pid 2>/dev/null)" > /dev/null 2>&1; then
    echo "Warning: AiiDA REST API failed to start. Output:"
    cat /tmp/aiida-restapi.log 2>/dev/null || true
    exit 0
fi


