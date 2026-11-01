# rclone Learning & Experiment Results

## 1. File Operations: copy vs move vs sync

- **COPY**: Copies files from source to destination. Any existing files already present at the destination are preserved.
- **SYNC**: Makes destination match the source exactly. Any files that exist only at the destination will be removed.
- **MOVE**: Moves files or directories from source to destination. Once files are copied and verified, the source files are deleted.

## 2. Smart Transfer Skipping
rclone checks both the **file size** and the **modification time** of files at the source and destination. If both match identically, rclone skips the file completely without re-transferring data. If either differs, it performs the transfer.

## 3. Configuration-Free Execution
There are 3 ways to use rclone without creating a persistent config file on disk:
1. **Environment Variables**: Set `RCLONE_CONFIG_<NAME>_*` variables in memory.
2. **Command-Line Flags**: Pass backend configuration flags directly (e.g. `--s3-provider`, `--s3-endpoint`).
3. **On-the-fly Connection String**: Pass connection parameters directly inside the command path using `:s3:...:`.


## 4. Transfer Reliability & Large Files (1 GB)
- The `--bwlimit` flag lets us control the bandwidth used by rclone so transfers do not saturate the network or become a bottleneck for other services.
- For large files, rclone uploads data using S3 multipart uploads (splitting the file into chunks). If the network drops in the middle of a transfer, no corrupted or half-baked file appears in the S3 bucket. On retry, rclone resumes or re-uploads cleanly.

## 5. Sync Safety & Integrity Verification
- Since `sync` is designed to make the destination an exact mirror of the source, it will delete any extra files at the destination. It is strongly advised to run `sync` with the `--dry-run` flag first to preview what will be copied or deleted before running it for real.
- The `rclone check` command verifies whether the source and destination are completely in sync, detecting any missing files or data corruption.

## 6. Evaluation Questions

### Q1: What happens when rclone copy is executed twice with the same source and destination?
rclone checks the file size and modification time. Since they are identical on the second run, no data is re-uploaded, resulting in 0 bytes transferred.

### Q2: What happens if a file exists at the destination but not at the source when rclone sync runs?
The destination-only file will be deleted permanently without any prompt.

### Q3: How does rclone determine whether a file needs to be transferred?
It checks if the file exists at the destination, and if it does, it compares the file size and modification timestamp (or hashes if `--checksum` is enabled). If they differ, the file is transferred.

### Q4: Can rclone transfer data directly between two S3 providers without downloading it to the local machine?
Cloud providers do not support direct cross-cloud server-to-server transfers. However, rclone can stream the data directly through system memory from one S3 bucket to another without saving the file to the local disk. (Within the same provider, it uses direct server-side copying).

### Q5: What happens when a network connection is interrupted halfway through a 1 GB upload?
Large files are uploaded in chunks via S3 multipart upload. The interrupted upload leaves the bucket safe from partial or corrupt files. When the transfer is retried, rclone handles the upload and commits the completed file.

### Q6: How would you securely execute rclone from a Celery worker without maintaining an rclone.conf file?
Use **Option 1 (Environment Variables)**: Inject `RCLONE_CONFIG_<NAME>_*` into the worker process environment, and run rclone with the `--config=""` flag. This keeps each task isolated in memory with no credentials stored on disk.
