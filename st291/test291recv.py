import socket
import struct
import sys
from ST291 import ST291RTPPayloadData
import bitstring
# requires `ip route add 232.0.0.0/8 dev ens1f1` before-hand

MCAST_IP='232.41.101.2'
UDP_PORT = 9001
IF_IP = '6.116.252.21'
server_address = (MCAST_IP, 9001)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

group_bin =  socket.inet_aton(MCAST_IP)
local_bin =  socket.inet_aton(IF_IP) # Which interface to IGMP join on

sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, local_bin)

mreq = struct.pack("4sL", group_bin, socket.INADDR_ANY)
#mreq = group_bin + local_bin # Possible IGMPv3 method

sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

sock.bind(server_address)
while True:
    data, address = sock.recvfrom(1024)

    bitarray_data = bitstring.BitString(data)
    
    my_event = ST291RTPPayloadData(bitarray_data)

    for packet in my_event.to_dict()["SMPTE 2110-40 Data"]["Packets"]:
        did, sdid = packet["DID"], packet["SDID"]

        if not (did == "0x41" and sdid == "0x5") and not (did == "0x60" and sdid == "0x60") and not (did == "0x61" and sdid == "0x1") :
            print('received %s bytes from %s' % (len(data), address))

        
            #my_event.print_values()
            my_event.print()
