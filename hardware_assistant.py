"""Safe, read-only Linux hardware question assistant."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from typing import Any, Callable


CommandRunner = Callable[[list[str]], str]


def run_command(command: list[str]) -> str:
    """Run one fixed command without invoking a shell."""
    if shutil.which(command[0]) is None:
        raise FileNotFoundError(command[0])
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=5,
        check=True,
        shell=False,
    )
    return result.stdout


def parse_lscpu(output: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in output.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return {
        "model": values.get("Model name", "Unknown"),
        "architecture": values.get("Architecture", "Unknown"),
        "cores": values.get("CPU(s)", "Unknown"),
        "vendor": values.get("Vendor ID", "Unknown"),
    }


def parse_meminfo(output: str) -> dict[str, str]:
    values: dict[str, float] = {}
    for line in output.splitlines():
        match = re.match(r"^(MemTotal|MemAvailable):\s+(\d+)(?:\s+([A-Za-z]+))?", line)
        if match:
            unit = (match.group(3) or "kB").lower()
            multipliers = {"kb": 1, "mb": 1024, "gb": 1024 * 1024}
            if unit in multipliers:
                values[match.group(1)] = int(match.group(2)) * multipliers[unit]

    def to_gb(kib: float | None) -> str:
        return f"{kib / 1024 / 1024:.2f} GB" if kib is not None else "Unknown"

    return {
        "total": to_gb(values.get("MemTotal")),
        "available": to_gb(values.get("MemAvailable")),
    }


def parse_lsblk(output: str) -> dict[str, Any]:
    data = json.loads(output)
    if not isinstance(data, dict) or not isinstance(data.get("blockdevices"), list):
        raise ValueError("lsblk output does not contain a blockdevices list")

    devices = []
    for device in data.get("blockdevices", []):
        if not isinstance(device, dict):
            raise ValueError("lsblk output contains an invalid device entry")
        devices.append(
            {
                "name": device.get("name", "Unknown"),
                "size": device.get("size", "Unknown"),
                "type": device.get("type", "Unknown"),
                "model": device.get("model") or "Unknown",
                "mountpoint": device.get("mountpoint") or "Not mounted",
            }
        )
    return {"devices": devices}


def parse_lspci(output: str) -> dict[str, list[str]]:
    graphics = [
        line.strip()
        for line in output.splitlines()
        if re.search(r"(VGA compatible controller|3D controller|Display controller)", line, re.I)
    ]
    return {"graphics_adapters": graphics}


TOOLS: dict[str, tuple[list[str], Callable[[str], dict[str, Any]]]] = {
    "cpu": (["lscpu"], parse_lscpu),
    "memory": (["cat", "/proc/meminfo"], parse_meminfo),
    "disks": (["lsblk", "-J", "-o", "NAME,SIZE,TYPE,MOUNTPOINT,MODEL"], parse_lsblk),
    "gpu": (["lspci"], parse_lspci),
}


INTENTS: dict[str, tuple[str, ...]] = {
    "cpu": ("cpu", "processor", "core", "cores", "architecture"),
    "memory": ("ram", "memory", "mem"),
    "disks": ("disk", "storage", "ssd", "nvme", "drive"),
    "gpu": ("gpu", "graphics", "graphic", "video card"),
}


def detect_intent(question: str) -> str | None:
    normalized = question.lower()
    matches = [
        intent
        for intent, keywords in INTENTS.items()
        if any(keyword in normalized for keyword in keywords)
    ]
    return matches[0] if len(matches) == 1 else None


def answer_question(question: str, runner: CommandRunner = run_command) -> str:
    intent = detect_intent(question)
    if intent is None:
        return (
            "I can answer questions about your CPU, RAM, disks, and GPU. "
            "Please ask about one hardware category at a time."
        )

    command, parser = TOOLS[intent]
    try:
        data = parser(runner(command))
    except FileNotFoundError as error:
        return f"I cannot check {intent}: the Linux tool '{error.args[0]}' is unavailable."
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        return f"I cannot check {intent}: the system tool failed ({type(error).__name__})."
    except (json.JSONDecodeError, ValueError) as error:
        return f"I cannot parse the {intent} data: {error}."

    return json.dumps({"hardware_type": intent, "data": data}, indent=2)


def main() -> None:
    if len(sys.argv) > 1:
        print(answer_question(" ".join(sys.argv[1:])))
        return

    print("Linux Hardware Assistant. Type 'exit' to quit.")
    while True:
        try:
            question = input("hardware> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"exit", "quit"}:
            break
        if question:
            print(answer_question(question))


if __name__ == "__main__":
    main()