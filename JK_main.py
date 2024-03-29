"""
Primary driver file for project for RPi Pico
This file creates the mini games, adds custom logic for each and then executes the main game framework

Copyright (C) 2023  James Kano

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from random import randint
from seg_game import SevenSegButtonGame, MiniGame
import time
from typing import Any, Dict, List

from rpi_tm1638_animations import TM1638Animated as Tm


# ------------------- #
#     Memory game     #
# ------------------- #

mem_win_length = 5


def memory_setup(tm1638: Tm) -> Any:
    """
    Setup answers and starting display for memory game

    :param tm1638: tm1638 interface (auto-assigned by MiniGame)
    :return: dictionary of game attributes to set up
    """
    memorable_sequence = [1 << randint(0, 7) for i in range(mem_win_length)]
    for led_num in memorable_sequence:
        tm1638.led(led_num, 1)
        time.sleep(0.5)
        tm1638.leds(0)
        time.sleep(0.25)
        tm1638.encode_string('-' * mem_win_length)

    start_seg_display = [64] * mem_win_length

    return_dict = {
        'correct_answer_conditions': memorable_sequence,
        'game_seg_display': start_seg_display,
    }

    return return_dict


def memory_correct_answer_action(progress: int) -> List[Any]:
    """
    Display / response when a correct answer is given for memory game

    :param progress: integer of the game's progress (auto-assigned by MiniGame)
    :param tm1638: tm1638 interface (auto-assigned by MiniGame)
    :return: List of segments for the game display
    """
    current_seg_display = [0 if i < progress
                           else 64
                           for i in range(mem_win_length)]

    return current_seg_display


memory_game = MiniGame(win_length=mem_win_length)
memory_game.setup_routine = memory_setup
memory_game.correct_answer_action = memory_correct_answer_action
memory_game.input_as_linear_int = False


# ----------------- #
#     Math game     #
# ----------------- #

math_answer_num = randint(1, 256)
math_answer_num_str = str(math_answer_num)
math_win_length = len(math_answer_num_str)


def math_setup(tm1638: Tm) -> Dict[str, Any]:
    """
    Setup answers and starting display for math game

    :param tm1638: tm1638 interface (auto-assigned by MiniGame)
    :return: dictionary of game attributes to set up
    """
    tm1638.load(50)
    time.sleep(0.5)
    tm1638.unload(50)

    # generate the answer at random
    answer_list = [int(i) for i in math_answer_num_str]

    # assign random segment positions to the answer integers
    answer_int_positions = {}
    for i in range(len(answer_list)):
        rand_position = randint(0, tm1638.num_segments - 1)
        while rand_position in answer_int_positions:
            rand_position = randint(0, tm1638.num_segments - 1)
        answer_int_positions[rand_position] = int(answer_list[i])

    # generate answer sequence and starting display
    start_seg_display = [randint(0, 9) if i not in answer_int_positions
                         else answer_int_positions[i]
                         for i in range(tm1638.num_segments)]

    return_dict = {
        'correct_answer_conditions': answer_list,
        'game_seg_display': start_seg_display,
        'game_LED_display': math_answer_num
    }

    return return_dict


def math_map_input(input_button: int,
                   game_seg_display: List[int]) -> int:
    """
    Maps the button input to corresponding the segment display input
    """
    input_button = game_seg_display[input_button]
    return input_button


def math_incorrect_answer_action(tm1638: Tm) -> List[Any]:
    """
    Reset progress if incorrect answer for math game

    :param tm1638: tm1638 interface (auto-assigned by MiniGame)
    """
    tm1638.encode_string("Error")
    return 0


math_game = MiniGame(win_length=math_win_length,
                     setup_routine=math_setup,
                     map_input=math_map_input,
                     incorrect_answer_action=math_incorrect_answer_action,
                     show_button_feedback=False,
                     input_as_linear_int=True)


# ------------------------------ #
#     Spatial reasoning game     #
# ------------------------------ #

spatial_game = MiniGame(win_length=4)


def main():
    """
    Main method to be executed upon microcontroller boot
    """
    # setup for main execution
    seg_game = SevenSegButtonGame(stb=2,
                                  clk=3,
                                  dio=4)

    seg_game.register_game('memory', memory_game)
    seg_game.register_game('math', math_game)
    seg_game.register_game('space', spatial_game)

    seg_game.setup()

    while seg_game.selected_game._alive:
        if seg_game.in_standby:
            seg_game.standby_start_loop
        else:
            seg_game.game_loop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
