import bitstring
import json
import copy
from scte.Scte104.SpliceEvent import SpliceEvent

from ST291_enums import VALS, DID_SDID

byte_size = 8

RTP = "Real-Time Transport Protocol"
ST211040 = "SMPTE 2110-40 Data"

class ST291RTPPayloadData:
    def __init__(self, bitarray_data, init_dict=None):

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

            message_dict[ST211040]["Packets"][i]["UDW"] = self.get_UDW_info(DID, SDID, values_dict[ST211040]["Packets"][i]["UDW"])

        return message_dict

    def get_UDW_info(self, DID, SDID, UDW):
        # Check if SCTE 104

        if DID == 0x41 and SDID == 0x07:
            bitarray_data = bitstring.BitString(UDW)
            event = SpliceEvent(bitarray_data)

            return event.to_dict(upid_as_str=True)

        return UDW

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

            UDW_bit_count = values_dict["Packets"][i]["Data Count"] * 10

            # First two bits of UDW belongs in the previous byte so we offset
            # the reader by 6 bits backwards to include the previous byte
            self.offset_reader(bitarray_data, -6)
            num_bits_to_read = UDW_bit_count + 6

            # Determine if the last bits of UDW trail into the next byte
            overflow = num_bits_to_read % 8
            extra = 0
            if overflow != 0:
                extra = 8 - overflow
                num_bits_to_read += extra

            values_dict["Packets"][i]["UDW"] = hex(bitarray_data.read("uint:" + str(num_bits_to_read)))

            # offset reader back if the next byte was included in UDW
            self.offset_reader(bitarray_data, -1 * extra)

            # First bit of checksum word is an inverse bit
            self.offset_reader(bitarray_data, 1)
            values_dict["Packets"][i]["Checksum Word"] = hex(bitarray_data.read("uint:9"))

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
