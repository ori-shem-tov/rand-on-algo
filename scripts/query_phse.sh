#!/usr/bin/env bash

a_addr=2OJJ5BUUUJE3ZSMJXTW3PAGALHDLFGBP555UDC7OBAJCGLMQIOSDTSE3V4
b_addr=5V5DYQ7R3B6LU3BWNZMK6I4W3LCMY4Z4B2DIQ6XGQRVL4UWVP5DM55QARE
eabc=UDDPDCI37AN4S2XS3N46CSCYP3PZFTPKMCCIVWVTFWZ7735RA346G3WZO4
app_id=15402405

goal clerk send -a 51000 -o a_to_eabc.tx -f $a_addr -t $eabc
goal clerk send -a 51000 -o b_to_eabc.tx -f $b_addr -t $eabc
goal app optin --app-id $app_id --from $eabc \
--app-arg "addr:$a_addr" --app-arg "addr:$b_addr" \
--app-arg "int:12297829382473034410" --app-arg "str:12345678" --app-arg "str:12345678" \
-o eabc_optin.tx

