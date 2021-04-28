from algosdk.v2client import algod
import os
import argparse


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
    parser = argparse.ArgumentParser(description='Test the VRF demo with a simple coin toss game.')
    parser.add_argument()
