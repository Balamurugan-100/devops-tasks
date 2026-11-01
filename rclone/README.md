# rclone File Transfer Lab

A simple, reproducible guide on using `rclone` for file transfers and synchronization with an S3-compatible backend (MinIO) without relying on persistent configuration files.

---

## Prerequisites

- `rclone` installed (`rclone version`)
- Docker and Docker Compose

---

## 1. Setup Local S3 (MinIO)

Start the local MinIO container using Docker Compose:

```bash
docker-compose up -d
```

- **S3 Endpoint:** `http://127.0.0.1:9010`
- **MinIO Console:** `http://127.0.0.1:9011`
- **Credentials:** `minioadmin` / `minioadmin`

---

## 2. Generate Test Files

Run these commands to create dummy files of various sizes and directory structures:

```bash
mkdir -p source/docs source/media dest
echo "Hello from rclone" > source/notes.txt
echo '{"app": "testpress"}' > source/config.json
echo "Sample PDF header" > source/docs/sample.pdf
echo "Nested info" > source/media/info.txt

# 100 MB test file
dd if=/dev/urandom of=source/file_100mb.bin bs=1m count=100

# 1 GB large test file
dd if=/dev/urandom of=file_1gb.bin bs=1m count=1024
```

---

## 3. Configuration-Free Setup

Instead of running `rclone config` to save credentials to disk, set them as environment variables in your current terminal session:

```bash
export RCLONE_CONFIG_MYSTORAGE_TYPE=s3
export RCLONE_CONFIG_MYSTORAGE_PROVIDER=Minio
export RCLONE_CONFIG_MYSTORAGE_ENDPOINT=http://127.0.0.1:9010
export RCLONE_CONFIG_MYSTORAGE_ACCESS_KEY_ID=minioadmin
export RCLONE_CONFIG_MYSTORAGE_SECRET_ACCESS_KEY=minioadmin
```

Always use `--config=""` in commands to ensure rclone ignores any `~/.config/rclone/rclone.conf` file.

Verify the connection:
```bash
rclone --config="" lsd MYSTORAGE:
```

---

## 4. Using the Transfer Script (`transfer.sh`)

`transfer.sh` automates transfers with logging, progress output, error codes, and config-free execution.

```bash
# Make it executable
chmod +x transfer.sh

# Copy files to S3
./transfer.sh -m copy source MYSTORAGE:test-bucket-1/backup

# Sync with a dry-run preview (safe check)
./transfer.sh -m sync -n source MYSTORAGE:test-bucket-1/backup

# Sync with speed limit (10MB/s)
./transfer.sh -m sync -b 10M source MYSTORAGE:test-bucket-1/backup
```

---

## Files in this Repository

- `docker-compose.yml` - Starts the local MinIO storage service.
- `transfer.sh` - Reusable automation script for copy/sync.
- `commands.md` - Command reference used throughout the exercises.
- `results.md` - Test findings and answers to the assignment questions.
