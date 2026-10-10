"""Create a shareable diagnostic report without changing Spotify's volume.

Place this file beside launcher.py (or the EXE and its account settings).
Run: python debug_report.py --lang en
Add --online to check the selected Spotify device using the saved account.
"""

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import sys


MESSAGES = {
    'en': {
        'description': "Create a diagnostic report without changing Spotify's volume.",
        'online': 'Check Spotify using the saved account (may refresh its local token).',
        'saved': 'Report saved as diagnosi_spotify.json beside this script.',
        'failed': 'Could not save the report. Check folder write permissions.',
        'privacy': 'The report excludes tokens, Client ID, device names and device IDs.',
    },
    'it': {
        'description': 'Crea una diagnosi senza cambiare il volume di Spotify.',
        'online': "Controlla Spotify con l'account salvato (può aggiornare il token locale).",
        'saved': 'Diagnosi salvata come diagnosi_spotify.json accanto a questo script.',
        'failed': 'Impossibile salvare la diagnosi. Controlla i permessi della cartella.',
        'privacy': 'La diagnosi esclude token, Client ID, nomi e ID dei dispositivi.',
    },
}


def read_settings(folder):
    """Keep configuration values local; return only presence checks for the report."""
    try:
        config = json.loads((folder / 'config.json').read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {}, {'status': 'missing'}
    except (OSError, ValueError):
        return {}, {'status': 'unreadable_or_invalid_json'}
    if not isinstance(config, dict):
        return {}, {'status': 'invalid_structure'}
    checks = {key + '_present': isinstance(config.get(key), str) and bool(config[key])
              for key in ('client_id', 'device_id', 'device_name')}
    return config, {'status': 'readable', **checks}


def check_device(config):
    from spotify_api import SpotifyAPI

    api = SpotifyAPI(config)
    devices = api.devices()
    selected = next((device for device in devices
                     if device.get('id') == config.get('device_id')), None)
    if selected is None:
        return {'status': 'selected_device_unavailable', 'device_count': len(devices)}
    # Copy only useful measurements, never the API response or account identifiers.
    volume = selected.get('volume_percent')
    return {
        'status': 'selected_device_available',
        'device_count': len(devices),
        'volume_percent': volume if type(volume) in (int, float) else None,
        'active': bool(selected.get('is_active')),
        'restricted': bool(selected.get('is_restricted')),
        'supports_volume': selected.get('supports_volume') is not False,
    }


def collect_report(folder, online=False):
    folder = Path(folder)
    config, settings = read_settings(folder)
    report = {
        'format_version': 1,
        'created_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'runtime': {'windows': os.name == 'nt', 'python': sys.version.split()[0]},
        'files_present': {name: (folder / name).is_file() for name in (
            'launcher.py', 'spotify_api.py', 'spotify_volume_lock.py',
            'terminal_ui.py', 'input_gate.py', 'config.json', 'client.json',
            'accesso.dat', 'preferences.json', 'assets/spotilock.ico',
        )},
        'dependencies_available': {
            name: importlib.util.find_spec(name) is not None
            for name in ('rich', 'psutil')
        },
        'configuration': settings,
        'spotify': {'status': 'not_requested'},
    }
    if online:
        if not all(settings.get(key + '_present') for key in
                   ('client_id', 'device_id', 'device_name')):
            report['spotify'] = {'status': 'configuration_incomplete'}
        elif not (folder / 'accesso.dat').is_file():
            report['spotify'] = {'status': 'authorization_file_missing'}
        elif os.name != 'nt':
            report['spotify'] = {'status': 'requires_windows'}
        else:
            try:
                report['spotify'] = check_device(config)
            except Exception as error:
                # Exception messages can contain URLs or account data; omit them.
                report['spotify'] = {
                    'status': 'connection_failed', 'error_type': type(error).__name__,
                }
    return report


def main(argv=None):
    language_parser = argparse.ArgumentParser(add_help=False)
    language_parser.add_argument('--lang', choices=('it', 'en'), default='en')
    language, _ = language_parser.parse_known_args(argv)
    text = MESSAGES[language.lang]
    parser = argparse.ArgumentParser(description=text['description'])
    parser.add_argument('--lang', choices=('it', 'en'), default='en', help='Italiano / English')
    parser.add_argument('--online', action='store_true', help=text['online'])
    args = parser.parse_args(argv)
    folder = Path(__file__).resolve().parent
    report = collect_report(folder, online=args.online)
    try:
        (folder / 'diagnosi_spotify.json').write_text(
            json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n',
            encoding='utf-8',
        )
    except (OSError, ValueError):
        print(text['failed'])
        return 1
    print(text['saved'])
    print(text['privacy'])
    print('Spotify: ' + report['spotify']['status'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
