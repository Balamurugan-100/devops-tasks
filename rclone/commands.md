# rclone Commands Reference

All commands below include `--config=""` so they run statelessly without reading or writing a config file to disk.

---

## 1. Basic File Operations (Local to Local)

### Listing
```bash
# Clean list of files and folders (folders end with /)
rclone --config="" lsf source/

# List only directories
rclone --config="" lsd source/

# List files with sizes recursively
rclone --config="" ls source/

# Show directory structure as a visual tree
rclone --config="" tree source/
```

### Copying & Moving
```bash
# Copy: adds/updates files at destination without deleting anything
rclone --config="" copy source/ dest/

# Move: copies files, then deletes the original source files
rclone --config="" move source/ dest/
```

### Syncing
```bash
# Preview what sync would do without modifying anything (always do this first!)
rclone --config="" sync source/ dest/ --dry-run

# Run sync: makes destination identical to source (deletes destination-only files!)
rclone --config="" sync source/ dest/
```

### Verification & Deletion
```bash
# Check if source and destination files match identically
rclone --config="" check source/ dest/

# Delete files in a destination path
rclone --config="" delete dest/

# Delete a single specific file
rclone --config="" deletefile dest/notes.txt
```

---

## 2. S3 Operations (MinIO)

Assuming environment variables for `MYSTORAGE` are exported:

```bash
# Create a new bucket
rclone --config="" mkdir MYSTORAGE:test-bucket-1

# List all buckets
rclone --config="" lsd MYSTORAGE:

# Upload a local folder to a bucket
rclone --config="" copy source/ MYSTORAGE:test-bucket-1/sample/

# List contents of a bucket
rclone --config="" lsf MYSTORAGE:test-bucket-1/sample/

# Download from S3 back to a local folder
rclone --config="" copy MYSTORAGE:test-bucket-1/sample/ ./downloaded/

# Copy directly from one bucket to another (server-side copy)
rclone --config="" copy MYSTORAGE:test-bucket-1/sample/ MYSTORAGE:test-bucket-2/backup/

# Delete a specific object in S3
rclone --config="" deletefile MYSTORAGE:test-bucket-1/sample/notes.txt
```

---

## 3. Transfer Reliability & Performance Flags

```bash
# Show live progress bar in terminal
rclone --config="" copy source/ MYSTORAGE:test-bucket-1/ -P

# Limit bandwidth to 20 MB/s
rclone --config="" copy file_1gb.bin MYSTORAGE:test-bucket-1/large/ --bwlimit 20M

# Control number of concurrent file transfers (default is 4)
rclone --config="" copy source/ MYSTORAGE:test-bucket-1/ --transfers 8

# Configure retries for unstable connections
rclone --config="" copy source/ MYSTORAGE:test-bucket-1/ --retries 3 --low-level-retries 10
```

---

## 4. Alternative Config-Free Methods

If you do not want to set environment variables, you can use these alternative methods:

### Method A: On-the-fly connection string (`:s3:`)
```bash
rclone --config="" copy source/ ":s3,provider=Minio,endpoint='http://127.0.0.1:9010',access_key_id='minioadmin',secret_access_key='minioadmin':test-bucket-1/demo"
```

### Method B: Passing backend flags directly
```bash
rclone --config="" \
  --s3-provider Minio \
  --s3-endpoint http://127.0.0.1:9010 \
  --s3-access-key-id minioadmin \
  --s3-secret-access-key minioadmin \
  copy source/ :s3:test-bucket-1/demo
```
