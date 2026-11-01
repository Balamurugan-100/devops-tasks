# Testpress Engineering Labs

This repository contains two hands-on infrastructure automation and data transfer labs:

## 1. Automated Server Provisioning (`cloud-init/`)
Automates complete Linux server setup (Ubuntu 24.04) from first boot using `cloud-init` without manual SSH intervention.
* Installs Docker, FFmpeg, Git, and system dependencies.
* Sets up non-root user `testpress` with Docker permissions.
* Deploys a containerized HTTP service on port `8080` managed by systemd.
* **[Setup guide & notes](./cloud-init/README.md)**

## 2. Stateless File Transfer & Sync (`rclone/`)
Builds a reproducible, configuration-free file transfer workflow across local storage and S3-compatible object storage (MinIO).
* Implements configuration-free execution using environment variables (`RCLONE_CONFIG_*`).
* Explores `copy` vs `move` vs `sync`, bandwidth throttling (`--bwlimit`), and multipart upload resilience.
* Includes a reusable automation script (`transfer.sh`).
* **[Setup & lab notes](./rclone/README.md)** | **[Commands cheat sheet](./rclone/commands.md)** | **[Observations & answers](./rclone/results.md)**

---

## Repository Structure

```text
.
├── cloud-init/
│   ├── cloud-init.yaml      # Cloud-init configuration for VM provisioning
│   └── README.md            # Reproduction guide & execution stages
│
├── rclone/
│   ├── docker-compose.yml   # Local MinIO S3 service
│   ├── transfer.sh          # Reusable CLI transfer script
│   ├── README.md            # Rclone setup & reproduction guide
│   ├── commands.md          # Reference of executed rclone commands
│   └── results.md           # Test findings & answers to evaluation questions
│
└── README.md                # Project index
```
