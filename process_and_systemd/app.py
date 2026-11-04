from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import logging
import mmap
import os
import signal
import sys
import threading
import time

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (PID %(process)d) %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("app")

CPU_LOAD_SECONDS = 30
MEMORY_LOAD_MB = 256
MEMORY_LOAD_SECONDS = 30


def log_heartbeat(stop_event):
    while not stop_event.wait(5):
        logger.info("Heartbeat: application is running")


def load_cpu():
    logger.info("CPU load started")
    deadline = time.time() + CPU_LOAD_SECONDS
    while time.time() < deadline:
        for i in range(10000):
            i * i
    logger.info("CPU load finished")


def load_memory():
    logger.info(f"Memory load started ({MEMORY_LOAD_MB} MB)")
    # mmap with MAP_POPULATE forces the kernel to immediately commit all physical
    # pages, without needing a CPU-intensive touch loop (not affected by CPUQuota)
    mem = mmap.mmap(-1, MEMORY_LOAD_MB * 1024 * 1024, mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS | mmap.MAP_POPULATE)
    time.sleep(MEMORY_LOAD_SECONDS)
    mem.close()
    logger.info("Memory load finished")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        if self.path == "/hello":
            self.respond(200, "Hello World!\n")

        elif self.path == "/health":
            self.respond(200, "OK\n")

        elif self.path == "/load/cpu":
            threading.Thread(target=load_cpu, daemon=True).start()
            self.respond(200, "CPU load started\n")

        elif self.path == "/load/memory":
            threading.Thread(target=load_memory, daemon=True).start()
            self.respond(200, "Memory load started\n")

        elif self.path == "/crash":
            self.respond(500, "Crashing application now...\n")
            logger.error("Fatal unexpected application crash triggered via /crash endpoint")
            logger.error(
                'Traceback (most recent call last):\n  File "app.py", line 58, in do_GET\n    raise RuntimeError("Unhandled fatal crash: database connection failed")\nRuntimeError: Unhandled fatal crash: database connection failed'
            )
            time.sleep(0.1)
            os._exit(1)

        else:
            self.respond(404, "Not Found\n")

    def respond(self, status, message):
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode())
        self.wfile.flush()


def shutdown(signum, frame):
    sig_name = signal.Signals(signum).name
    logger.info(f"Received {sig_name}, shutting down...")
    raise SystemExit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python HTTP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind (default: 0.0.0.0)")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to listen on (default: 8000)")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), Handler)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    logger.info(f"Server running on {args.host}:{args.port}")
    heartbeat_stop = threading.Event()
    heartbeat_thread = threading.Thread(
        target=log_heartbeat, args=(heartbeat_stop,), daemon=True
    )
    try:
        heartbeat_thread.start()
        server.serve_forever()
    finally:
        heartbeat_stop.set()
        heartbeat_thread.join()
        server.server_close()
        logger.info("Application shutdown complete.")
