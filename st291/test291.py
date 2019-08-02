from ST291 import ST291RTPPayloadData
from ST291_enums import VALS
from Utilities import convert_8_to_10_bit_words
from Packet import Packet
import unittest
import bitstring
from scte.Scte104.SpliceEvent import SpliceEvent


packet_string_1 = "0x00a7880098260442008c250a425080110601208011060120801206013000000000"
packet_test_string_1 = "7fffff0098260442008c250a4250801106012080110601208012060130000000"
packet_test_dict = {
    'C': 0,
    'Line Number': 10,
    'Horizontal Offset': 1928,
    'S': 0,
    'StreamNum': 0,
    'Checksum Word': 304,
    'Packet Info': 'Ancillary Time Code (S12M-2)',
    'DID': 96,
    'SDID': 96,
    'Data Count': 16,
    'UDW': 731532151408787574238337190537472808866183152000}

packet_string_2 = "0x00a000009050793508bfeff8" \
"014c8010177e00802008020340504801" \
"02802004050b80230bfeffbfeff80200" \
"7210187a308c2308c132936418c2308c" \
"2308c2308c2308cd378d630552304dd3" \
"24c9318e5324ca308c10140605405014" \
"05018010b4060f801028020c50000000"

packet_test_string_2 = "7fffff009050793508bfeff8" \
"014c8010177e00802008020340504801" \
"02802004050b80230bfeffbfeff80200" \
"7210187a308c2308c132936418c2308c" \
"2308c2308c2308cd378d630552304dd3" \
"24c9318e5324ca308c10140605405014" \
"05018010b4060f801028020c50000000"


class TestPacket(unittest.TestCase):

    def test_8_to_10(self):
        bin_str = "01011010"
        bitarray_data = bitstring.BitString(bin=bin_str)
        test_bin_str = "1001011010"
        self.assertEqual(convert_8_to_10_bit_words(bitarray_data), test_bin_str)

    def test_packet_init(self):
        packet_bits_1 = bitstring.BitString(packet_string_1)
        packet = Packet(packet_bits_1)
        self.assertEqual(packet.DID, packet_test_dict["DID"])
        self.assertEqual(packet.SDID, packet_test_dict["SDID"])
        self.assertEqual(packet.word_count, packet_test_dict["Data Count"])
        self.assertEqual(packet.UDW, packet_test_dict["UDW"])

        packet_bits_2 = bitstring.BitString(packet_string_2)
        packet = Packet(packet_bits_2)
        self.assertEqual(packet.to_binary().hex, packet_test_string_2)
        self.assertIsInstance(packet.UDW, SpliceEvent)

    def test_packet_binary(self):
        packet_bits_1 = bitstring.BitString(packet_string_1)
        packet = Packet(packet_bits_1)
        self.assertEqual(packet.to_binary().hex, packet_test_string_1)

        packet_bits_2 = bitstring.BitString(packet_string_2)
        packet = Packet(packet_bits_2)
        self.assertEqual(packet.to_binary().hex, packet_test_string_2)

    def test_packet_dict(self):
        packet_bits_1 = bitstring.BitString(packet_string_1)
        packet = Packet(packet_bits_1)
        self.assertEqual(packet.to_dict(), packet_test_dict)

    def test_packet_printable_dict(self):
            packet_test_printable_dict = {
                'C': "(0) " + VALS["C"][0],
                'Line Number': 10,
                'Horizontal Offset': 1928,
                'S': "(0) " + VALS["S"][0],
                'StreamNum': 0,
                'Checksum Word': "0x130",
                'Packet Info': 'Ancillary Time Code (S12M-2)',
                'DID': "0x60",
                'SDID': "0x60",
                'Data Count': 16,
                'UDW': 731532151408787574238337190537472808866183152000}
            packet_bits_1 = bitstring.BitString(packet_string_1)
            packet = Packet(packet_bits_1)
            self.assertEqual(packet.to_printable_dict(), packet_test_printable_dict)


hex_string="0x8064b206bd50bf96000000005c36008c" \
"0200000000a7880098260442008c250a" \
"42508011060120801106012080120601" \
"3000000000a000009050793508bfeff8" \
"014c8010177e00802008020340504801" \
"02802004050b80230bfeffbfeff80200" \
"7210187a308c2308c132936418c2308c" \
"2308c2308c2308cd378d630552304dd3" \
"24c9318e5324ca308c10140605405014" \
"05018010b4060f801028020c50000000"

test_hex_str = "8064b206bd50bf96000000005c36008c" \
"020000007fffff0098260442008c250a" \
"42508011060120801106012080120601" \
"300000007fffff009050793508bfeff8" \
"014c8010177e00802008020340504801" \
"02802004050b80230bfeffbfeff80200" \
"7210187a308c2308c132936418c2308c" \
"2308c2308c2308cd378d630552304dd3" \
"24c9318e5324ca308c10140605405014" \
"05018010b4060f801028020c50000000"

class TestST291(unittest.TestCase):

    def test_st291_binary(self):
        bitarray_data = bitstring.BitString(hex_string)
        my_event = ST291RTPPayloadData(bitarray_data)
        test = my_event.to_binary()

        self.assertEqual(test.hex, test_hex_str)



if __name__ == '__main__':
    unittest.main()
