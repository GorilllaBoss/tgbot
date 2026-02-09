import asyncio
import os
import signal
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_env_file(path: Path):
    if not path.exists():
        return

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def enabled(var_name: str, default: str = "1") -> bool:
    return os.getenv(var_name, default).strip().lower() in {"1", "true", "yes", "on"}


async def stream_output(prefix: str, stream: asyncio.StreamReader):
    try:
        while True:
            line = await stream.readline()
            if not line:
                break
            print(f"[{prefix}] {line.decode(errors='replace').rstrip()}")
    except asyncio.CancelledError:
        return


async def spawn_bot(name: str, script_path: Path):
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        str(script_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(ROOT),
    )
    print(f"[{name}] started pid={proc.pid} ({script_path})")
    output_task = asyncio.create_task(stream_output(name, proc.stdout))
    return proc, output_task


async def main():
    load_env_file(ROOT / ".env")

    bots = []
    if enabled("RUN_GORILLA", "1"):
        bots.append(("gorilla", ROOT / "Gorilla_bot" / "bot.py"))

    if enabled("RUN_GONKAAI", "1"):
        bots.append(("gonkaai", ROOT / "gonkaai" / "bot.py"))

    if enabled("RUN_LIFEKEY", "0"):
        lifekey_entry = os.getenv("LIFEKEY_ENTRY", "lifekey/bot.py")
        bots.append(("lifekey", ROOT / lifekey_entry))

    running = []
    for name, path in bots:
        if not path.exists():
            print(f"[{name}] skipped: entrypoint not found -> {path}")
            continue
        proc, out = await spawn_bot(name, path)
        running.append((name, proc, out))

    if not running:
        print("No bot entrypoints found/enabled. Nothing to run.")
        return

    stop_event = asyncio.Event()

    def _request_stop(*_):
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _request_stop)
        except NotImplementedError:
            pass

    wait_tasks = [asyncio.create_task(proc.wait()) for _, proc, _ in running]
    stop_task = asyncio.create_task(stop_event.wait())
    await asyncio.wait(wait_tasks + [stop_task], return_when=asyncio.FIRST_COMPLETED)

    print("Stopping all bots...")
    for _, proc, _ in running:
        if proc.returncode is None:
            proc.terminate()
    await asyncio.gather(*(proc.wait() for _, proc, _ in running), return_exceptions=True)

    for _, _, out in running:
        out.cancel()
    await asyncio.gather(*(out for _, _, out in running), return_exceptions=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
