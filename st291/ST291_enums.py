F_VALS = {
    0: "Field: unspecified or progressive scan",
    1: "Field: not valid",
    2: "Field 1",
    3: "Field 2"
}

C_VALS = {
    0: "Either Luma (Y) data channel, SD signal, or no specific channels",
    1: "Color-difference data channel"
}

S_VALS = {
    0: "StreamNum not used",
    1: "StreamNum used"
}

# Special Line_Number Values
# +-------------+------------------------------------------------------+
# | Line_Number | ANC data packet generic vertical location            |
# +-------------+------------------------------------------------------+
# |   0x7FF     | Without specific line location within the field or   |
# |             | frame                                                |
# |             |                                                      |
# |   0x7FE     | On any line in the range from the second line after  |
# |             | the line specified for switching, as defined in SMPTE|
# |             | RP 168 [RP168], to the last line before active video,|
# |             | inclusive                                            |
# |             |                                                      |
# |   0x7FD     | On a line number larger than can be represented in 11|
# |             | bits of this field (if needed for future formats)    |
# +-------------+------------------------------------------------------+
LINE_NUM_VALS = {
    2047: "No specific line location",
    2046: "On any line from the second line after the switching line to the last line before active video",
    2045: "On a line number larger than 11 bits can represent"
}

# Special Horizontal Offset values listed below for potential future addition
# +-------------+--------------------------------------------------------+
# | Horizontal_ | ANC data packet generic horizontal location            |
# | Offset      |                                                        |
# +-------------+--------------------------------------------------------+
# |   0xFFF     | Without specific horizontal location                   |
# |             |                                                        |
# |   0xFFE     | Within horizontal ancillary data space (HANC) as       |
# |             | defined in SMPTE ST 291-1 [ST291]                      |
# |             |                                                        |
# |   0xFFD     | Within the ancillary data space located between SAV    |
# |             | (Start of Active Video) and EAV (End of Active Video)  |
# |             | markers of the serial digital interface                |
# |             |                                                        |
# |   0xFFC     | Horizontal offset is larger than can be represented in |
# |             | the 12 bits of this field (if needed for future        |
# |             | formats or for certain low frame rate 720p formats)    |
# +-------------+--------------------------------------------------------+
HO_VALS = {
    4095: "No specific horizontal location",
    4094: "Within horizontal ancillary data space",
    4093: "Withing ANC data space between SAV and EAV markers",
    4092: "Horizontal offset is larger than 12 bits can represent"
}

VALS = {
    "F": F_VALS,
    "C": C_VALS,
    "Line Number": LINE_NUM_VALS,
    "Horizontal Offset": HO_VALS,
    "S": S_VALS
}

# Taken from https://github.com/FOXNEOAdvancedTechnology/smpte2110-40-dissector/blob/master/ST2110-40.lua
# DID / SDID info from https://smpte-ra.org/smpte-ancillary-data-smpte-st-291 as per 7 Feb 2017

DID_SDID={}

DID_SDID[0x08]={}
DID_SDID[0x40]={}
DID_SDID[0x41]={}
DID_SDID[0x43]={}
DID_SDID[0x44]={}
DID_SDID[0x45]={}
DID_SDID[0x46]={}
DID_SDID[0x50]={}
DID_SDID[0x51]={}
DID_SDID[0x60]={}
DID_SDID[0x61]={}
DID_SDID[0x62]={}
DID_SDID[0x64]={}

DID_SDID[0x00]="Undefined data deleted, (Deprecated; revision of ST291-2010) (S291)"
DID_SDID[0x80]="Packet marked for deletion (S291)"
DID_SDID[0x84]="End packet deleted  (Deprecated; revision of ST291-2010) (S291)"
DID_SDID[0x88]="Start packet deleted (Deprecated; revision of ST291-2010) (S291)"
DID_SDID[0xA0]="Audio data in HANC space (3G) - Group 8 Control pkt (ST 299-2)"
DID_SDID[0xA1]="Audio data in HANC space (3G) - Group 7 Control pkt (ST 299-2)"
DID_SDID[0xA2]="Audio data in HANC space (3G) - Group 6 Control pkt (ST 299-2)"
DID_SDID[0xA3]="Audio data in HANC space (3G- Group 5 Control pkt) (ST 299-2)"
DID_SDID[0xA4]="Audio data in HANC space (3G) - Group 8 (ST 299-2)"
DID_SDID[0xA5]="Audio data in HANC space (3G) - Group 7 (ST 299-2)"
DID_SDID[0xA6]="Audio data in HANC space (3G) - Group 6 (ST 299-2)"
DID_SDID[0xA7]="Audio data in HANC space (3G)- Group 5 (ST 299-2)"
DID_SDID[0xE0]="Audio data in HANC space (HDTV) (ST 299-1)"
DID_SDID[0xE1]="Audio data in HANC space (HDTV) (ST 299-1)"
DID_SDID[0xE2]="Audio data in HANC space (HDTV) (ST 299-1)"
DID_SDID[0xE3]="Audio data in HANC space (HDTV) (ST 299-1)"
DID_SDID[0xE4]="Audio data in HANC space (HDTV) (ST 299-1)"
DID_SDID[0xE5]="Audio data in HANC space (HDTV) (ST 299-1)"
DID_SDID[0xE6]="Audio data in HANC space (HDTV) (ST 299-1)"
DID_SDID[0xE7]="Audio data in HANC space (HDTV) (ST 299-1)"
DID_SDID[0xEc]="Audio Data in HANC space (SDTV) (S272)"
DID_SDID[0xEd]="Audio Data in HANC space (SDTV) (S272)"
DID_SDID[0xEe]="Audio Data in HANC space (SDTV) (S272)"
DID_SDID[0xEf]="Audio Data in HANC space (SDTV) (S272)"
DID_SDID[0xF0]="Camera position (HANC or VANC space) (S315)"
DID_SDID[0xF4]="Error Detection and Handling (HANC space) (RP165)"
DID_SDID[0xF8]="Audio Data in HANC space (SDTV) (S272)"
DID_SDID[0xF9]="Audio Data in HANC space (SDTV) (S272)"
DID_SDID[0xFa]="Audio Data in HANC space (SDTV) (S272)"
DID_SDID[0xFB]="Audio Data in HANC space (SDTV) (S272)"
DID_SDID[0xFC]="Audio Data in HANC space (SDTV) (S272)"
DID_SDID[0xFD]="Audio Data in HANC space (SDTV) (S272)"
DID_SDID[0xFE]="Audio Data in HANC space (SDTV) (S272)"
DID_SDID[0xFF]="Audio Data in HANC space (SDTV) (S272)"

