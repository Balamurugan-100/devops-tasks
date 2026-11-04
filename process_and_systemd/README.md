# Linux Process Management and systemd

A Python HTTP service used to explore Linux signals, automatic restarts, failure investigation, and systemd resource limits.

The app logs a heartbeat every five seconds, even when no HTTP requests arrive, and handles SIGTERM and SIGINT gracefully.

See [experiments.md](experiments.md) for what I learnt and the screenshots in [evidence/](evidence/).

## Setup

Use a Linux environment with systemd, Python 3.11, and curl. No additional Python packages are required.

Update `User`, `WorkingDirectory`, and `ExecStart` in `testpress.service` to match your non-root user, project directory, and Python executable. The service user must be able to write `app.log` in the project directory.

From this directory:

```bash
sudo cp testpress.service /etc/systemd/system/testpress.service
sudo systemctl daemon-reload
sudo systemctl enable --now testpress
systemctl status testpress --no-pager -l
curl http://localhost:8000/health
```

To run the app directly instead, stop the service and run `python3 app.py`. The default address is `0.0.0.0:8000`; use `--host` and `--port` to change it.

## Test endpoints

| Endpoint | Purpose |
| --- | --- |
| `/hello` | Returns Hello World |
| `/health` | Checks that the app responds |
| `/crash` | Simulates a failure and exits with status 1 |
| `/load/memory` | Attempts to allocate 256 MB |
| `/load/cpu` | Runs a CPU workload for 30 seconds |

The unit configures automatic restarts, restart rate limiting, a 150 MB memory maximum, and a 5% CPU quota.

## Service commands

```bash
sudo systemctl stop testpress
sudo systemctl start testpress
sudo systemctl restart testpress
sudo journalctl -u testpress -n 30 --no-pager
```

Logs are available in journald and `app.log`. Detailed results and explanations are in the experiment notes.
