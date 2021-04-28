import os
from hashlib import sha256

from algosdk import encoding
from algosdk.v2client import algod

from pyteal import compileTeal, Mode

from teal import game_stateless_escrow, oracle_stateless_escrow

from base64 import b64encode, b64decode, b32encode

from Cryptodome.Hash import SHA512


def cut(prog: bytes, prefix_end: int, suffix_start: int):
    prefix = prog[:prefix_end]
    suffix = prog[suffix_start:]
    prefix_b64 = b64encode(prefix)
    suffix_b64 = b64encode(suffix)
    checksum = SHA512.new(truncate='256')
    checksum.update(suffix)
    suffix_hash_b64 = b64encode(checksum.digest())
    return prefix_b64, suffix_b64, suffix_hash_b64


def main():
    algod_addr = os.getenv('AF_ALGOD_ADDRESS')
    algod_token = os.getenv('AF_ALGOD_TOKEN')
    if algod_addr == '':
        print('please export AF_ALGOD_ADDRESS and AF_ALGOD_TOKEN environment variables to a valid v2 algod client')
        exit(1)
    algod_client = algod.AlgodClient(
        algod_token,
        algod_addr,
    )
    A = 'USBW2XJGOJINHTAJJPKXV3S2NWSZKV4KRWH5KIBOZYUTKFNXP73WSZITGI'
    B = 'ZUUCQCF3AVUBLFOSRSN6NY64GI3ZI2XJJ53ONX7EM7DJBWXYIXQB3UAMFU'
    counter = 'AAAAAAAAAAAAAAAA'
    gse = compileTeal(game_stateless_escrow(A, B, counter), Mode.Signature, version=3)
    try:
        res = algod_client.compile(gse)
        gse_bytes = b64decode(res['result'])
    except Exception as e:
        print(f'error compiling stateless TEAL {e}')
        exit(1)
    eabc_addr = res['hash']
    gse_prefix_b64, gse_suffix_b64, gse_suffix_hash_b64 = cut(gse_bytes, 28, 107)
    print(gse_prefix_b64, gse_suffix_b64, gse_suffix_hash_b64)
    oracle_pk_addr = 'YUO5WDTSKVI5VADGDNGDCFDTPDO2TQMH2OZGZ6MLDXA6G2ZU5CD5GWVHBE'
    oracle_pk = b32encode(encoding.decode_address(oracle_pk_addr)).decode()
    oracle_owner_addr = 'LI5I7DNXC2FK6EVUJUOKXIPS3LV7FU5VHHI7LHBRIEBTTEWX5GICA47DBQ'
    block_number = 50
    app_id = 6
    x = sha256(encoding.decode_address(A) + encoding.decode_address(B) + bytes.fromhex(counter)).digest()
    x_b32 = b32encode(x).decode()

    ose = compileTeal(
        oracle_stateless_escrow(
            oracle_pk,
            oracle_owner_addr,
            eabc_addr,
            f'{block_number:08}',
            x_b32,
            app_id,
            "vrf"
        ),
        Mode.Signature, version=3
    )
    try:
        res = algod_client.compile(ose)
        ose_bytes = b64decode(res['result'])
    except Exception as e:
        print(f'error compiling stateless TEAL {e}')
        exit(1)



if __name__ == '__main__':
    main()
