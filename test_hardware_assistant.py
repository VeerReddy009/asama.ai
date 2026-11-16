import unittest

from hardware_assistant import (
    answer_question,
    detect_intent,
    parse_lsblk,
    parse_lscpu,
    parse_meminfo,
)


class HardwareAssistantTests(unittest.TestCase):
    def test_detects_hardware_categories(self):
        self.assertEqual(detect_intent("What CPU do I have?"), "cpu")
        self.assertEqual(detect_intent("How much RAM is installed?"), "memory")
        self.assertEqual(detect_intent("Show my SSD disks"), "disks")
        self.assertEqual(detect_intent("Which GPU is installed?"), "gpu")

    def test_rejects_ambiguous_or_unrelated_questions(self):
        self.assertIsNone(detect_intent("Tell me about my CPU and RAM"))
        self.assertIsNone(detect_intent("What is the weather?"))

    def test_parses_cpu_output(self):
        result = parse_lscpu(
            "Architecture: x86_64\nModel name: Example CPU\nCPU(s): 8\nVendor ID: GenuineIntel\n"
        )
        self.assertEqual(result["model"], "Example CPU")
        self.assertEqual(result["cores"], "8")

    def test_parses_memory_output(self):
        result = parse_meminfo("MemTotal:       16777216 kB\nMemAvailable:    8388608 kB\n")
        self.assertEqual(result["total"], "16.00 GB")
        self.assertEqual(result["available"], "8.00 GB")

    def test_parses_memory_output_with_supported_units(self):
        result = parse_meminfo("MemTotal: 16 MB\nMemAvailable: 1 GB\n")
        self.assertEqual(result["total"], "0.02 GB")
        self.assertEqual(result["available"], "1.00 GB")

    def test_rejects_malformed_lsblk_structure(self):
        with self.assertRaises(ValueError):
            parse_lsblk('{"blockdevices": {}}')

    def test_uses_fixed_command_and_formats_result(self):
        commands = []

        def fake_runner(command):
            commands.append(command)
            return "Architecture: x86_64\nModel name: Test CPU\nCPU(s): 4\n"

        response = answer_question("What processor do I have?", fake_runner)
        self.assertEqual(commands, [["lscpu"]])
        self.assertIn('"model": "Test CPU"', response)


if __name__ == "__main__":
    unittest.main()