DID_SDID[0x08][0x08]="MPEG recoding data, VANC space (S353)"
DID_SDID[0x08][0x0C]="MPEG recoding data, HANC space (S353)"
DID_SDID[0x40][0x01]="SDTI transport in active frame space (S305)"
DID_SDID[0x40][0x02]="HD-SDTI transport in active frame space (S348)"
DID_SDID[0x40][0x04]="Link Encryption Message 1 (S427)"
DID_SDID[0x40][0x05]="Link Encryption Message 2 (S427)"
DID_SDID[0x40][0x06]="Link Encryption Metadata (S427)"
DID_SDID[0x41][0x01]="Payload Identification, HANC space (S352)"
DID_SDID[0x41][0x05]="AFD and Bar Data (S2016-3)"
DID_SDID[0x41][0x06]="Pan-Scan Data (S2016-4)"
DID_SDID[0x41][0x07]="ANSI/SCTE 104 messages (S2010)"
DID_SDID[0x41][0x08]="DVB/SCTE VBI data (S2031)"
DID_SDID[0x41][0x09]="MPEG TS packets in VANC (ST 2056)"
DID_SDID[0x41][0x0A]="Stereoscopic 3D Frame Compatible Packing and Signaling (ST 2068)"
DID_SDID[0x41][0x0B]="Lip Sync data (ST 2064)"
DID_SDID[0x43][0x01]="Structure of inter-station control data conveyed by ancillary data packets (ITU-R BT.1685)"
DID_SDID[0x43][0x02]="Subtitling Distribution packet (SDP) (RDD 8)"
DID_SDID[0x43][0x03]="Transport of ANC packet in an ANC Multipacket (RDD 8)"
DID_SDID[0x43][0x04]="Metadata to monitor errors of audio and video signals on a broadcasting chain ARIB http://www.arib.or.jp/english/html/overview/archives/br/8-TR-B29v1_0-E1.pdf (ARIB TR-B29)"
DID_SDID[0x43][0x05]="Acquisition Metadata Sets for Video Camera Parameters (RDD18)"
DID_SDID[0x44][0x04]="KLV Metadata transport in VANC space (RP214)"
DID_SDID[0x44][0x14]="KLV Metadata transport in HANC space (RP214)"
DID_SDID[0x44][0x44]="Packing UMID and Program Identification Label Data into SMPTE 291M Ancillary Data Packets (RP223)"
DID_SDID[0x45][0x01]="Compressed Audio Metadata (S2020-1)"
DID_SDID[0x45][0x02]="Compressed Audio Metadata (S2020-1)"
DID_SDID[0x45][0x03]="Compressed Audio Metadata (S2020-1)"
DID_SDID[0x45][0x04]="Compressed Audio Metadata (S2020-1)"
DID_SDID[0x45][0x05]="Compressed Audio Metadata (S2020-1)"
DID_SDID[0x45][0x06]="Compressed Audio Metadata (S2020-1)"
DID_SDID[0x45][0x07]="Compressed Audio Metadata (S2020-1)"
DID_SDID[0x45][0x08]="Compressed Audio Metadata (S2020-1)"
DID_SDID[0x45][0x09]="Compressed Audio Metadata (S2020-1)"
DID_SDID[0x46][0x01]="Two Frame Marker in HANC (ST 2051)"
DID_SDID[0x50][0x01]="WSS data per RDD 8 (RDD 8)"
DID_SDID[0x51][0x01]="Film Codes in VANC space (RP215)"
DID_SDID[0x60][0x60]="Ancillary Time Code (S12M-2)"
DID_SDID[0x60][0x61]="Time Code for High Frame Rate Signals (ST 12-3)"
DID_SDID[0x61][0x01]="EIA 708B Data mapping into VANC space (S334-1)"
DID_SDID[0x61][0x02]="EIA 608 Data mapping into VANC space (S334-1)"
DID_SDID[0x62][0x01]="Program Description in VANC space (RP207)"
DID_SDID[0x62][0x02]="Data broadcast (DTV) in VANC space (S334-1)"
DID_SDID[0x62][0x03]="VBI Data in VANC space (RP208)"
DID_SDID[0x64][0x64]="Time Code in HANC space (Deprecated; for reference only) (RP196 (Withdrawn))"
DID_SDID[0x64][0x7F]="VITC in HANC space (Deprecated; for reference only) (RP196 (Withdrawn))"
DID_SDID[0x60][0x62]="Generic Time Label (ST 2103 (in development))"
