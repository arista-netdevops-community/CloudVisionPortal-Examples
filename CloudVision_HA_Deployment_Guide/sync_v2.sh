#!/bin/bash

# Copyright (c) 2026 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

SECONDARY="x.x.x.x"
SECONDARY_CLUSTER="Secondary Cluster"
PASS="cvpadmin"


SYSLOG_SRVS=`grep -E '(@@?|@)[^ ]+' /etc/cvpi/rsyslog.conf  |grep -v remote-host | cut -f2 -d '@' | sort -n | uniq`

ping -c 3 "$SECONDARY" > /dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "Ping to $SECONDARY Successful"
else
  echo "Ping to $SECONDARY FAILED"
  for IP in $SYSLOG_SRVS; do
    SRV_IP="$(echo $IP | cut -d':' -f1)"
    SRV_PT="$(echo $IP | cut -d':' -f2)"
    logger -n $SRV_IP -P $SRV_PT -d -p user.crit "%CVP-3-HA: Ping to $SECONDARY - SECONDARY CLUSTER FAILED"
  done
  exit 1
fi

# Sync this file and DHCPD config.
scp  /etc/dhcp/dhcpd.conf root@${SECONDARY}:/etc/dhcp/dhcpd.conf
scp /root/sync.sh root@${SECONDARY}:/root/sync.sh

# BACKUP CVP
/cvpi/bin/cvpi backup cvp

# SYNC CVP BACKUP TO SECONDARY
FILES=`ls -t /data/cvpbackup/cvp.20* | head -1`
FILES="$FILES $(ls -t /data/cvpbackup/cvp.eos* | head -1)"
for FILE in $FILES; do
  scp ${FILE} root@${SECONDARY}:${FILE}
done

ssh root@${SECONDARY} "
        chown cvp:cvp /data/cvpbackup/* ; \
        su cvp -c \"export RESTORE_SYNC={}; cvpi restore cvp ${FILES} ;\"; \
        /cvpi/tools/apish publish -d cvp -p /clusterManagement \
        --update '{\"key\":\"clusterName\", \"value\": \"${SECONDARY_CLUSTER}\"}'"

echo "Script completed Successfully"
exit 0 # Exit the script with status 0 (Success)