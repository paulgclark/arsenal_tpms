#!/usr/bin/python3
import zmq
import pmt
import argparse

# default ZMQ addresses
TCP_MSG_FROM_RX_FG = "tcp://127.0.0.1:5555"


class ZmqSocketFromRxFg:
    def __init__(self, tcp_str: str = TCP_MSG_FROM_RX_FG, timeout_ms: int = 100):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect(tcp_str)
        self.timeout_ms = timeout_ms

    def get_payload(self) -> list[int]:
        raw_msg = self.socket.recv()
        pdu_rx = pmt.deserialize_str(raw_msg)
        payload_pmt = pmt.cdr(pdu_rx)
        payload = list(pmt.u8vector_elements(payload_pmt))
        return payload


# returns a string containing each bit of the input bit list
# - separator enables a '|' between each 8 bits and a space between
#   the nibbles of each byte
def bit_list_to_bit_str(bit_list, separator=False):
    bit_str = ""
    for i, bit in enumerate(bit_list):
        if separator:
            if i % 8 == 0:
                bit_str += '|'
            elif i % 4 == 0:
                bit_str += ' '
        bit_str += str(bit)
    return bit_str


def bit_list_to_byte_list(bits, chunk_size=8):
    if len(bits) % chunk_size != 0:
        print("WARNING: incomplete byte detected in input to bit_list_to_byte_list")
    byte_list = []
    for i in range(0, len(bits), chunk_size):
        bits_in_byte = bits[i:i+chunk_size]
        byte = bit_list_to_uint(bits_in_byte)
        byte_list.append(byte)
    return byte_list


def bit_list_to_uint(bit_list):
    # build integer left shifting each bit into final value
    value = 0
    for bit in bit_list:
        if bit in (0, 1):
            value = (value << 1) | bit
        else:
            # we don't have a valid bit, return illegal value
            value = -1
            break
    return int(value)


# converts a list of bytes into a string containing their hex
# representation
# - sep_char (a space by default) is inserted between each byte;
#   setting this to "" eliminates the separation
def byte_list_to_hex_str(byte_list, sep_char=" "):
    s = ""
    for byte in byte_list:
        if 0 <= byte <= 15:
            s += "0{:1x}".format(byte) + sep_char
        elif 15 <= byte <= 255:
            s += "{:2x}".format(byte) + sep_char
        else:
            s += "0xXX" + sep_char
            print("WARNING: Byte value not 0-255")
    # if the separator is enabled, we get an unwanted separator at the end
    if len(sep_char) > 0:
        s = s[:-1*len(sep_char)]
    return s


out_file_name = "payloads.txt"

# should be an Enum
NRZ = 0
MANCH = 1
MANCH_INV = 2
MANCH_DIFF = 3


def decoder(encoded_bits, encoding):
    if encoding in [MANCH, MANCH_INV]:
        decoded_bits = []
        for i in range(0, len(encoded_bits), 2):
            if encoded_bits[i] == encoded_bits[i + 1]:
                print("Manchester Decode Error")
                break
            else:
                if encoding == MANCH_INV:
                    decoded_bits += [encoded_bits[i]]
                else:
                    decoded_bits += [encoded_bits[i + 1]]
    elif encoding == MANCH_DIFF:
        decoded_bits = []
        for i in range(0, len(encoded_bits), 2):
            # same level signifies 1
            if encoded_bits[i] == encoded_bits[i+1]:
                decoded_bits.append(1)
            else:
                decoded_bits.append(0)
    else:
        decoded_bits = encoded_bits

    return decoded_bits


def main():
    parser = argparse.ArgumentParser("Receives packets via ZMQ and logs them to console with optional decoding")
    parser.add_argument(
        "-d",
        "--decode",
        help="select decoding (0: NRZ (none), 1: Manchester, 2: Inverted Manchester, 3: Differential Manchester)",
        type=int,
        default=0)
    args = parser.parse_args()

    # instance the ZMQ connection to the flowgraph
    rx_socket = ZmqSocketFromRxFg(tcp_str=TCP_MSG_FROM_RX_FG)

    print("Logging active, press Ctrl-C to complete")
    while True:
        try:
            # check if there's a message from the flowgraph
            rx_bits = rx_socket.get_payload()
            decoded_bits = decoder(encoded_bits=rx_bits, encoding=args.decode)
            decoded_bytes = bit_list_to_byte_list(decoded_bits)
            print(f"{byte_list_to_hex_str(decoded_bytes)}")

        except KeyboardInterrupt:
            print("Exiting logging...")
            break


if __name__ == "__main__":
    main()
