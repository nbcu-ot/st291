import bitstring
import json
import copy
from collections import deque
from scte.Scte104.SpliceEvent import SpliceEvent

from st291.ST291_enums import VALS, DID_SDID
from st291.Packet import Packet
from st291.Utilities import convert_8_to_10_bit_words, int_to_bin, bool_to_bin, offset_reader

byte_size = 8

RTP = "Real-Time Transport Protocol"
ST211040 = "SMPTE 2110-40 Data"

class ST291RTPPayloadData:
    def __init__(self, bitarray_data, init_dict=None):
        self.packets = []
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

        self.raw_data = bitarray_data
        self.values = values_dict

    def dissect_values(self, bitarray_data):
        values_dict = {
            "Extended Sequence Number": hex(bitarray_data.read("uint:16")),
            "Length": bitarray_data.read("uint:16")
        }

        values_dict["ANC Count"] = bitarray_data.read("uint:8")
        values_dict["F"] = bitarray_data.read("uint:2")

        # Offset for 22 bit reserved field
        offset_reader(bitarray_data, 22)

        for i in range(0, values_dict["ANC Count"]):
            packet = Packet(bitarray_data)
            self.packets.append(packet)

        return values_dict

    def print(self):
        print(str(self))

    def __str__(self):
        return(json.dumps(self.to_dict(), indent=4, sort_keys=False))

    def to_dict(self):
        message_dict = copy.deepcopy(self.values)

        message_dict[ST211040]["F"] = "(" + str(message_dict[ST211040]["F"]) + ") " + VALS["F"][message_dict[ST211040]["F"]]

        message_dict[ST211040]["Packets"] = []

        if self.packets:
            length = 0

            for packet in self.packets:
                length += packet.get_length() / 8
                message_dict[ST211040]["Packets"].append(packet.to_printable_dict())

            message_dict[ST211040]["length"] = length

        return message_dict

    def print_values(self):
        print(json.dumps(self.get_values_dict(), indent=4, sort_keys=False))

    def get_values_dict(self):
        values_dict = copy.deepcopy(self.values)

        values_dict[ST211040]["Packets"] = []

        if self.packets:
            length = 0

            for packet in self.packets:
                length += packet.get_length() / 8
                values_dict[ST211040]["Packets"].append(packet.to_dict())

            values_dict[ST211040]["length"] = length

        return values_dict

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

        binary_str += int_to_bin(version, 2)
        binary_str += bool_to_bin(padding)
        binary_str += bool_to_bin(extension)
        binary_str += int_to_bin(csi_count, 4)
        binary_str += bool_to_bin(marker)
        binary_str += int_to_bin(payload_type, 7)
        binary_str += int_to_bin(seq_num, 16)
        binary_str += int_to_bin(timestamp, 32)
        binary_str += int_to_bin(sync_source_id, 32)

        ST291_data = copy.deepcopy(self.values[ST211040])

        ext_seq_num = int(ST291_data["Extended Sequence Number"], 0)
        f = ST291_data["F"]
        length = 0

        for packet in self.packets:
            length += packet.get_length() / 8

        anc_count = len(self.packets)

        binary_str += int_to_bin(ext_seq_num, 16)
        binary_str += int_to_bin(int(length), 16)
        binary_str += int_to_bin(anc_count, 8)
        binary_str += int_to_bin(f, 2)
        binary_str += '0' * 22

        for packet in self.packets:
            binary_str += packet.to_binary().bin

        return bitstring.BitString(bin=binary_str)
