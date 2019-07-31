import bitstring
import json
import copy
from collections import deque
from scte.Scte104.SpliceEvent import SpliceEvent

from st291.ST291_enums import VALS, DID_SDID

byte_size = 8

RTP = "Real-Time Transport Protocol"
ST211040 = "SMPTE 2110-40 Data"

class ST291RTPPayloadData:
    def __init__(self, bitarray_data, init_dict=None):
        self.payload_descriptors = deque()

        values_dict = {}
        message_dict = {}

        # Very rough RTP dissection
        values_dict[RTP] = {
            "Version": bitarray_data.read("uint:2"),
            "Padding": bitarray_data.read("bool:1"),
            "Extension": bitarray_data.read("bool:1"),
            "Contributing source identifiers count": bitarray_data.read("uint:4"),
            "Marker": bitarray_data.read("bool:1"),
            "Payload type": bitarray_data.read("uint:7"),
            "Sequence Number": bitarray_data.read("uint:16"),
            "Timestamp": bitarray_data.read("uint:32"),
            "Synchronization Source identifier": hex(bitarray_data.read("uint:32"))
        }

        values_dict[ST211040] = self.dissect_values(bitarray_data)
        message_dict = self.extract_explanations(values_dict)

        self.raw_data = bitarray_data
        self.values = values_dict
        self.explanations = message_dict

    def extract_explanations(self, values_dict):
        message_dict = copy.deepcopy(values_dict)

        message_dict[ST211040]["F"] = "(" + str(message_dict[ST211040]["F"]) + ") " + VALS["F"][values_dict[ST211040]["F"]]

        for i in range(0, values_dict[ST211040]["ANC Count"]):

            DID = int(values_dict[ST211040]["Packets"][i]["DID"], 0)
            SDID = int(values_dict[ST211040]["Packets"][i]["SDID"], 0)

            for title, value in values_dict[ST211040]["Packets"][i].items():
                if title in VALS and value in VALS[title]:
                    message_dict[ST211040]["Packets"][i][title] = "(" + str(message_dict[ST211040]["Packets"][i][title]) + ") " + VALS[title][value]

            UDW_str = values_dict[ST211040]["Packets"][i]["UDW"]
            self.payload_descriptors.append(UDW_str[:4])
            message_dict[ST211040]["Packets"][i]["UDW"] = self.get_UDW_info(DID, SDID, "0x" + UDW_str[4:])

        return message_dict

    def get_UDW_info(self, DID, SDID, UDW):
        # Check if SCTE 104

        if DID == 0x41 and SDID == 0x07:
            bitarray_data = bitstring.BitString(UDW)
            event = SpliceEvent(bitarray_data)

            return event.to_dict()

        return UDW

    def get_UDW_bit_array(self, DID, SDID, UDW):
        payload_descriptor = ""

        if self.payload_descriptors:
            payload_descriptor = self.payload_descriptors.popleft()

        if isinstance(UDW, str):
            UDW_bin = bitstring.BitArray(UDW)
            UDW_bin.prepend(payload_descriptor)

            return UDW_bin

        if DID == 0x41 and SDID == 0x07:
            event = SpliceEvent(None, init_dict=UDW)
            event_bin = event.to_binary()

            event_bin.prepend(payload_descriptor)
            return event_bin

    def dissect_values(self, bitarray_data):
        values_dict = {
            "Extended Sequence Number": hex(bitarray_data.read("uint:16")),
            "Length": bitarray_data.read("uint:16")
        }

        values_dict["ANC Count"] = bitarray_data.read("uint:8")
        values_dict["F"] = bitarray_data.read("uint:2")

        self.offset_reader(bitarray_data, 22)

        values_dict["Packets"] = []

        for i in range(0, values_dict["ANC Count"]):

            values_dict["Packets"].append({
                "C": bitarray_data.read("uint:1"),
                "Line Number": bitarray_data.read("uint:11"),
                "Horizontal Offset": bitarray_data.read("uint:12"),
                "S": bitarray_data.read("uint:1"),
                "StreamNum": bitarray_data.read("uint:7")
            })

            # Offset for parity bits
            self.offset_reader(bitarray_data, 2)
            values_dict["Packets"][i]["DID"] = hex(bitarray_data.read("uint:8"))

            # Offset for parity bits
            self.offset_reader(bitarray_data, 2)
            values_dict["Packets"][i]["SDID"] = hex(bitarray_data.read("uint:8"))

            # Offset for parity bits
            self.offset_reader(bitarray_data, 2)
            values_dict["Packets"][i]["Data Count"] = bitarray_data.read("uint:8")

            UDW_word_count = values_dict["Packets"][i]["Data Count"]
            UDW = "0x"

            for _ in range(UDW_word_count):
                self.offset_reader(bitarray_data, 2)
                word = bitarray_data.read("hex:8")
                UDW += word

            values_dict["Packets"][i]["UDW"] = UDW

            # First bit of checksum word is an inverse bit
            self.offset_reader(bitarray_data, 1)
            values_dict["Packets"][i]["Checksum Word"] = hex(bitarray_data.read("uint:9"))

            UDW_bit_count = UDW_word_count * 10
            word_align = 32 - ((UDW_bit_count - 2 + 10) % 32)
            values_dict["Packets"][i]["Word Align"] = str(len(bitarray_data.read("bin:" + str(word_align)))) + " bits"

            DID = int(values_dict["Packets"][i]["DID"], 0)
            SDID = int(values_dict["Packets"][i]["SDID"], 0)

            if (DID in DID_SDID):
                if SDID in DID_SDID[DID]:
                    values_dict["Packets"][i]["Packet Info"] = DID_SDID[DID][SDID]
                else:
                    values_dict["Packets"][i]["Packet Info"] = DID_SDID[DID]
            else:
                values_dict["Packets"][i]["Packet Info"] = ""


        return values_dict

    def offset_reader(self, bitarray_data, bit_offset):
        bitarray_data.pos += bit_offset

    def print(self):
        print(str(self))

    def __str__(self):
        return(json.dumps(self.to_dict(), indent=4, sort_keys=False))

    def to_dict(self):
        return copy.deepcopy(self.explanations)

    def print_values(self):
        print(json.dumps(self.get_values_dict(), indent=4, sort_keys=False))

    def get_values_dict(self):
        return copy.deepcopy(self.values)

    def to_binary(self):
        binary_str = ""

        RTP_Data = self.values[RTP]
        version = RTP_Data["Version"]
        padding = RTP_Data["Padding"]
        extension = RTP_Data["Extension"]
        csi_count = RTP_Data["Contributing source identifiers count"]
        marker = RTP_Data["Marker"]
        payload_type = RTP_Data["Payload type"]
        seq_num = RTP_Data["Sequence Number"]
        timestamp = RTP_Data["Timestamp"]
        sync_source_id = int(RTP_Data["Synchronization Source identifier"], 0)

        binary_str += self.int_to_bin(version, 2)
        binary_str += self.bool_to_bin(padding)
        binary_str += self.bool_to_bin(extension)
        binary_str += self.int_to_bin(csi_count, 4)
        binary_str += self.bool_to_bin(marker)
        binary_str += self.int_to_bin(payload_type, 7)
        binary_str += self.int_to_bin(seq_num, 16)
        binary_str += self.int_to_bin(timestamp, 32)
        binary_str += self.int_to_bin(sync_source_id, 32)

        ST291_data = copy.deepcopy(self.values[ST211040])
        ext_seq_num = int(ST291_data["Extended Sequence Number"], 0)
        f = ST291_data["F"]

        binary_str += self.int_to_bin(ext_seq_num, 16)

        anc_count = 0
        length = 0

        for index, packet in enumerate(ST291_data["Packets"]):
            anc_count += 1
            packet_length = 72

            packet["Line Number"] = 0x7FF
            packet["Horizontal Offset"] = 0xFFF
            did = int(packet["DID"], 0)
            sdid = int(packet["SDID"], 0)
            udw_bit_array = self.get_UDW_bit_array(did, sdid, self.explanations[ST211040]["Packets"][index]["UDW"])
            udw_hex = udw_bit_array.hex
            packet["Data Count"] = int(len(udw_hex) / 2)
            packet_length += packet["Data Count"] * 10
            udw_bin = self.convert_8_to_10_bit_words(udw_bit_array)
            packet["UDW"] = udw_bin

            word_align = 32 - ((packet["Data Count"] * 10 - 2 + 10) % 32)
            packet_length += word_align
            packet["Word Align"] = '0' * int(word_align)

            length += packet_length / 8

        binary_str += self.int_to_bin(int(length), 16)
        binary_str += self.int_to_bin(anc_count, 8)
        binary_str += self.int_to_bin(f, 2)
        binary_str += '0' * 22

        for index, packet in enumerate(ST291_data["Packets"]):
            c = packet["C"]
            line_num = packet["Line Number"]
            horiz_offset = packet["Horizontal Offset"]
            s = packet["S"]
            stream_num = packet["StreamNum"]
            did = self.int_to_bin(int(packet["DID"], 0), 8)
            sdid = self.int_to_bin(int(packet["SDID"], 0), 8)
            data_count = self.int_to_bin(packet["Data Count"], 8)
            checksum = int(packet["Checksum Word"], 0)

            binary_str += self.int_to_bin(c, 1)
            binary_str += self.int_to_bin(line_num, 11)
            binary_str += self.int_to_bin(horiz_offset, 12)
            binary_str += self.int_to_bin(s, 1)
            binary_str += self.int_to_bin(stream_num, 7)
            binary_str += self.convert_8_to_10_bit_words(bitstring.BitString(bin=did + sdid + data_count))
            binary_str += packet["UDW"]
            checksum_bin = self.int_to_bin(checksum, 9)
            checksum_parity = "0"

            if checksum_bin[0] == "0":
                checksum_parity = "1"

            binary_str += checksum_parity
            binary_str += checksum_bin
            binary_str += packet["Word Align"]

        return bitstring.BitString(bin=binary_str)

    def convert_8_to_10_bit_words(self, bitarray):
        raw_binary_str = bitarray.bin

        converted = ""

        word = ""
        num_odd = 0
        for i in raw_binary_str:
            if i == '1':
                num_odd = (num_odd + 1) % 2

            word = word + i

            if len(word) == 8:
                num_even = 0

                if num_odd == 0:
                    num_even = 1

                converted = converted + str(num_even) + str(num_odd) + word
                word = ""
                num_odd = 0

        return converted

    def int_to_bin(self, value, num_bits=1):
        raw = bin(value).lstrip("0b")

        num_missing_bits = num_bits - len(raw)

        raw = "0" * num_missing_bits + raw

        return raw

    def bool_to_bin(self, bool_val):
        return self.int_to_bin(int(bool_val))
