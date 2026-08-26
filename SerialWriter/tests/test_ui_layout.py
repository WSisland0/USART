import os
import sys
import unittest


# 在无显示器的测试环境中也能创建 Qt 窗口。
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QGroupBox, QLabel

import main as app_main
from ui import base_window
from ui.modern_window import ModernWindow


class UiLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv[:1])

    def setUp(self):
        self.window = ModernWindow()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def _show_at(self, width: int, height: int):
        self.window.resize(width, height)
        self.window.show()
        self.app.processEvents()

    def _group(self, title: str) -> QGroupBox:
        return next(
            group
            for group in self.window.findChildren(QGroupBox)
            if group.title() == title
        )

    def test_serial_labels_do_not_expand_away_from_their_controls(self):
        self._show_at(1920, 1080)
        serial_group = self._group("串口设置")
        field_labels = [
            label
            for label in serial_group.findChildren(QLabel)
            if label.text().endswith(":")
        ]

        self.assertEqual(len(field_labels), 6)
        for label in field_labels:
            with self.subTest(label=label.text()):
                unused_width = label.width() - label.sizeHint().width()
                self.assertLessEqual(unused_width, 4)

    def test_controls_keep_readable_heights_when_window_is_short(self):
        self._show_at(900, 500)

        self.assertGreaterEqual(self.window._data_input.height(), 64)
        self.assertGreaterEqual(self.window._btn_send.height(), 50)
        self.assertGreaterEqual(self.window._log_text.height(), 70)

    def test_data_panel_does_not_consume_extra_height_when_maximized(self):
        self._show_at(1920, 1080)

        self.assertLessEqual(self._group("数据设置").height(), 260)

    def test_frame_preview_explains_each_protocol_field(self):
        formatter = getattr(base_window, "_format_frame_description_html", None)
        self.assertIsNotNone(formatter)
        html = formatter(["A5", "5A", "01", "80", "01", "80"])

        for text in ("帧头", "序号", "写入值", "CRC16", "低字节", "高字节"):
            with self.subTest(text=text):
                self.assertIn(text, html)

    def test_log_uses_larger_readable_font(self):
        self._show_at(900, 700)

        self.assertGreaterEqual(self.window._log_text.font().pointSizeF(), 12)

    def test_application_icon_asset_can_be_loaded(self):
        loader = getattr(app_main, "_load_application_icon", None)
        self.assertIsNotNone(loader)
        icon = loader()

        self.assertFalse(icon.isNull())


if __name__ == "__main__":
    unittest.main()
