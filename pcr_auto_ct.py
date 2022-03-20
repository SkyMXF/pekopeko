import os
import time

import adb
from dfa.state import *
from dfa.condition import *
from dfa.transition import *
from dfa.operation import *

resources_dir = os.path.join("resources", "pcr_auto_ct")
cache_dir = os.path.join("cache")

adb_runner = adb.AdbRunner()
device = list(adb_runner.device_info.keys())[0]

# positions
pos_adventure = (0.5, 0.972)
pos_princess_arena = (0.868, 0.759)
pos_princess_arena_banner = (0.116, 0.06)
pos_edit_team_button = (0.269, 0.813)
pos_team_1_button = (0.105, 0.166)
pos_team_2_button = (0.2256, 0.166)
pos_team_3_button = (0.35, 0.166)
pos_team_edit_banner = (0.5, 0.0833)
pos_clear_team_member = (0.561, 0.841)
pos_my_team_button = (0.904, 0.291)
pos_my_team_banner = (0.5, 0.08)
pos_my_team_group_button = [
    (0.1288, 0.1678),
    (0.2738, 0.1678),
    (0.4225, 0.1678),
    (0.5675, 0.1678),
    (0.7175, 0.1678)
]
pos_my_team_reverse_button = (0.8981, 0.1656)
pos_choose_team_button = [(0.82625, 0.38667), (0.82625, 0.61), (0.82625, 0.802)]
pos_finish_edit = (0.875, 0.83)

def generate_choose_team_op(group_id, reverse=False):
    
    op_choose_team_group = TapOperation(
        runner=adb_runner,
        pos=pos_my_team_group_button[group_id],
        device=device,
        descrip="choose team group"
    )

    if not reverse:
        return op_choose_team_group
    
    op_choose_and_reverse = SequentialOperation(
        [
            op_choose_team_group,
            TapOperation(
                runner=adb_runner,
                pos=pos_my_team_reverse_button,
                device=device,
                descrip="press reverse button"
            )
        ], descrip="choose team group and reverse"
    )

    return op_choose_and_reverse

# states
state_main = State(descrip="main view")
state_adventure = State(descrip="adventure view")
state_princess_arena = State(descrip="princess arena view")
state_edit_teams = [State(descrip="edit team %d view"%(i)) for i in range(3)]
state_my_team = [State(descrip="my team %d view"%(i)) for i in range(3)]
state_finish_team = [State(descrip="finish editing team %d view"%(i)) for i in range(3)]

# main view -> adventure view
op_press_adventure = TapOperation(
    runner=adb_runner,
    pos=pos_adventure,
    device=device,
    descrip="press adventure"
)
cond_find_princess_arena = FindTemplateCondition(
    template_file=os.path.join(resources_dir, "princessArena.png"),
    screen_file=os.path.join(cache_dir, "%s.png"%(device)),
    adb_runner=adb_runner,
    pos=pos_princess_arena,
    descrip="Find princess arena button"
)
trans_adventure_view = CondTransition(
    aim_state=state_adventure,
    cond=cond_find_princess_arena
)
state_main.operation = op_press_adventure
state_main.transition = trans_adventure_view

# adventure view -> princess arena view
op_press_princess_arena = TapOperation(
    runner=adb_runner,
    pos=pos_princess_arena,
    device=device,
    descrip="press princess arena"
)
cond_find_princess_arena_banner = FindTemplateCondition(
    template_file=os.path.join(resources_dir, "princessArenaBanner.png"),
    screen_file=os.path.join(cache_dir, "%s.png"%(device)),
    adb_runner=adb_runner,
    pos=pos_princess_arena_banner,
    descrip="Find princess arena banner"
)
trans_princess_arena_view = CondTransition(
    aim_state=state_princess_arena,
    cond=cond_find_princess_arena_banner
)
state_adventure.operation = op_press_princess_arena
state_adventure.transition = trans_princess_arena_view

