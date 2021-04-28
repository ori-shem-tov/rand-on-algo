#!/usr/bin/env bash

goal_cmd="/Users/orishemtov/work/sandbox/sandbox goal"
#goal_cmd="goal"

/Users/orishemtov/work/sandbox/sandbox copy game_stateful_app.teal
/Users/orishemtov/work/sandbox/sandbox copy game_clear_out.teal
$goal_cmd app create --creator 5S5HN65ZHGPLXXCDJ6JO5GKEMUMQVHIR7DG24PCVHTN7E5B7XMI4UVHCFY --approval-prog ./game_stateful_app.teal --global-byteslices 0 --global-ints 0 --local-byteslices 6 --local-ints 0 --clear-prog ./game_clear_out.teal

