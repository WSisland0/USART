import unittest

from core.logger import LogCategory, LogEntry
from ui.base_window import _format_log_entry_html, _format_raw_rx_display


class ReceiveDisplayTests(unittest.TestCase):
    def test_empty_data_is_not_displayed(self):
        self.assertIsNone(_format_raw_rx_display(b"", "HEX"))

    def test_ascii_space_falls_back_to_hex(self):
        self.assertEqual(_format_raw_rx_display(b" ", "ASCII"), "20")

    def test_ascii_text_is_displayed_as_text(self):
        self.assertEqual(_format_raw_rx_display(b"OK", "ASCII"), "OK")

    def test_hex_mode_still_displays_hex(self):
        self.assertEqual(_format_raw_rx_display(bytes([0x0D, 0x0A]), "HEX"), "0D 0A")

    def test_rx_arrow_is_escaped_for_html_display(self):
        entry = LogEntry(LogCategory.RX, "EEPROM OK, EmptyFre=5164, DigitalV=138")

        html = _format_log_entry_html(entry, "#388E3C")

        self.assertIn("RX &lt;- EEPROM OK", html)
        self.assertNotIn("RX <- EEPROM OK", html)


if __name__ == "__main__":
    unittest.main()