# princess arena view -> edit team 0 view
op_press_edit_team = TapOperation(
    runner=adb_runner,
    pos=pos_edit_team_button,
    device=device,
    descrip="press edit team button"
)
cond_find_team_1_button = FindTemplateCondition(
    template_file=os.path.join(resources_dir, "team1Button.png"),
    screen_file=os.path.join(cache_dir, "%s.png"%(device)),
    adb_runner=adb_runner,
    pos=pos_team_1_button,
    descrip="Find team 1 button"
)
trans_edit_team_0_view = CondTransition(
    aim_state=state_edit_teams[0],
    cond=cond_find_team_1_button
)
state_princess_arena.operation = op_press_edit_team
state_princess_arena.transition = trans_edit_team_0_view

# edit team 0 view -> my team 0 view
op_clear_team_member = ForOperation(
    op=TapOperation(
        runner=adb_runner,
        pos=pos_clear_team_member,
        device=device,
        delay=0.3
    ), times=7, descrip="clear team member"
)
op_clear_all_team_member = SequentialOperation(
    ops=[
        op_clear_team_member,
        TapOperation(
            runner=adb_runner,
            pos=pos_team_2_button,
            device=device
        ),
        op_clear_team_member,
        TapOperation(
            runner=adb_runner,
            pos=pos_team_3_button,
            device=device
        ),
        op_clear_team_member
    ], descrip="clear all team member"
)
op_press_my_team_button = TapOperation(
    runner=adb_runner,
    pos=pos_my_team_button,
    device=device,
    descrip="press my team button"
)
op_clear_and_my_team = SequentialOperation(
    ops=[
        op_clear_all_team_member,
        TapOperation(
            runner=adb_runner,
            pos=pos_team_1_button,
            device=device,
            descrip="press team 1 button"
        ),
        op_press_my_team_button
    ],
    descrip="clear team member and press my team button"
)
cond_find_my_team_banner = FindTemplateCondition(
    template_file=os.path.join(resources_dir, "myTeamBanner.png"),
    screen_file=os.path.join(cache_dir, "%s.png"%(device)),
    adb_runner=adb_runner,
    pos=pos_my_team_banner,
    descrip="Find my team banner"
)
trans_my_team_0_view = CondTransition(
    aim_state=state_my_team[0],
    cond=cond_find_my_team_banner
)
state_edit_teams[0].operation = op_clear_and_my_team
state_edit_teams[0].transition = trans_my_team_0_view

# my team 0 view -> edit team 1 view
op_choose_team_group = generate_choose_team_op(group_id=1)
op_press_choose_button_0 = TapOperation(
    runner=adb_runner,
    pos=pos_choose_team_button[0],
    device=device,
    descrip="press choose team button 0"
)
op_choose_group_and_team_and_return = SequentialOperation(
    ops=[
        op_choose_team_group,
        op_press_choose_button_0,
        TapOperation(
            runner=adb_runner,
            pos=pos_team_2_button,
            device=device,
            descrip="press team 2 button"
        )
    ],
    descrip="choose team group and team 0 and press team 2"
)
cond_find_team_2_button = FindTemplateCondition(
    template_file=os.path.join(resources_dir, "team2Button.png"),
    screen_file=os.path.join(cache_dir, "%s.png"%(device)),
    adb_runner=adb_runner,
    pos=pos_team_2_button,
    descrip="Find team 2 button"
)
trans_edit_team_1_view = CondTransition(
    aim_state=state_edit_teams[1],
    cond=cond_find_team_2_button
)
state_my_team[0].operation = op_choose_group_and_team_and_return
state_my_team[0].transition = trans_edit_team_1_view

# edit team 1 view -> my team 1 view
print("Edit teams 1 ...")
trans_my_team_1_view = CondTransition(
    aim_state=state_my_team[1],
    cond=cond_find_my_team_banner
)
state_edit_teams[1].operation = op_press_my_team_button
state_edit_teams[1].transition = trans_my_team_1_view

