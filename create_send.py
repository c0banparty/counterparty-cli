#! /usr/bin/env python3

from datetime import datetime
import os
import sys
from optparse import OptionParser
import time

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from counterpartylib.lib import util
from counterpartylib.lib import config

parser = OptionParser()
parser.add_option("-r", "--regtest", dest="regtest", default=True)
parser.add_option("-t", "--testnet", dest="testnet", default=False)
(options, args) = parser.parse_args()

# counterparty-lib
XCB_RPC_PORT = config.DEFAULT_RPC_PORT
if options.regtest:
    XCB_RPC_PORT = config.DEFAULT_RPC_PORT_REGTEST
elif options.testnet:
    XCB_RPC_PORT = config.DEFAULT_RPC_PORT_TESTNET

config.RPC = "http://rpc:rpcpassword@localhost:{}/api/".format(XCB_RPC_PORT)
config.BACKEND_URL = 'http://localhost'
config.BACKEND_SSL_NO_VERIFY = False
config.REQUESTS_TIMEOUT = 1


# c0band
CBN_RPC_USER = os.environ['RPC_USER'] if 'RPC_USER' in os.environ else 'test'
CBN_RPC_PASSWORD = os.environ['RPC_PASSWORD'] if 'RPC_PASSWORD' in os.environ else 'test'
CBN_RPC_HOST = os.environ['RPC_HOST'] if 'RPC_HOST' in os.environ else 'c0ban'
CBN_RPC_PORT = os.environ['RPC_PORT'] if 'RPC_PORT' in os.environ else '23882'

cbn_connection_str = "http://{}:{}@{}:{}".format(
    CBN_RPC_USER, CBN_RPC_PASSWORD, CBN_RPC_HOST, CBN_RPC_PORT)
cbn_rpc_connection = AuthServiceProxy(cbn_connection_str)

def counterparty_api(method, params):
    # import pdb; pdb.set_trace()
    return util.api(method, params)


def c0ban_api(method, param):
    c0band = getattr(cbn_rpc_connection, method)
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
