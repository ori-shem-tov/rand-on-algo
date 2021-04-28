#!/usr/bin/env bash

a_addr=USBW2XJGOJINHTAJJPKXV3S2NWSZKV4KRWH5KIBOZYUTKFNXP73WSZITGI
b_addr=ZUUCQCF3AVUBLFOSRSN6NY64GI3ZI2XJJ53ONX7EM7DJBWXYIXQB3UAMFU
eabc=ERI2YG6I4RZ3CC3ROJKZDGOE6I35W5KW2QGOSGM2N5IE46H6MJFQLMXTWE
app_id=6
goal_cmd="/Users/orishemtov/work/sandbox/sandbox goal"
#goal_cmd="goal"

$goal_cmd app closeout --app-id $app_id --from $eabc \
--app-arg "str:A" -o eabc_closeout_a.tx

$goal_cmd clerk send -a 0 -f $eabc -t $eabc --close-to $a_addr -o eabc_closeto_a.tx

docker exec -it algorand-sandbox-algod sh -c "cat eabc_closeout_a.tx eabc_closeto_a.tx > group_a.tx"
#cat eabc_closeout_a.tx eabc_closeto_a.tx > group_a.tx

$goal_cmd clerk group -i group_a.tx -o group_a.tx.out

$goal_cmd clerk split -i group_a.tx.out -o ungrp_a.tx

/Users/orishemtov/work/sandbox/sandbox copy game_stateless_escrow.teal
$goal_cmd clerk sign -i ungrp_a-0.tx -o ungrp_a-0.tx.sig -p game_stateless_escrow.teal --argb64 "$(echo -n settlement | base64)"
$goal_cmd clerk sign -i ungrp_a-1.tx -o ungrp_a-1.tx.sig -p game_stateless_escrow.teal --argb64 "$(echo -n settlement | base64)"

docker exec -it algorand-sandbox-algod sh -c "cat ungrp_a-0.tx.sig ungrp_a-1.tx.sig > signed.grp_a"
#cat ungrp_a-0.tx.sig ungrp_a-1.tx.sig > signed.grp_a
$goal_cmd clerk rawsend -f signed.grp_a



$goal_cmd app closeout --app-id $app_id --from $eabc \
--app-arg "str:B" -o eabc_closeout_b.tx

$goal_cmd clerk send -a 0 -f $eabc -t $eabc --close-to $b_addr -o eabc_closeto_b.tx

docker exec -it algorand-sandbox-algod sh -c "cat eabc_closeout_b.tx eabc_closeto_b.tx > group_b.tx"
#cat eabc_closeout_b.tx eabc_closeto_b.tx > group_b.tx

$goal_cmd clerk group -i group_b.tx -o group_b.tx.out

$goal_cmd clerk split -i group_b.tx.out -o ungrp_b.tx

/Users/orishemtov/work/sandbox/sandbox copy game_stateless_escrow.teal
$goal_cmd clerk sign -i ungrp_b-0.tx -o ungrp_b-0.tx.sig -p game_stateless_escrow.teal --argb64 "$(echo -n settlement | base64)"
$goal_cmd clerk sign -i ungrp_b-1.tx -o ungrp_b-1.tx.sig -p game_stateless_escrow.teal --argb64 "$(echo -n settlement | base64)"

docker exec -it algorand-sandbox-algod sh -c "cat ungrp_b-0.tx.sig ungrp_b-1.tx.sig > signed.grp_b"
#cat ungrp_b-0.tx.sig ungrp_b-1.tx.sig > signed.grp_b
$goal_cmd clerk rawsend -f signed.grp_b