# my team 1 view -> edit team 2 view
op_press_choose_button_1 = TapOperation(
    runner=adb_runner,
    pos=pos_choose_team_button[1],
    device=device,
    descrip="press choose team button 1"
)
op_choose_group_and_team_and_return = SequentialOperation(
    ops=[
        op_choose_team_group,
        op_press_choose_button_1,
        TapOperation(
            runner=adb_runner,
            pos=pos_team_3_button,
            device=device,
            descrip="press team 3 button"
        )
    ],
    descrip="choose team group and team 1 and press team 3"
)
cond_find_team_3_button = FindTemplateCondition(
    template_file=os.path.join(resources_dir, "team3Button.png"),
    screen_file=os.path.join(cache_dir, "%s.png"%(device)),
    adb_runner=adb_runner,
    pos=pos_team_3_button,
    descrip="Find team 3 button"
)
trans_edit_team_2_view = CondTransition(
    aim_state=state_edit_teams[2],
    cond=cond_find_team_3_button
)
state_my_team[1].operation = op_choose_group_and_team_and_return
state_my_team[1].transition = trans_edit_team_2_view

# edit team 2 view -> my team 2 view
trans_my_team_2_view = CondTransition(
    aim_state=state_my_team[2],
    cond=cond_find_my_team_banner
)
state_edit_teams[2].operation = op_press_my_team_button
state_edit_teams[2].transition = trans_my_team_2_view

# my team 2 view -> finished
op_press_choose_button_2 = TapOperation(
    runner=adb_runner,
    pos=pos_choose_team_button[2],
    device=device,
    descrip="press choose team button 2"
)
op_choose_group_and_team_and_return = SequentialOperation(
    ops=[
        op_choose_team_group,
        op_press_choose_button_2,
        TapOperation(
            runner=adb_runner,
            pos=pos_finish_edit,
            device=device,
            descrip="press finish edit button"
        )
    ],
    descrip="choose team group and team 2 and press finish edit button"
)
trans_finish_state = SequentialTransition(
    aim_state=state_main
)
state_my_team[2].operation = op_choose_group_and_team_and_return
state_my_team[2].transition = trans_finish_state

def reset_choose_team_op(group_id, reverse=False):

    global state_my_team
    
    op_choose_team_group = generate_choose_team_op(group_id=group_id, reverse=reverse)

    op_choose_group_and_team_and_return = SequentialOperation(
        ops=[
            op_choose_team_group,
            op_press_choose_button_0,
            TapOperation(
                runner=adb_runner,
                pos=pos_team_2_button,
                device=device,
                descrip="press team 2 button"
            )
        ],
        descrip="choose team group and team 0 and press team 2"
    )
    state_my_team[0].operation = op_choose_group_and_team_and_return

    op_choose_team_group = generate_choose_team_op(group_id=group_id)
    op_choose_group_and_team_and_return = SequentialOperation(
        ops=[
            op_choose_team_group,
            op_press_choose_button_1,
            TapOperation(
                runner=adb_runner,
                pos=pos_team_3_button,
                device=device,
                descrip="press team 3 button"
            )
        ],
        descrip="choose team group and team 1 and press team 3"
    )
    state_my_team[1].operation = op_choose_group_and_team_and_return

    # my team 2 view -> finished
    op_choose_group_and_team_and_return = SequentialOperation(
        ops=[
            op_choose_team_group,
            op_press_choose_button_2,
            TapOperation(
                runner=adb_runner,
                pos=pos_finish_edit,
                device=device,
                descrip="press finish edit button"
            )
        ],
        descrip="choose team group and team 2 and press finish edit button"
    )
    state_my_team[2].operation = op_choose_group_and_team_and_return

def run_dfa():
    try:
        curr_state = state_main
        while True:
            curr_state.run()
            curr_state = curr_state.next()
            time_str = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            print("[%s]Current State: %s"%(time_str, curr_state.descrip))
            if curr_state is state_main:
                break
    except Exception as e:
        print(e)
    finally:
        pass
        #run_dfa()

if __name__ == "__main__":
    
    group_id = 0

    while True:
    
        group_id += 1
        if group_id > 4:
            group_id = 1
        reset_choose_team_op(group_id=group_id)
        print("Reset group id as %d"%(group_id))

        run_dfa()       # cost 35s
        print("Finish changing team. Sleeping...")
        time.sleep(70)

    