import ast
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import i18n
import spotify_api
import spotify_volume_lock
import launcher
from app_paths import data_root
from spotify_volume_lock import Controller
from terminal_ui import ControlMenu, TerminalUI


class FakeAPI:
    def __init__(self):
        self.current = 40
        self.sent = []
        self.apply = True

    def device(self):
        return {'id': 'this-pc', 'name': 'PC', 'volume_percent': self.current}

    def set_volume(self, device, target):
        self.sent.append((device, target))
        if self.apply:
            self.current = target


class AppTests(unittest.TestCase):
    def setUp(self):
        i18n.set_language('it')

    def tearDown(self):
        i18n.set_language('it')

    def test_all_translated_calls_have_english_messages(self):
        root = Path(__file__).resolve().parents[1]
        for filename in ('spotify_api.py', 'spotify_volume_lock.py', 'terminal_ui.py', 'launcher.py'):
            tree = ast.parse((root / filename).read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'tr':
                    if node.args and isinstance(node.args[0], ast.Constant):
                        self.assertIn(node.args[0].value, i18n.ENGLISH, (filename, node.lineno))

    def test_language_selection_and_previous_choice(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(i18n, 'ROOT', Path(directory)), \
                patch('builtins.print'), patch('builtins.input', side_effect=['bad', '2', '']):
            self.assertEqual(i18n.choose_language(), 'en')
            self.assertEqual(i18n.choose_language(), 'en')
            self.assertEqual(i18n.tr('Scegli volume fisso'), 'Choose fixed volume')

    def test_client_id_survives_cancelled_login(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(spotify_api, 'ROOT', Path(directory)), \
                patch('builtins.input', return_value='a' * 32), patch('builtins.print'), \
                patch.object(spotify_api, 'authorize', side_effect=spotify_api.ApiError('cancelled')):
            with self.assertRaises(spotify_api.ApiError):
                spotify_api.configure()
            self.assertEqual(spotify_api.saved_client_id(), 'a' * 32)

    def configure_fixture(self, directory):
        folder = Path(directory)
        (folder / 'client.json').write_text(json.dumps({'client_id': 'a' * 32}), encoding='utf-8')
        return {'id': 'local', 'name': 'THIS-PC', 'type': 'Computer', 'volume_percent': 67,
                'supports_volume': True}

    def test_automatic_local_pc_selection_without_input(self):
        with tempfile.TemporaryDirectory() as directory:
            device = self.configure_fixture(directory)
            with patch.object(spotify_api, 'ROOT', Path(directory)), patch('builtins.print'), \
                    patch('builtins.input', side_effect=AssertionError('No input expected')), \
                    patch.dict(os.environ, {'COMPUTERNAME': 'this-pc'}), \
                    patch.object(spotify_api, 'authorize', return_value={'access_token': 'mock'}), \
                    patch.object(spotify_api.SpotifyAPI, 'devices', return_value=[device]), \
                    patch.object(spotify_api.SpotifyAPI, 'save_token'):
                spotify_api.configure()
            config = json.loads((Path(directory) / 'config.json').read_text())
            self.assertEqual(config['device_id'], 'local')

    def test_manual_selection_has_clear_english_instructions(self):
        i18n.set_language('en')
        with tempfile.TemporaryDirectory() as directory:
            device = self.configure_fixture(directory)
            output = io.StringIO()
            with patch.object(spotify_api, 'ROOT', Path(directory)), patch('sys.stdout', output), \
                    patch('builtins.input', side_effect=['D', '1']), \
                    patch.dict(os.environ, {'COMPUTERNAME': 'different-name'}), \
                    patch.object(spotify_api, 'authorize', return_value={'access_token': 'mock'}), \
                    patch.object(spotify_api.SpotifyAPI, 'devices', return_value=[device]), \
                    patch.object(spotify_api.SpotifyAPI, 'save_token'):
                spotify_api.configure()
            text = output.getvalue()
            self.assertIn('TYPE the number', text)
            self.assertIn('press ENTER', text)
            self.assertIn('No clicking is needed', text)
            self.assertIn('Invalid choice', text)
            self.assertIn('Opening the control panel', text)
            self.assertNotIn('Collegamento', text)

    def test_control_panel_rendering_in_both_languages(self):
        from rich.console import Console
        for language, label in [('it', 'Scegli volume fisso'), ('en', 'Choose fixed volume')]:
            i18n.set_language(language)
            output = io.StringIO()
            console = Console(file=output, width=80, height=30, color_system=None)
            ui = TerminalUI(console=console, keyboard=object())
            ui.update(70, 70, True, True, False)
            ui.menu.handle('v', 70, True)
            console.print(ui.render())
            text = output.getvalue()
            self.assertIn(label, text)
            if language == 'en':
                self.assertIn('Enter confirms', text)
                self.assertNotIn('Invio', text)
                self.assertNotIn('Modalità', text)

    def test_explicit_command_and_confirmation(self):
        api = FakeAPI()
        controller = Controller(api)
        controller.tick()
        controller.command(('volume', 70, True))
        controller.tick()
        self.assertEqual(api.sent, [('this-pc', 70)])
        self.assertIsNotNone(controller.pending)
        controller.tick()
        self.assertIsNone(controller.pending)
        self.assertIn('confermato', controller.status)

    def test_failed_command_does_not_repeat_forever(self):
        api = FakeAPI()
        api.apply = False
        controller = Controller(api)
        controller.command(('volume', 80, True))
        controller.tick()
        controller.pending = (80, time.monotonic() - 20)
        controller.tick()
        controller.tick()
        self.assertEqual(len(api.sent), 1)
        self.assertTrue(controller.blocked)

    def test_interactive_mode_requires_qualified_input(self):
        api = FakeAPI()
        controller = Controller(api)
        controller.tick()
        controller.input(True, True)
        api.current = 65
        controller.tick()
        self.assertEqual(controller.target, 65)
        controller.input(False, False)
        api.current = 10
        controller.tick()
        self.assertEqual(api.current, 65)

    def test_volume_input_and_limits_in_english(self):
        i18n.set_language('en')
        menu = ControlMenu()
        self.assertEqual(menu.handle('+', 99, True), ('volume', 100, True))
        menu.handle('f', 80, False)
        for character in '999':
            menu.handle(character, 80, False)
        self.assertIsNone(menu.handle('\r', 80, False))
        self.assertEqual(menu.message, 'Enter a number from 0 to 100.')

    def test_launcher_passes_language_without_second_selector(self):
        with patch.object(launcher, 'choose_language', return_value='en'), \
                patch.object(launcher.os, 'name', 'nt'), \
                patch.object(sys, 'argv', ['launcher.py', '--setup']), \
                patch.object(spotify_volume_lock, 'main', return_value=0) as run:
            self.assertEqual(launcher.main(), 0)
            self.assertIn('--configura', sys.argv)
            self.assertEqual(sys.argv[-2:], ['--lang', 'en'])
            run.assert_called_once()

    def test_frozen_settings_persist_beside_executable(self):
        executable = str(Path(__file__).resolve().parent / 'SpotifyVolumeLock.exe')
        with patch.object(sys, 'frozen', True, create=True), patch.object(sys, 'executable', executable):
            self.assertEqual(data_root(), Path(executable).parent)

    def test_reconnect_command_uses_same_launcher(self):
        self.assertEqual(ControlMenu().handle('r', 70, True), ('setup',))
        with patch.object(launcher, 'choose_language', return_value='en'), \
                patch.object(launcher.os, 'name', 'nt'), \
                patch.object(sys, 'argv', ['launcher.py']), \
                patch.object(spotify_volume_lock, 'main', side_effect=[2, 0]) as run:
            self.assertEqual(launcher.main(), 0)
            self.assertEqual(run.call_count, 2)
            self.assertIn('--configura', sys.argv)


if __name__ == '__main__':
    unittest.main()
