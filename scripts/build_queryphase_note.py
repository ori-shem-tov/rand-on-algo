from algosdk import encoding
from hashlib import sha256
from sys import argv
from base64 import b64encode, b32encode


def build_note(opk_addr: str, owner_addr: str, sender: str, block_number: str, addr_a: str, addr_b: str, counter: str, app_id: str):
    opk_addr = encoding.decode_address(opk_addr)
    owner_addr = encoding.decode_address(owner_addr)
    sender = encoding.decode_address(sender)
    addr_a = encoding.decode_address(addr_a)
    addr_b = encoding.decode_address(addr_b)
    result = 'vrf-v0'.encode()
    block_number = f'{int(block_number):08}'
    app_id = f'{int(app_id):08}'
    x = sha256(addr_a + addr_b + bytes.fromhex(hex(int(counter))[2:])).digest()
    result += opk_addr + owner_addr + sender + block_number.encode() + x + app_id.encode() + 'vrf'.encode()
    return result


if __name__ == '__main__':
    print(b64encode(build_note(*argv[1:])).decode(), end='')
