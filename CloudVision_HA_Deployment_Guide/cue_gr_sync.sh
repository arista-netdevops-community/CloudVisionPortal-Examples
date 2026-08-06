#!/bin/bash

# Copyright (c) 2026 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

#########################################
# 1. Global Variables
#########################################

# User-configurable parameters
SECONDARY="x.x.x.x"
LOG_FILE="/root/cue_gr_sync.log"
SCRIPT_PATH="/root/cue_gr_sync.sh"

# System parameters (do not modify)
BACKUP_DIR="/data/wifimanager/backup"
WM_BKP_PATH="/opt/wibhu/spectraguard/data/backup/datastore/full_bkp"
EXEC_CMD="nerdctl exec wifimanager"


#########################################
# Helper functions
#########################################
log() {
  local message="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  echo "$message"
  echo "$message" >> "$LOG_FILE"
}

rotate_log() {
  if [ -f "$LOG_FILE" ]; then
    local file_size=$(stat -c%s "$LOG_FILE" 2>/dev/null)
    local max_size=$((5 * 1024 * 1024))  # 5MB
    local keep_bytes=2621440  # 2.5MB

    if [ "$file_size" -gt "$max_size" ]; then
      local temp_file="${LOG_FILE}.tmp"

      # Keep only the last 2.5MB
      tail -c "$keep_bytes" "$LOG_FILE" > "$temp_file"
      mv "$temp_file" "$LOG_FILE"
    fi
  fi
}

run_cleanup() {
  local desc="$1"
  local cmd="$2"

  ERROR_MSG=$(eval "$cmd" 2>&1)
  if [ $? -ne 0 ]; then
    log "WARNING: Failed to remove backup files from $desc"
    log "Error details: ${ERROR_MSG}"
  fi
}

get_secondary_mount_path() {
  local cmd output rc

  cmd='sudo nerdctl -n=k8s.io --data-root=${CVP_DATA_DIR}/wifimanager/ volume inspect wifimanager_data | jq -r ".[0].Mountpoint"'

  # Execute on remote host
  output=$(ssh -o BatchMode=yes -o ConnectTimeout=5 root@"$SECONDARY" "$cmd" 2>/dev/null)
  rc=$?

  # Validate result
  if [ $rc -ne 0 ] || [ -z "$output" ] || [ "$output" = "null" ]; then
    log "WARNING: Could not determine secondary backup mount path"
    SECONDARY_BACKUP_MOUNT_PATH=""
    return 1
  fi

  SECONDARY_BACKUP_MOUNT_PATH="$output"
  log "Secondary backup mount path: ${SECONDARY_BACKUP_MOUNT_PATH}"
  return 0
}

clean_up() {
  log "Cleaning up backup files..."

  local files="${LATEST_BACKUP_TGZ} ${LATEST_BACKUP_MD5}"

  run_cleanup "primary container" \
    "$EXEC_CMD sh -c 'rm -f ${WM_BKP_PATH}/${files}'"

  run_cleanup "primary host" \
    "rm -f \"$BACKUP_TGZ_PATH\" \"$BACKUP_MD5_PATH\""

  run_cleanup "secondary host" \
    "ssh root@\"$SECONDARY\" 'rm -f ${BACKUP_DIR}/${files}'"

  # Secondary container - using volume mount path
  if [ -n "$SECONDARY_BACKUP_MOUNT_PATH" ]; then
    local sec_path="${SECONDARY_BACKUP_MOUNT_PATH}/data/backup/datastore/full_bkp"
    run_cleanup "secondary container" \
      "ssh root@\"$SECONDARY\" 'sudo rm -f ${sec_path}/${files}'"
  fi

  log "Cleanup completed"
}

#########################################
# 2. Start logging
#########################################
rotate_log
log "=========================================="
log "Starting GR sync process"
log "=========================================="

#########################################
# 3. Validate script path
#########################################
if [ ! -f "$SCRIPT_PATH" ]; then
  log "ERROR: Script not found at ${SCRIPT_PATH}"
  exit 1
