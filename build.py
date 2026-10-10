"""Developer tool: build the single Windows executable with PyInstaller."""
import os
from pathlib import Path
import subprocess
import sys

if os.name != 'nt':
    raise SystemExit('Build this executable on Windows.')
root = Path(__file__).resolve().parent
subprocess.run([
    sys.executable, '-m', 'PyInstaller', '--onefile', '--console', '--noupx',
    '--noconfirm', '--name', 'SpotifyVolumeLock', '--distpath', str(root / 'dist'),
    '--workpath', str(root / 'build'), '--specpath', str(root / 'build'),
    str(root / 'launcher.py'),
], cwd=root, check=True)
print(root / 'dist' / 'SpotifyVolumeLock.exe')
