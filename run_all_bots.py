import asyncio
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def enabled(var_name: str, default: str = "1") -> bool:
    return os.getenv(var_name, default).strip() in {"1", "true", "True", "yes", "on"}


async def stream_output(prefix: str, stream: asyncio.StreamReader):
    while True:
        line = await stream.readline()
        if not line:
            break
        print(f"[{prefix}] {line.decode(errors='replace').rstrip()}")


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
    bots = []

    if enabled("RUN_GORILLA", "1"):
        bots.append(("gorilla", ROOT / "Gorilla_bot" / "bot.py"))

    if enabled("RUN_GONKAAI", "1"):
        bots.append(("gonkaai", ROOT / "gonkaai" / "bot.py"))

    if enabled("RUN_LIFEKEY", "1"):
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

    try:
        await asyncio.gather(*(proc.wait() for _, proc, _ in running))
    except KeyboardInterrupt:
        print("Stopping all bots...")
        for _, proc, _ in running:
            if proc.returncode is None:
                proc.terminate()
        await asyncio.gather(*(proc.wait() for _, proc, _ in running), return_exceptions=True)
    finally:
        for _, _, out in running:
            out.cancel()


if __name__ == "__main__":
    asyncio.run(main())
