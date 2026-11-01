# Automated Server Provisioning with cloud-init

A hands-on, reproducible guide for automating Linux server setup (Ubuntu 24.04) from first boot using `cloud-init` without manual SSH configuration.

---

## 1. Overview

Instead of manually SSH-ing into newly created servers to run setup commands, this project uses `cloud-init.yaml` to automatically:
1. Update system packages and install prerequisites (`docker`, `git`, `curl`, `ffmpeg`).
2. Create a non-root user `testpress` with passwordless `sudo` and `docker` group permissions.
3. Set up the application directory at `/opt/testpress` with environment variables in `/opt/testpress/app.env`.
4. Deploy a containerized Python HTTP service on port `8080` returning `"Hello from Testpress!"`.
5. Register a `systemd` unit (`testpress-app.service`) to start the stack on boot and restart if it crashes.

---

## 2. Launching the VM

You can launch a fresh Ubuntu 24.04 instance using Multipass, QEMU, or OrbStack with `cloud-init.yaml`:

### Option A: Using Multipass
```bash
multipass launch 24.04 --name testpress-lab --cloud-init cloud-init.yaml
```

### Option B: Using OrbStack
```bash
orb create ubuntu:noble testpress-lab -c cloud-init.yaml
```
*(OrbStack uses the flag `-c` or `--user-data` for cloud-init configurations).*

Wait until cloud-init finishes its run:
```bash
# Check provisioning status
cloud-init status --wait
```

---

## 3. Verification & Outputs

### 1. Test Application Over HTTP
From your host machine, query port `8080` of the VM:
```bash
curl -i http://<VM_IP>:8080/
```
**Output:**
```text
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.12.16
Date: Sun, 01 Nov 2026 17:22:08 GMT
Content-Type: text/plain; charset=utf-8
Content-Length: 22

Hello from Testpress!
```

### 2. Verify User & Docker Group Permissions
Ensure `testpress` user exists and can run Docker without `sudo`:
```bash
id testpress
```
**Output:**
```text
uid=1000(testpress) gid=1000(testpress) groups=1000(testpress),27(sudo),989(docker)
```

Run Docker as `testpress`:
```bash
sudo -u testpress docker ps
```
**Output:**
```text
CONTAINER ID   IMAGE                 COMMAND                 STATUS                    PORTS                    NAMES
860f3dbd443f   testpress-app:local   "python3 /app/app.py"   Up 45 minutes (healthy)   0.0.0.0:8080->8080/tcp   testpress-lab-app-1
```

### 3. Verify Installed Packages
```bash
ffmpeg -version | head -1
git --version
curl --version | head -1
```
**Output:**
```text
ffmpeg version 6.1.1-3ubuntu5 Copyright (c) 2000-2023 the FFmpeg developers
git version 2.43.0
curl 8.5.0 (aarch64-unknown-linux-gnu)
```

### 4. Verify Systemd Service & Auto-Boot
The container is managed by `/etc/systemd/system/testpress-app.service`:
```bash
systemctl status testpress-app.service
```
**Output:**
```text
● testpress-app.service - Testpress Docker app (compose stack)
     Loaded: loaded (/etc/systemd/system/testpress-app.service; enabled; preset: enabled)
     Active: active (exited)
```

* **Crash Recovery**: Docker's `restart: unless-stopped` policy restarts the container if the Python process is killed.
* **Reboot Persistence**: The systemd service is `enabled`, automatically rebuilding or launching the stack whenever the VM reboots.

---

## 4. How Cloud-Init Works

When a new machine powers on, `cloud-init` runs early in the boot sequence to configure the operating system based on the provided user-data before any user ever logs in.

### The 4 Execution Stages (1 Line Each)
1. **Generator / Local (`cloud-init-local.service`)**: Identifies local data sources and brings up basic fallback networking so the system can boot. *(Runs on every boot)*
2. **Network / Init (`cloud-init.service`)**: Brings up full networking, reads the user-data YAML, and sets up hostnames, users, and groups. *(Runs once on first boot)*
3. **Config (`cloud-config.service`)**: Writes declared configuration files (`write_files`) and installs system packages (`packages`). *(Runs once on first boot)*
4. **Final (`cloud-final.service`)**: Executes custom shell commands (`runcmd`), sets up systemd services, and starts applications at the end of boot. *(Runs once on first boot)*

---

### How Cloud-Init Determines "First Boot"
- On first boot, cloud-init records the machine's hardware instance ID inside `/var/lib/cloud/instance/instance-id`.
- On every normal reboot, cloud-init compares the hardware ID against this saved file.
- Since the IDs match, cloud-init knows the server was already provisioned and **skips stages 2, 3, and 4**.

---

### What Does `cloud-init clean` Do?
Running `cloud-init clean` wipes `/var/lib/cloud/` and removes the saved `instance-id`. This resets cloud-init's memory, tricking it into treating the next reboot as a brand new **first boot** and re-running the entire setup.

---

### The Neovim Experiment (Proving First-Boot Logic)

To prove this behavior in practice, we ran the following test:

1. **Test 1: Normal Reboot**
   * Installed Neovim via cloud-init.
   * Manually uninstalled Neovim (`rm /usr/local/bin/nvim` / `apt remove`).
   * Rebooted the VM.
   * **Result:** Neovim was **still missing**. Because cloud-init saw the matching `instance-id`, it skipped provisioning on boot.

2. **Test 2: Reboot After `cloud-init clean`**
   * With Neovim still uninstalled, executed:
     ```bash
     sudo cloud-init clean
     sudo reboot
     ```
   * **Result:** After rebooting, Neovim was **automatically re-downloaded and restored**. 
   * **Why?** `cloud-init clean` erased the instance state, forcing cloud-init to execute all 4 stages again from scratch.

---

## 5. cloud-init vs. Dockerfile: What's the Difference?

| Feature | `cloud-init` | `Dockerfile` |
| :--- | :--- | :--- |
| **Scope** | Provisions the **entire host OS / VM** (kernel settings, users, disk mounts, system packages, network). | Provisions a single **isolated container filesystem**. |
| **Execution** | Runs dynamically at first boot on the machine. | Runs at build-time to produce a static container image. |
| **Purpose** | Brings bare-metal or cloud VMs to a desired baseline state. | Packages application code and runtime dependencies for portability. |
| **Relationship** | `cloud-init` installs Docker and orchestrates containers; `Dockerfile` defines what runs inside each container. |
