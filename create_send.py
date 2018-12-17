#! /usr/bin/env python3

from datetime import datetime
import os
import sys
import time

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from counterpartylib.lib import util
from counterpartylib.lib import config

config.RPC = 'http://rpc:rpcpassword@localhost:4000/api/'
config.BACKEND_URL = 'http://localhost'
config.BACKEND_SSL_NO_VERIFY = False
config.REQUESTS_TIMEOUT = 1

# rpc_user and rpc_password are set in the bitcoin.conf file
RPC_USER = os.environ['RPC_USER'] if 'RPC_USER' in os.environ else 'c0ban'
RPC_PASSWORD = os.environ['RPC_PASSWORD'] if 'RPC_PASSWORD' in os.environ else 'c0ban'
RPC_HOST = os.environ['RPC_HOST'] if 'RPC_HOST' in os.environ else 'party-c0band-lyra2rev2'
RPC_PORT = os.environ['RPC_PORT'] if 'RPC_PORT' in os.environ else '3882'

connection_str = "http://{}:{}@{}:{}".format(
    RPC_USER, RPC_PASSWORD, RPC_HOST, RPC_PORT)
print(connection_str)
rpc_connection = AuthServiceProxy(connection_str)

def counterparty_api(method, params):
    # import pdb; pdb.set_trace()
    return util.api(method, params)


def c0ban_api(method, param):
    c0band = getattr(rpc_connection, method)
    return c0band(param)

def do_create_broadcast(source, fee_fraction, text, timestamp, value):
    unsigned_tx = counterparty_api('create_broadcast', {
        'source': source,
        'fee_fraction': fee_fraction,
        'text': text,
        'timestamp': timestamp,
        'value': value,
        'allow_unconfirmed_inputs': True
    })
    return unsigned_tx


if __name__ == '__main__':
    args = sys.argv
    ## broadcast
    unsigned_tx = do_create_broadcast(
        args[1],  # source
        0.05,  # fee_fraction
        'test2',  # text
        int(time.time()),  # timestamp
        -1,  # value
    )
    print("create tx = {}".format(unsigned_tx))

    ## sign
    sign_tx = c0ban_api('signrawtransaction', unsigned_tx)
    print("create sign_tx = {}".format(sign_tx['hex']))

    ## send
    result = c0ban_api('sendrawtransaction', sign_tx['hex'])
    print("send send_tx result = {}".format(result))

    ## generate
    # result = c0ban_api('generate', 1)
    # print("generate block = {}".format(result))
