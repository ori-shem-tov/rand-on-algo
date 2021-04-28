#!/usr/bin/env bash

a_addr=USBW2XJGOJINHTAJJPKXV3S2NWSZKV4KRWH5KIBOZYUTKFNXP73WSZITGI
b_addr=ZUUCQCF3AVUBLFOSRSN6NY64GI3ZI2XJJ53ONX7EM7DJBWXYIXQB3UAMFU
eabc=ERI2YG6I4RZ3CC3ROJKZDGOE6I35W5KW2QGOSGM2N5IE46H6MJFQLMXTWE
app_id=6
oracle_pk=YUO5WDTSKVI5VADGDNGDCFDTPDO2TQMH2OZGZ6MLDXA6G2ZU5CD5GWVHBE
oracle_owner_address=LI5I7DNXC2FK6EVUJUOKXIPS3LV7FU5VHHI7LHBRIEBTTEWX5GICA47DBQ
block_number=50
padded_block_number=$(printf "%08d" $block_number)
counter=12297829382473034410
oe=XNKLALUXBK27CMWBYS5DVMUEGCHDTI3ZHPBQN7SUKJSPLUB5FM3DO27QQ4
goal_cmd="/Users/orishemtov/work/sandbox/sandbox goal"
#goal_cmd="goal"
eabc_logic_suffix_b64="LSgSQABcLSkSQAABADIEIhNAAEkxFiMSQAA4MRYkEkAAAQAxECQSMQgjEhAzABAlEhAzABkiEhA3ABoAKhIxCSsSEDcAGgAnBBIxCScFEhAREEMxECUSMRkiEhBDI0NCAFknBicGEjEgMgMSEDIEIQQSEDMAECQSMwAAKxIQMwAHMQASEBAzARAkEjMBACcFEhAzAQcxABIQEDEWIhIxECUSEDEZJBIQMRYhBRIxECQSEDEJMgMSEBEQQw=="

$goal_cmd clerk send -a 51000 -o a_to_eabc.tx -f $a_addr -t $eabc
$goal_cmd clerk send -a 51000 -o b_to_eabc.tx -f $b_addr -t $eabc
$goal_cmd app optin --app-id $app_id --from $eabc \
--app-arg "addr:$a_addr" --app-arg "addr:$b_addr" \
--app-arg "int:$counter" --app-arg "str:$padded_block_number" --app-arg "int:12345678" --app-arg "b64:$eabc_logic_suffix_b64" \
-o eabc_optin.tx

note=$(python scripts/build_queryphase_note.py $oracle_pk $oracle_owner_address $eabc $block_number $a_addr $b_addr $counter $app_id)
echo "note: $note"

$goal_cmd clerk send -a 50000 -o eabc_to_oe.tx -f $eabc -t $oe --noteb64 "$note"

docker exec -it algorand-sandbox-algod sh -c "cat a_to_eabc.tx b_to_eabc.tx eabc_optin.tx eabc_to_oe.tx > group.tx"
#cat a_to_eabc.tx b_to_eabc.tx eabc_optin.tx eabc_to_oe.tx > group.tx
$goal_cmd clerk group -i group.tx -o group.tx.out

$goal_cmd clerk split -i group.tx.out -o ungrp.tx

/Users/orishemtov/work/sandbox/sandbox copy game_stateless_escrow.teal
$goal_cmd clerk sign -i ungrp-0.tx -o ungrp-0.tx.sig
$goal_cmd clerk sign -i ungrp-1.tx -o ungrp-1.tx.sig
$goal_cmd clerk sign -i ungrp-2.tx -o ungrp-2.tx.sig -p game_stateless_escrow.teal --argb64 "$(echo -n query | base64)"
$goal_cmd clerk sign -i ungrp-3.tx -o ungrp-3.tx.sig -p game_stateless_escrow.teal --argb64 "$(echo -n query | base64)"

docker exec -it algorand-sandbox-algod sh -c "cat ungrp-0.tx.sig ungrp-1.tx.sig ungrp-2.tx.sig ungrp-3.tx.sig > signed.grp"
#cat ungrp-0.tx.sig ungrp-1.tx.sig ungrp-2.tx.sig ungrp-3.tx.sig > signed.grp
$goal_cmd clerk rawsend -f signed.grp