fi

#########################################
# 4. Check connectivity
#########################################
log "Checking connectivity to secondary node ${SECONDARY}..."
ERROR_MSG=$(ping -c 3 "$SECONDARY" 2>&1)
if [ $? -ne 0 ]; then
  log "ERROR: Ping failed to ${SECONDARY}"
  log "Error details: ${ERROR_MSG}"
  exit 1
fi
log "Connectivity check passed"

#########################################
# 5. Get secondary mount path
#########################################
get_secondary_mount_path

#########################################
# 6. Sync script
#########################################
log "Syncing script ${SCRIPT_PATH} to secondary node ${SECONDARY}..."
ERROR_MSG=$(scp "$SCRIPT_PATH" root@"$SECONDARY":"$SCRIPT_PATH" 2>&1)
if [ $? -ne 0 ]; then
  log "WARNING: Failed to sync script to ${SECONDARY}"
  log "Error details: ${ERROR_MSG}"
else
  log "Script synced successfully"
fi

#########################################
# 7. Take backup
#########################################
log "Taking backup of wifimanager container..."
ERROR_MSG=$(/cvpi/bin/cvpi backup-config wifimanager 2>&1)
if [ $? -ne 0 ]; then
  log "ERROR: Failed to take backup of wifimanager container"
  log "Error details: ${ERROR_MSG}"
  exit 1
fi
log "Backup completed successfully"

#########################################
# 8. Get latest backup (inside container)
#########################################
log "Fetching latest backup from container path ${WM_BKP_PATH}..."

LATEST_BACKUP_TGZ=$($EXEC_CMD sh -c \
"ls -t ${WM_BKP_PATH}/*_Config.tgz 2>/dev/null | head -1 | xargs -n1 basename")

if [ -z "$LATEST_BACKUP_TGZ" ]; then
  log "ERROR: No backup found in ${WM_BKP_PATH}"
  exit 1
fi

log "Found backup file: ${LATEST_BACKUP_TGZ}"
LATEST_BACKUP_MD5="${LATEST_BACKUP_TGZ}.md5"

# Host paths
BACKUP_TGZ_PATH="${BACKUP_DIR}/${LATEST_BACKUP_TGZ}"
BACKUP_MD5_PATH="${BACKUP_DIR}/${LATEST_BACKUP_MD5}"

if [ ! -f "$BACKUP_MD5_PATH" ]; then
  log "ERROR: Missing MD5 file: ${BACKUP_MD5_PATH}"
  exit 1
fi

log "Using backup file: ${BACKUP_TGZ_PATH}"

#########################################
# 9. Copy to secondary
#########################################
log "Copying backup files to secondary ${SECONDARY}:${BACKUP_DIR}/..."
ERROR_MSG=$(scp "$BACKUP_TGZ_PATH" "$BACKUP_MD5_PATH" \
     root@"$SECONDARY":"$BACKUP_DIR/" 2>&1)
if [ $? -ne 0 ]; then
  log "ERROR: Failed to copy backup files to ${SECONDARY}"
  log "Error details: ${ERROR_MSG}"
  clean_up
  exit 1
fi
log "Backup files copied successfully"

#########################################
# 10. Restore on secondary
#########################################
log "Restoring backup on secondary node ${SECONDARY}..."

ERROR_MSG=$(ssh root@"$SECONDARY" "
chown cvp:cvp ${BACKUP_DIR}/${LATEST_BACKUP_TGZ}* &&
su cvp -c '/cvpi/bin/cvpi restore wifimanager \
  ${BACKUP_DIR}/${LATEST_BACKUP_TGZ} SKIP_LICENSE_RESTORE'
" 2>&1)
if [ $? -ne 0 ]; then
  log "ERROR: Restore failed on secondary ${SECONDARY}"
  log "Error details: ${ERROR_MSG}"
  clean_up
  exit 1
fi
log "Restore completed successfully on secondary"

clean_up

log "GR sync completed successfully to secondary ${SECONDARY}"
exit 0