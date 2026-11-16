# Linux Hardware Q&A Assistant

A small, read-only CLI that answers basic Linux hardware questions using verified system command output.

## Requirements

- Python 3
- Linux
- `pciutils` and `util-linux`

The assistant uses only fixed commands: `lscpu`, `/proc/meminfo`, `lsblk`, and `lspci`.
It never passes user input to a shell and does not modify the system.

## Run on Linux

Open a terminal in this directory and install the required system tools:

```bash
sudo apt update
sudo apt install python3 pciutils util-linux
```

Run a question directly:

```bash
python3 hardware_assistant.py "What CPU do I have?"
python3 hardware_assistant.py "How much RAM is available?"
python3 hardware_assistant.py "What disks are installed?"
python3 hardware_assistant.py "What GPU do I have?"
```
 
