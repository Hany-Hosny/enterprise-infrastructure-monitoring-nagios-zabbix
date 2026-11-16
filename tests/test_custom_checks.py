import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_plugin(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


memory = load_plugin("check_memory", "files/plugins/check_memory.py")
zabbix_api = load_plugin("check_zabbix_api", "files/plugins/check_zabbix_api.py")


class MemoryPluginTests(unittest.TestCase):
    def test_ok_threshold(self):
        sample = "MemTotal: 1000 kB\nMemAvailable: 300 kB\n"
        status, output = memory.evaluate(sample, 80, 90)
        self.assertEqual(status, memory.OK)
        self.assertIn("70.0%", output)

    def test_warning_and_critical_boundaries(self):
        warning_sample = "MemTotal: 1000 kB\nMemAvailable: 200 kB\n"
        critical_sample = "MemTotal: 1000 kB\nMemAvailable: 100 kB\n"
        self.assertEqual(memory.evaluate(warning_sample, 80, 90)[0], memory.WARNING)
        self.assertEqual(memory.evaluate(critical_sample, 80, 90)[0], memory.CRITICAL)

    def test_missing_available_memory_is_rejected(self):
        with self.assertRaises(ValueError):
            memory.evaluate("MemTotal: 1000 kB\n", 80, 90)


class ZabbixApiResponseTests(unittest.TestCase):
    def test_version_reader_is_exposed(self):
        self.assertTrue(callable(zabbix_api.read_version))


if __name__ == "__main__":
    unittest.main()
