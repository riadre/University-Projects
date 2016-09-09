# Server to receive messages over Simple Transport Protocol (STP). The server 
# sits in an infinite loop listening for a file in sent via UDP packets from 
# an STP client. The server then reassembles the data and writes it to file 
# under the user-specified filename.
#
# Written by Juliana Zhu, z3252163
# Written for COMP9331 16s2, Assignment 1. 
#
# Python 3.0


import sys
import socket
import datetime
from stp_headers import receive_segment     # helper
from stp_headers import create_header       # helper
from stp_headers import interpret_header    # helper


RECEIVER_IP = "127.0.0.1"


def send_SYNACK(return_addr, received_sequence_number, sequence_number):
    print("Received Sequence Number:", received_sequence_number)
    ack_number = received_sequence_number + 1 
    header = create_header("SYNACK", sequence_number, ack_number)
    segment = header
    sock.sendto(segment, (return_addr))

def receive_ACK(expected_ack):
    return_addr, segment_type, received_sequence_no, received_ack_no, data = receive_segment(sock)
    if segment_type == "ACK" and received_ack_no == expected_ack:
        return return_addr, received_sequence_no, received_ack_no
    else:
        receive_ACK(expected_ack)

def receive_data(expected_ack):
    while True:
        return_addr, segment_type, received_sequence_no, received_ack_no, data = receive_segment(sock)
        print("EXPECTED_ACK = ", expected_ack)
        print("received_ack_no=", received_ack_no)
        if segment_type == "PUSH" and received_ack_no == expected_ack:
            with open(filename, 'a') as f:
                f.write(data.decode("ascii"))
                f.close()
            send_ACK(return_addr, received_sequence_no, received_ack_no)
            expected_ack = received_ack_no
        elif segment_type == "FIN":
            return return_addr, received_sequence_no, received_ack_no

def send_ACK(return_addr, ack_number, sequence_number):
    segment = create_header("ACK", sequence_number, ack_number)
    sock.sendto(segment, (return_addr))
    print("Just sent the ACK")

# ===== MAIN =====
# Command line arguments
try:
    receiver_port = int(sys.argv[1])
    filename = sys.argv[2]
except (IndexError, ValueError):
    print("Incorrect arguments. Usage: receiver.py <receiver_port> <file.txt>")
    sys.exit()

# Open the listening socket port.
sock = socket.socket(socket.AF_INET,                # internet
                            socket.SOCK_DGRAM)      # UDP
sock.bind((RECEIVER_IP, receiver_port))
sequence_number = 0 # Temp => change to random no. after testing
return_addr, segment_type, received_sequence_no, received_ack_no, data = receive_segment(sock)
send_SYNACK(return_addr, received_sequence_no, sequence_number)
sequence_number += 1
return_addr, received_sequence_no, received_ack_no = receive_ACK(sequence_number)
print("Successfully received ACK")
return_addr, received_sequence_no, received_ack_no = receive_data(sequence_number)
print("all data received, just finalising")
# if segment_type == "SYN":
#     generate_ack(sequence_number, ack_number)