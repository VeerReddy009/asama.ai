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

Run without an argument for interactive mode:

```bash
python3 hardware_assistant.py
```

## Run on Windows with WSL

The hardware queries require Linux commands, so run the assistant inside
Ubuntu/WSL rather than directly from PowerShell.

If WSL is not installed, open PowerShell as Administrator and run:

```powershell
wsl --install -d Ubuntu
```

After restarting, open Ubuntu or run `wsl`, then navigate to the project:

```bash
cd /mnt/c/Users/veerr/Desktop/SOCIAL
sudo apt update
sudo apt install python3 pciutils util-linux
python3 hardware_assistant.py "What GPU do I have?"
```

The prompt should look like `user@computer:...$`. Do not run `sudo apt`
commands at a `PS C:\...>` PowerShell prompt.

WSL may report a Microsoft Basic Render Driver instead of the physical GPU.
This is a limitation of how hardware is exposed to WSL.

## Test

```bash
python3 -m unittest discover -s . -p "test_*.py"
```

The tests use mocked command output and can also be run from PowerShell:

```powershell
py -m unittest discover -s . -p "test_*.py"
```

Missing commands are reported clearly. `dmidecode` and administrator
privileges are intentionally outside this first MVP.