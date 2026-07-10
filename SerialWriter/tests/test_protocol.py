import unittest

from core.protocol import (
    ResponseParser,
    build_frame,
    format_response,
    to_hex_string,
)


class ProtocolTests(unittest.TestCase):
    def test_build_frame_uses_simplified_a55a_protocol(self):
        frame = build_frame(55, seq=1)

        self.assertEqual(frame, bytes([0xA5, 0x5A, 0x01, 0x37, 0x41, 0xF6]))
        self.assertEqual(to_hex_string(frame), "A5 5A 01 37 41 F6")

    def test_response_parser_restores_emptyfre_and_digitalv(self):
        parser = ResponseParser()
        response_frame = bytes([
            0xA5, 0x5A,
            0x01,
            0x00,
            0xC4, 0x09,
            0x37,
            0x1F, 0xBB,
        ])

        responses = parser.feed(response_frame)

        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0].seq, 1)
        self.assertEqual(responses[0].status, 0)
        self.assertEqual(responses[0].empty_fre, 2500)
        self.assertEqual(responses[0].digital_v, 55)
        self.assertEqual(
            format_response(responses[0]),
            "EEPROM OK, EmptyFre=2500, DigitalV=55",
        )

    def test_response_parser_handles_noise_and_partial_frames(self):
        parser = ResponseParser()
        responses = parser.feed(bytes([0x00, 0xA5, 0x5A, 0x02, 0x00]))

        self.assertEqual(responses, [])
        self.assertTrue(parser.has_pending_data)

        responses = parser.feed(bytes([0xC4, 0x09, 0x37, 0x5B, 0xBB]))

        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0].seq, 2)
        self.assertEqual(responses[0].empty_fre, 2500)
        self.assertEqual(responses[0].digital_v, 55)
        self.assertFalse(parser.has_pending_data)

    def test_response_parser_drops_bad_crc_frame(self):
        parser = ResponseParser()
        bad_crc_frame = bytes([
            0xA5, 0x5A,
            0x01,
            0x00,
            0xC4, 0x09,
            0x37,
            0x00, 0x00,
        ])

        self.assertEqual(parser.feed(bad_crc_frame), [])


if __name__ == "__main__":
    unittest.main()
