import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import debug_report


class DebugReportTests(unittest.TestCase):
    def test_offline_check_does_not_contact_spotify(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(debug_report, 'check_device') as check:
                report = debug_report.collect_report(directory)
        check.assert_not_called()
        self.assertEqual(report['configuration']['status'], 'missing')
        self.assertEqual(report['spotify']['status'], 'not_requested')

    def test_report_does_not_include_configuration_values(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            config = {key: 'private-' + key for key in
                      ('client_id', 'device_id', 'device_name')}
            (folder / 'config.json').write_text(json.dumps(config), encoding='utf-8')
            (folder / 'accesso.dat').write_bytes(b'private-token')
            report = debug_report.collect_report(folder)
        serialized = json.dumps(report)
        for value in [*config.values(), 'private-token']:
            self.assertNotIn(value, serialized)
        self.assertTrue(report['configuration']['client_id_present'])

    def test_invalid_configuration_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / 'config.json').write_text('[]', encoding='utf-8')
            report = debug_report.collect_report(directory, online=True)
        self.assertEqual(report['configuration']['status'], 'invalid_structure')
        self.assertEqual(report['spotify']['status'], 'configuration_incomplete')

    def test_device_report_excludes_names_ids_and_tokens(self):
        class FakeAPI:
            def __init__(self, config):
                pass

            def devices(self):
                return [{'id': 'private-id', 'name': 'private-name',
                         'access_token': 'private-token', 'volume_percent': 63,
                         'is_active': True, 'supports_volume': False}]

        import types
        fake_module = types.ModuleType('spotify_api')
        fake_module.SpotifyAPI = FakeAPI
        with patch.dict(sys.modules, {'spotify_api': fake_module}):
            report = debug_report.check_device({'device_id': 'private-id'})
        self.assertEqual(report['volume_percent'], 63)
        self.assertFalse(report['supports_volume'])
        self.assertNotIn('private-', json.dumps(report))


if __name__ == '__main__':
    unittest.main()
