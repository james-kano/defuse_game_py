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
from typing import List

from rpi_tm1638_animations import TM1638Animated as Tm


# ------------------- #
#     Memory game     #
# ------------------- #

mem_win_length = 5


def memory_setup(tm1638: Tm) -> List[int]:
    """
    Setup answers and starting display for memory game

    :param tm1638: tm1638 interface (auto-assigned by MiniGame)
    :return: List of correct answers as integers
    """
    memorable_sequence = [1 << randint(0, 7) for i in range(mem_win_length)]
    for led_num in memorable_sequence:
        tm1638.led(led_num, 1)
        time.sleep(0.5)
        tm1638.leds(0)
        time.sleep(0.25)
        tm1638.encode_string('-' * mem_win_length)
    return memorable_sequence


def memory_correct_answer_action(progress: int,
                                 tm1638: Tm) -> None:
    """
    Display / response when a correct answer is given for memory game

    :param progress: integer of the game's progress (auto-assigned by MiniGame)
    :param tm1638: tm1638 interface (auto-assigned by MiniGame)
    """
    tm1638.write(0, progress)


memory_game = MiniGame(win_length=mem_win_length)
memory_game.setup_routine = memory_setup
memory_game.correct_answer_action = memory_correct_answer_action


# ----------------- #
#     Math game     #
# ----------------- #

math_win_length = 3


def math_setup(tm1638: Tm):
    """
    Setup answers and starting display for math game

    :param tm1638: tm1638 interface (auto-assigned by MiniGame)
    :return: List of correct answers as integers
    """

    pass


def math_correct_answer_action(progress: int,
                               tm1638: Tm):
    """
    Display / response when a correct answer is given for math game

    :param progress: integer of the game's progress (auto-assigned by MiniGame)
    :param tm1638: tm1638 interface (auto-assigned by MiniGame)
    """
    pass


math_game = MiniGame(win_length=math_win_length,
                     )


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
