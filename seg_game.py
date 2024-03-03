"""
Main import for 7-segment button game

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

from inspect import getfullargspec
from machine import Pin
from random import randint

from pico_tm1638_animations import TM1638Animated


class MiniGame:
    def __init__(self,
                 win_length,
                 tm1638 = None,
                 setup_routine = None,
                 correct_answer_conditions = None,
                 correct_answer_action = None,
                 incorrect_answer_action = None,
                 ):
        """
        MiniGame class adds crates a standard design pattern for ease of creating multiple games and running them
        together.

        This class is designed to support both inheritance and composition use cases.
        Composition may be achieved by passing functions for game setup_routine and correct_answer_action.

        :param tm1638: Instance of the tm168 instance from main / SevenSegButtonGame class
        :param win_length: Number of steps / turns required to complete the game
        :param setup_routine: Function to set up a MiniGame
            • This may take an argument of 'tm1638', the tm1638 object to be used
            • This may return a list (or iterable) of correct_answer_conditions
        :param correct_answer_conditions: List of correct answers (typically list of ints)
            • This may be determined randomly by the setup routine. If so, the setup_routine() should return the correct
            answer list, which will be stored to self.correct_answer_conditions
        :param correct_answer_action: Function for correct action response (progress increment is handled automatically)
            • This may take an argument of 'progress' which will access the MiniGame's progress attribute
        :param incorrect_answer_action: Function for incorrect action response (life decrement is handled automatically)
        """
        self.tm1638 = tm1638

        self.setup_routine = setup_routine

        # store conditions and action for correct answer
        self.correct_answer_conditions = correct_answer_conditions
        self.correct_answer_action = correct_answer_action
        self.incorrect_answer_action = incorrect_answer_action

        # internal monitoring variables
        self._win_length = win_length
        self._alive = True
        self._lives = 2
        self._progress = 0
        self._show_final_display = False

    def setup(self):
        """
        Setup actions for the MiniGme.
            Note: By default this is not called during class initiation to save memory when multiple MiniGame instances
            are registered.
        """
        if self.setup_routine is not None:
            setup_routine_args = getfullargspec(self.setup_routine)._asdict()['args']

            setup_kwargs = {}
            if 'tm1638' in setup_routine_args:
                setup_kwargs['tm1638'] = self.tm1638

            self.correct_answer_conditions = self.setup_routine(**setup_kwargs)

        assert len(self.correct_answer_conditions) == self._win_length, \
            f"The Game has {self._win_length} completion steps and {self.correct_answer_conditions} step answers. " \
            f"This game may be unplayable!"

    def _lose_screen(self):
        """
        Displays the game-over screen.
        """
        pass

    def _win_screen(self):
        """
        Displays the win screen.
        """
        self.tm1638.encode_string("--safe--")

    def final_display(self):
        """
        Shows the final screen for a game (win or lose).
        """
        if self._alive:
            self._win_screen()
        else:
            self._lose_screen()

    def play(self, input_button: int):
        """
        Plays a turn.

        :param input_button: The switch input number as an int
        """
        # lock the game loop if won or lost
        if self._show_final_display:
            self.final_display()
            return

        # take action according to the turn input
        if input_button == self.correct_answer_conditions[self._progress]:
            if self.correct_answer_action is not None:
                action_kwargs = {}
                correct_answer_action_args = getfullargspec(self.correct_answer_action)._asdict()['args']
                if 'progress' in correct_answer_action_args:
                    action_kwargs['progress'] = self._progress
                if 'tm1638' in correct_answer_action_args:
                    action_kwargs['tm1638'] = self.tm1638
                self.correct_answer_action(**action_kwargs)
            self._progress += 1
        else:
            if self.incorrect_answer_action is not None:
                action_kwargs = {}
                incorrect_answer_action_args = getfullargspec(self.incorrect_answer_action)._asdict()['args']
                if 'tm1638' in incorrect_answer_action_args:
                    action_kwargs['tm1638'] = self.tm1638
                self.incorrect_answer_action(**action_kwargs)
            else:
                self.tm1638.encode_string("Error")
            self._lives -= 1

        # take action if the game has been won or lost
        if self._progress == self._win_length:
            self._show_final_display = True
            self.final_display()
        elif self._lives == 0:
            self._alive = False
            self._show_final_display = True
            self.final_display()


class SevenSegButtonGame:
    def __init__(self,
                 stb,
                 clk,
                 dio):
        """
        7-segment button game main class

        This object can have multiple games assigned and selects one at random, then
        coordinates gameplay with the selected game.

        :param stb: Specifies the stb pin number
        :param clk: Specifies the clk pin number
        :param dio: Specifies the dio pin number
        """
        self.tm = TM1638Animated(stb=Pin(stb),
                                 clk=Pin(clk),
                                 dio=Pin(dio),
                                 brightness=4)

        self._game_register = {}

        # internal monitoring variables
        self._game_select = 0
        self._selected_game = None
        self._setup_run = False

        # internal input monitoring variables
        self.is_pressed = False

    def register_game(self,
                      game_title,
                      game_object):
        """
        Enables the main object to register

        :param game_title: String of the game's name
        :param game_object: MiniGame object containing the game instance
        """
        assert not self._setup_run, "Games may not be registered after setup() is called"
        self._game_register[game_title] = game_object

        if game_object.tm1638 is None:
            game_object.tm1638 = self.tm

    def _check_new_input(self):
        """
        This function gets the button input, but prevents single presses from being registered multiple times. While a
        button remains pressed, the function will return 0 after the first call, until all buttons are released.

        :return: Integer of allowed button input
        """
        key_pressed = int(self.tm.qyf_keys())
        if key_pressed > 0 and not self.is_pressed:
            self.is_pressed = True
            return key_pressed
        elif key_pressed == 0 and self.is_pressed:
            self.is_pressed = False

        return 0

    def setup(self,
              selected_game_name = None):
        """
        Runs the setup of the registered MiniGame.
            Note: all games should be registered before this function call

        :param selected_game_name: Enables a specific game to be selected and played
        """
        if selected_game_name is None:
            self._game_select = randint(0, len(self._game_register) - 1)
            selected_game_name = list(self._game_register.keys())[self._game_select]

        self._selected_game = self._game_register[selected_game_name]
        self._selected_game.setup()

        self._setup_run = True

    def game_loop(self):
        """
        Main loop entry point for game.
        This is designed to be called from a loop to maintain responsiveness of the controller
            Note: Win / lose handling is handled by the MiniGame class so that different MiniGame instances can have
            different outcomes if desired.
        """
        assert self._setup_run, "Please call setup() from the main file before entering the loop"

        # get the player input
        player_input = self._check_new_input()

        # pass the player input to the game to play a turn
        if player_input > 0:
            self._selected_game.play(player_input)
