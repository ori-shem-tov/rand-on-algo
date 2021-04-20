from pyteal import *


def game_stateless_escrow(addr_a: str, addr_b: str, counter: str):
    handle_query_phase = And(
        Bytes('base16', counter) == Bytes('base16', counter),
        Txn.rekey_to() == Global.zero_address(),
        Global.group_size() == Int(4),
        *[And(
            Gtxn[i].type_enum() == TxnType.Payment,
            Gtxn[i].sender() == Addr(addr),
            Gtxn[i].receiver() == Txn.sender(),
        ) for i, addr in enumerate([addr_a, addr_b])],
        Or(
            And(
                Txn.group_index() == Int(2),
                Txn.type_enum() == TxnType.ApplicationCall,
                Txn.on_completion() == OnComplete.OptIn,
            ),
            And(
                Txn.group_index() == Int(3),
                Txn.type_enum() == TxnType.Payment,
                Txn.close_remainder_to() == Global.zero_address(),
            )
        )
    )

    handle_settlement_phase = And(
        Txn.rekey_to() == Global.zero_address(),
        Global.group_size() == Int(2),
        Or(
            And(
                Txn.group_index() == Int(0),
                Txn.type_enum() == TxnType.ApplicationCall,
                Txn.on_completion() == OnComplete.CloseOut,
            ),
            And(
                Txn.group_index() == Int(1),
                Txn.type_enum() == TxnType.Payment,
                Txn.amount() == Int(0),
                Or(
                    And(
                        Gtxn[0].application_args[1] == Bytes('A'),
                        Txn.close_remainder_to() == Addr(addr_a),
                    ),
                    And(
                        Gtxn[0].application_args[1] == Bytes('B'),
                        Txn.close_remainder_to() == Addr(addr_b),
                    ),
                ),
            ),
        ),
        Gtxn[0].type_enum() == TxnType.ApplicationCall,
        Gtxn[0].on_completion() == OnComplete.CloseOut,

    )

    return Cond(
        [Arg(0) == Bytes('query'), Return(handle_query_phase)],
        [Arg(0) == Bytes('settlement'), Return(handle_settlement_phase)],
    )


def oracle_stateless_escrow(signing_pk_b32: str, owner_address: str, sender: str, block: int, x_b32: str, app_id: int, arg0: str):
    return And(
        Global.group_size() == Int(2),
        Or(
            And(
                Txn.group_index() == Int(0),
                Txn.type_enum() == TxnType.ApplicationCall,
                Txn.application_id() == Int(app_id),
                Txn.application_args[0] == Bytes(arg0),
                Txn.application_args[1] == Itob(Int(block)),
                Txn.application_args[3] == Bytes('base32', x_b32),
                Txn.accounts[1] == Addr(sender),
                Ed25519Verify(
                    Concat(
                        Txn.sender(),
                        Itob(Int(block)),
                        Txn.application_args[2],
                        Bytes('base32', x_b32),
                        Txn.application_args[4]
                    ),
                    Arg(0),
                    Bytes('base32', signing_pk_b32)
                )
            ),
            And(
                Txn.group_index() == Int(1),
                Txn.type_enum() == TxnType.Payment,
                Txn.amount() == Int(0),
                Txn.close_remainder_to() == Addr(owner_address)
            )
        )
    )


def game_stateful_app():
    handle_opt_in = Seq(
        [
            Assert(Not(App.optedIn(Int(0), Int(0)))),
            App.localPut(Int(0), Bytes('A'), Txn.application_args[0]),
            App.localPut(Int(0), Bytes('B'), Txn.application_args[1]),
            App.localPut(Int(0), Bytes('counter'), Txn.application_args[2]),
            App.localPut(Int(0), Bytes('block'), Txn.application_args[3]),
            App.localPut(Int(0), Bytes('expiration'), Txn.application_args[4]),
            Int(1),
        ]
    )
    store_vrf = Seq(
        [
            App.localPut(Int(1), Bytes('vrf'), Txn.application_args[4]),
            Int(1),
        ]
    )
    vrf_suffix = Btoi(Substring(App.localGet(Int(0), Bytes('vrf')), Int(63), Int(64)))
    handle_close_out = Or(
        And(
            vrf_suffix % Int(2) == Int(0),
            Txn.application_args[0] == Bytes('A')
        ),
        And(
            vrf_suffix % Int(2) == Int(1),
            Txn.application_args[0] == Bytes('B')
        )
    )
    program = Cond(
        [Txn.application_id() == Int(0), Return(Int(1))],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Int(1))],
        [Txn.on_completion() == OnComplete.OptIn, Return(handle_opt_in)],
        [Txn.on_completion() == OnComplete.CloseOut, Return(handle_close_out)],
        [Txn.application_args[0] == Bytes('vrf'), Return(store_vrf)]
    )
    return program


def game_clear_out():
    program = Seq([
        Return(Int(1))
    ])
    return program


if __name__ == '__main__':
    filename = 'game_stateless_escrow.teal'
    with open(filename, 'w') as f:
        compiled = compileTeal(
            game_stateless_escrow(
                '6QFRT6Y6ZWCHHSYW7TUDF4V7PEYQ3GDT7JSCZSZ4XDGKAGEMOJDR3CZKGQ',
                '5V5DYQ7R3B6LU3BWNZMK6I4W3LCMY4Z4B2DIQ6XGQRVL4UWVP5DM55QARE',
                'AAAAAAAAAAAAAAAA'
            ),
            Mode.Signature,
        )
        f.write(compiled)
        print(f'compiled {filename}')

    filename = 'oracle_stateless_escrow.teal'
    with open(filename, 'w') as f:
        compiled = compileTeal(
            oracle_stateless_escrow(
                'TCLTAJTUJOTNAT2T6IIAQ2W74PHLFRWBDBFPGGQHWUUXIQQSWQWA====',
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ',
                'AEAQCAIBAEAQCAIBAEAQCAIBAEAQCAIBAEAQCAIBAEAQCAIBAEA5RCDXMI',
                13630997,
                'VKXOU4TN5LFJ5RUEKSUACP7AXPBN4I7333T3WQ5TCB7CS7GRBVYZS===',
                123456,
                "vrf"
            ),
            Mode.Signature,
        )
        f.write(compiled)
        print(f'compiled {filename}')
    filename = 'game_stateful_app.teal'
    with open(filename, 'w') as f:
        compiled = compileTeal(game_stateful_app(), Mode.Application)
        f.write(compiled)
        print(f'compiled {filename}')
    filename = 'game_clear_out.teal'
    with open(filename, 'w') as f:
        compiled = compileTeal(game_clear_out(), Mode.Application)
        f.write(compiled)
        print(f'compiled {filename}')
