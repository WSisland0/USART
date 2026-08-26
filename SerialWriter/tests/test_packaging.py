from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class PackagingCommandTests(unittest.TestCase):
    def test_modern_build_uses_clean_build_and_windows_icon(self):
        instructions = (PROJECT_ROOT / "编译.txt").read_text(encoding="utf-8")
        modern_name = '--name "SerialWriter-现代风"'

        self.assertIn(modern_name, instructions)
        modern_command = next(
            line for line in instructions.splitlines() if modern_name in line
        )
        self.assertIn("--clean", modern_command)
        self.assertIn('--icon "assets/serial_writer.ico"', modern_command)
        self.assertIn('--add-data "assets;assets"', modern_command)


if __name__ == "__main__":
    unittest.main()
