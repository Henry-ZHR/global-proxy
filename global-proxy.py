#!/usr/bin/python
# PYTHON_ARGCOMPLETE_OK

import pwd, sys
from argparse import ArgumentParser, BooleanOptionalAction
from socket import AF_INET, AF_INET6

from nftables import Nftables
from pyroute2 import IPRoute

FWMARK = 2333
TABLE_ID = 233


def run_nft_cmd(cmd: str, ignore_error: bool = False):
    rc, output, error = nft.cmd(cmd)
    if not ignore_error and rc != 0:
        print(f'Error: Failed to run nft cmd `{cmd}`', file=sys.stderr)
        print(error, file=sys.stderr)
        sys.exit(1)


def add_or_del_ip_route(command: str):
    lo = ipr.link_lookup(ifname='lo')[0]
    for family in AF_INET, AF_INET6:
        ipr.route(command, family=family, type='local', oif=lo, table=TABLE_ID, scope='host')
        ipr.rule(command, family=family, fwmark=FWMARK, table=TABLE_ID)


def init():
    add_or_del_ip_route('add')

    if not nft.add_var(f'MARK={FWMARK}'):
        sys.exit('Error: Failed to add var MARK')
    rc, output, error = nft.cmd_from_file('/usr/share/global-proxy/global-proxy.nft')
    if rc != 0:
        print(f'Error: Failed to run nft cmd from file: {error}', file=sys.stderr)
        sys.exit(1)


def clear():
    add_or_del_ip_route('del')
    run_nft_cmd('delete table inet global_proxy')


def get_uid(user: str) -> int:
    try:
        return pwd.getpwnam(user).pw_uid
    except:
        pass
    try:
        return pwd.getpwuid(int(user)).pw_uid
    except:
        pass
    sys.exit(f'Error: Failed to get uid of user {user}')


def enable(user: str, **kwargs):
    uid = get_uid(user)
    chain = f'inet global_proxy output_{uid}'
    run_nft_cmd(f'delete chain {chain}', ignore_error=True)
    run_nft_cmd(f'add chain {chain} {{ type route hook output priority mangle; }}')
    run_nft_cmd(f'add rule {chain} meta skuid != {uid} return')
    for proto in ['tcp', 'udp']:
        if kwargs[proto]:
            run_nft_cmd(f'add rule {chain} meta l4proto {proto} jump output_loop')


def disable(user: str):
    uid = get_uid(user)
    chain = f'inet global_proxy output_{uid}'
    run_nft_cmd(f'delete chain {chain}')


if __name__ == '__main__':
    parser = ArgumentParser(description='Helper script for setting up global proxy')
    subparsers = parser.add_subparsers(title='action', required=True)

    parser_init = subparsers.add_parser('init', help='initialize the environment')
    parser_init.set_defaults(func=init)

    parser_clear = subparsers.add_parser('clear', help='clear the environment')
    parser_clear.set_defaults(func=clear)

    parser_enable = subparsers.add_parser('enable', help='enable for specific user')
    parser_enable.add_argument('user', help='uid / username of the user')
    parser_enable.add_argument('--tcp',
                               action=BooleanOptionalAction,
                               default=True,
                               help='whether enable for TCP (default: true)')
    parser_enable.add_argument('--udp',
                               action=BooleanOptionalAction,
                               default=True,
                               help='whether enable for UDP (default: true)')
    parser_enable.set_defaults(func=enable)

    parser_disable = subparsers.add_parser('disable', help='disable for specific user')
    parser_disable.add_argument('user', help='uid / username of the user')
    parser_disable.set_defaults(func=disable)

    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except:
        pass

    args = parser.parse_args()
    func = args.func
    args = vars(args)
    args.pop('func')

    nft = Nftables()
    ipr = IPRoute()

    func(**args)
