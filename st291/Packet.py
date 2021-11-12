import bitstring
import json
import copy
from collections import deque
from scte.Scte104.SpliceEvent import SpliceEvent

from st291.ST291_enums import VALS, DID_SDID
from st291.Utilities import convert_8_to_10_bit_words, int_to_bin, offset_reader

# For testing
# from ST291_enums import VALS, DID_SDID
# from Utilities import convert_8_to_10_bit_words, int_to_bin, offset_reader


class Packet:
    def __init__(self, bitarray_data):
        self.payload_descriptor = ""

        self.values_dict = {
            "C": bitarray_data.read("uint:1"),
            "Line Number": bitarray_data.read("uint:11"),
            "Horizontal Offset": bitarray_data.read("uint:12"),
            "S": bitarray_data.read("uint:1"),
            "StreamNum": bitarray_data.read("uint:7")
        }

        # Offset for parity bits
        offset_reader(bitarray_data, 2)
        self.DID = bitarray_data.read("uint:8")

        # Offset for parity bits
        offset_reader(bitarray_data, 2)
        self.SDID = bitarray_data.read("uint:8")

        # Offset for parity bits
        offset_reader(bitarray_data, 2)
        self.word_count = bitarray_data.read("uint:8")

        self.UDW = self.find_UDW_object(bitarray_data)

        # First bit of checksum word is an inverse bit
        offset_reader(bitarray_data, 1)
        self.values_dict["Checksum Word"] = bitarray_data.read("uint:9")

        UDW_bit_count = self.word_count * 10
        word_align = (32 - (UDW_bit_count - 2 + 10)) % 32
        offset_reader(bitarray_data, word_align)

        if (self.DID in DID_SDID):
            if isinstance(DID_SDID[self.DID], str):
                self.values_dict["Packet Info"] = DID_SDID[self.DID]
            elif self.SDID in DID_SDID[self.DID]:
                self.values_dict["Packet Info"] = DID_SDID[self.DID][self.SDID]
        else:
            self.values_dict["Packet Info"] = ""

    def update_UDW_object(self, UDW_object):
        self.UDW = UDW_object

    def find_UDW_object(self, bitarray_data):
        if self.is_scte_104_packet():
            UDW_hex = "0x"

            for _ in range(self.word_count):
                offset_reader(bitarray_data, 2)
                word = bitarray_data.read("hex:8")
                UDW_hex += word

            self.payload_descriptor = UDW_hex[:4]

            return SpliceEvent(bitstring.BitString("0x" + UDW_hex[4:]))
        else:
            UDW_bit_count = self.word_count * 10
            UDW_int = bitarray_data.read("uint:" + str(UDW_bit_count))
            return UDW_int

    def to_dict(self):
        final_dict = copy.deepcopy(self.values_dict)
        final_dict["DID"] = self.DID
        final_dict["SDID"] = self.SDID
        final_dict["Data Count"] = self.word_count

        if isinstance(self.UDW, int):
            final_dict["UDW"] = self.UDW
        else:
            final_dict["UDW"] = self.UDW.to_dict()

        return final_dict

    def to_printable_dict(self):
        printable_dict = copy.deepcopy(self.values_dict)
        printable_dict["DID"] = hex(self.DID)
        printable_dict["SDID"] = hex(self.SDID)
        printable_dict["Data Count"] = self.word_count
        printable_dict["Checksum Word"] = hex(printable_dict["Checksum Word"])

        for title, value in printable_dict.items():
            if title in VALS and value in VALS[title]:
                printable_dict[title] = "(" + str(printable_dict[title]) + ") " + VALS[title][value]

        if isinstance(self.UDW, int):
            ##TODO returns 10-bit words but may want to return 8 bit words
            printable_dict["UDW"] = hex(self.UDW)
        else:
            if self.is_scte_104_packet():
                printable_dict["UDW"] = self.UDW.to_dict(upid_as_str=True)
            else:
                printable_dict["UDW"] = self.UDW.to_dict()
        return printable_dict

    def to_binary(self):
        # self.values_dict["Line Number"] = 0x7FF
        # self.values_dict["Horizontal Offset"] = 0xFFF
        binary_str = ""

        udw_bin = ""

        if not isinstance(self.UDW, int):
            udw_bit_array = self.UDW.to_binary()
            udw_bit_array.prepend(self.payload_descriptor)
            udw_hex = udw_bit_array.hex
            self.word_count = int(len(udw_hex) / 2)
            udw_bin = convert_8_to_10_bit_words(udw_bit_array)
        else:
            udw_bin = int_to_bin(self.UDW, self.word_count * 10)

        c = self.values_dict["C"]
        line_num = self.values_dict["Line Number"]
        horiz_offset = self.values_dict["Horizontal Offset"]
        s = self.values_dict["S"]
        stream_num = self.values_dict["StreamNum"]
        checksum = self.values_dict["Checksum Word"]

        binary_str += int_to_bin(c, 1)
        binary_str += int_to_bin(line_num, 11)
        binary_str += int_to_bin(horiz_offset, 12)
        binary_str += int_to_bin(s, 1)
        binary_str += int_to_bin(stream_num, 7)
        did = int_to_bin(self.DID, 8)
        sdid = int_to_bin(self.SDID, 8)
        data_count = int_to_bin(self.word_count, 8)
        binary_str += convert_8_to_10_bit_words(bitstring.BitString(bin=did + sdid + data_count))
        binary_str += udw_bin
        checksum_bin = int_to_bin(checksum, 9)
        checksum_parity = "0"

        if checksum_bin[0] == "0":
            checksum_parity = "1"

        binary_str += checksum_parity
        binary_str += checksum_bin

        word_align = 32 - ((self.word_count * 10 - 2 + 10) % 32)
        binary_str += '0' * int(word_align)

        return bitstring.BitString(bin=binary_str)

    def get_length(self):
        length = 72
        udw_bin = ""

        if not isinstance(self.UDW, int):
            udw_bit_array = self.UDW.to_binary()
            udw_bit_array.prepend(self.payload_descriptor)
            udw_hex = udw_bit_array.hex
            self.word_count = int(len(udw_hex) / 2)
            udw_bin = convert_8_to_10_bit_words(udw_bit_array)
        else:
            udw_bin = int_to_bin(self.UDW, self.word_count * 10)

        length += len(udw_bin)

        word_align = 32 - ((self.word_count * 10 - 2 + 10) % 32)

        length += word_align

        return length

    def is_scte_104_packet(self):
        return self.DID == 0x41 and self.SDID == 0x07
