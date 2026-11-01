#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<EOF
Usage: $0 [options] <source> <destination>

Arguments:
  <source>         Source path or remote
  <destination>    Destination path or remote

Options:
  -m, --mode MODE        Transfer mode: 'copy' (default) or 'sync'
  -b, --bwlimit LIMIT    Bandwidth limit (e.g. 10M, 50M)
  -t, --transfers NUM    Concurrent file transfers (default: 4)
  -n, --dry-run          Perform a trial run with no changes made
  -l, --log-file FILE    Path to log file (default: ./transfer.log)
  -h, --help             Display this help message
EOF
    exit 1
}

MODE="copy"
BWLIMIT=""
TRANSFERS="4"
DRY_RUN=false
LOG_FILE="./transfer.log"
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -b|--bwlimit)
            BWLIMIT="$2"
            shift 2
            ;;
        -t|--transfers)
            TRANSFERS="$2"
            shift 2
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -l|--log-file)
            LOG_FILE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

if [[ ${#POSITIONAL_ARGS[@]} -ne 2 ]]; then
    echo "Error: Source and Destination are required." >&2
    usage
fi

SRC="${POSITIONAL_ARGS[0]}"
DEST="${POSITIONAL_ARGS[1]}"

if [[ "$MODE" != "copy" && "$MODE" != "sync" ]]; then
    echo "Error: Invalid mode '$MODE'. Allowed modes: 'copy', 'sync'." >&2
    exit 2
fi

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local timestamp
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "[$timestamp] $*" | tee -a "$LOG_FILE"
}

log "INFO: Starting transfer [mode: $MODE]"
log "INFO: Source:      $SRC"
log "INFO: Destination: $DEST"

RCLONE_CMD=(
    rclone
    --config=""
    "$MODE"
    "$SRC"
    "$DEST"
    --transfers "$TRANSFERS"
    --stats 1s
    --stats-one-line
    --retries 2
    --low-level-retries 3
    --contimeout 5s
    --timeout 10s
    -v
)

if [[ -n "$BWLIMIT" ]]; then
    RCLONE_CMD+=(--bwlimit "$BWLIMIT")
fi

if [[ "$DRY_RUN" == true ]]; then
    RCLONE_CMD+=(--dry-run)
    log "INFO: Dry-run flag enabled."
fi

set +e
"${RCLONE_CMD[@]}" 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}
set -e

if [[ $EXIT_CODE -eq 0 ]]; then
    log "SUCCESS: Transfer finished successfully."
else
    log "ERROR: Transfer failed with exit code $EXIT_CODE."
fi

exit "$EXIT_CODE"
