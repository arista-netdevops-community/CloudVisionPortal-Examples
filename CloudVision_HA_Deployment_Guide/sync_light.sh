#!/bin/bash

# Copyright (c) 2026 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

SECONDARY="192.0.2.100"
SECONDARY_CLUSTER="Secondary Cluster"

# Sync this file and DHCPD config.
scp /etc/dhcp/dhcpd.conf root@${SECONDARY}:/etc/dhcp/dhcpd.conf
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