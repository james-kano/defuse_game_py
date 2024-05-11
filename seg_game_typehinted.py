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
from random import randint
from time import sleep
from typing import Any, Callable, Dict, List, Optional

from rpi_tm1638_animations import TM1638Animated
from decorators import testing_wrapper


class MiniGame:
    def __init__(self,
                 win_length: int,
                 tm1638: TM1638Animated = None,
                 setup_routine: Callable = None,
                 correct_answer_conditions: List[Optional[int]] = None,
                 map_input: Callable = None,
                 input_as_linear_int: bool = True,
                 show_button_feedback: bool = True,
                 correct_answer_action: Callable = None,
                 incorrect_answer_action: Callable = None,
                 test_mode: bool=False
                 ) -> None:
        """
        MiniGame class creates a standard design pattern for ease of creating multiple games and running them
        together.

        This class is designed to support both inheritance and composition use cases.
        Composition may be achieved by passing functions for game setup_routine and correct_answer_action.

        :param tm1638: Instance of the tm168 instance from main / SevenSegButtonGame class
        :param win_length: Number of steps / turns required to complete the game
        :param setup_routine: Function to set up a MiniGame
            • This may take an argument of 'tm1638', the tm1638 object to be used
            • This may return:
                - a list (or iterable) of correct_answer_conditions
                - the starting display for the segments
        :param correct_answer_conditions: List of correct answers (typically list of ints)
            • This may be determined randomly by the setup routine. If so, the setup_routine() should return the correct
            answer list, which will be stored to self.correct_answer_conditions
        :param map_input: Function to convert a raw button press into a comparable answer
            • This may be useful where multiple correct answers are possible
            • Returns the converted input for answer comparison
        :param input_as_linear_int: Tells the game to convert button value to button number 0-7 left to right
            • e.g. input of 8 = button 3
        :param show_button_feedback: Determines if a corresponding LED should light with a button press
        :param correct_answer_action: Function for correct action response (progress increment is handled automatically)
            • This may take an argument of 'progress' which will access the MiniGame's progress attribute
            • Returns the updated segment display
        :param incorrect_answer_action: Function for incorrect action response (life decrement is handled automatically)
            • Returns the updated progress
        """
        self.tm1638 = tm1638

        self.setup_routine: Callable = setup_routine

        # store conditions and actions for correct answers
        self.correct_answer_conditions: List[Optional[int]] = correct_answer_conditions
        self.map_input: Callable = map_input
        self.correct_answer_action: Callable = correct_answer_action
        self.incorrect_answer_action: Callable = incorrect_answer_action

        # UI variables
        self.game_seg_display: List[Any] = None
        self.game_LED_display: int = 0
        self.show_button_feedback: bool = show_button_feedback
        self.input_as_linear_int: bool = input_as_linear_int

        # monitoring variables
        self._win_length: int = win_length
        self._alive: bool = True
        self._lives: int = 2
        self._progress: int = 0
        self._show_final_display: bool = False
        self.test_mode: bool = test_mode

    def setup(self) -> None:
        """
        Setup actions for the MiniGme.
            Note: By default this is not called during class initiation to save memory when multiple MiniGame instances
            are registered.
        """
        # run the setup routine
        if self.setup_routine is not None:
            # inject any required self-stored objects into the function
            setup_routine_args = getfullargspec(self.setup_routine)._asdict()['args']
            setup_kwargs = {}
            if 'tm1638' in setup_routine_args:
                setup_kwargs['tm1638'] = self.tm1638

            # run the setup routine
            attr_dict = self.setup_routine(**setup_kwargs)
            for attr, value in attr_dict.items():
                setattr(self, attr, value)

        assert len(self.correct_answer_conditions) == self._win_length, \
            f"The Game has {self._win_length} completion steps and {self.correct_answer_conditions} step answers. " \
            f"This game may be unplayable!"


    @testing_wrapper(message="Game lost!")
    def _lose_screen(self) -> None:
        """
        Displays the game-over screen.
        """
        pass

    # @testing_wrapper(message="Game won!")
    def _win_screen(self) -> None:
        """
        Displays the win screen.
        """
        self.tm1638.display_line("--safe--")

    def _input_to_linear_int(self,
                             input_button: int) -> int:
        """
        Coverts the binary integer of the button input to a linear integer
        """
        linear_int = None
        for i in range(self.tm1638.num_leds + 1):
            if input_button == (1 << i):
                linear_int = i

        if self.test_mode:
            print(f"{input_button} converted to: {linear_int}")

        return linear_int

    def final_display(self,
                      set_lose: bool = False) -> None:
        """
        Shows the final screen for a game (win or lose).

        :param set_lose: Enables the game to be externally set to lost
        """
        if set_lose:
            self._alive = False
            self._show_final_display = True

        if self._alive:
            self._win_screen()
        else:
            self._lose_screen()

    def play(self, input_button: int) -> None:
        """
        Plays a turn.

        :param input_button: The switch input number as an int
        """
        # lock the game loop if won or lost
        if self._show_final_display:
            self.final_display()
            return

        # take action according to the turn input
        if self.input_as_linear_int:
            input_button = self._input_to_linear_int(input_button)
        if self.map_input:
            map_input_args = getfullargspec(self.map_input)._asdict()['args']
            map_input_kwargs = {arg: getattr(self, arg) for arg in map_input_args
                                if arg in self.__dict__}
            input_button = self.map_input(input_button, **map_input_kwargs)
        if input_button == self.correct_answer_conditions[self._progress]:
            self._progress += 1
            if self.correct_answer_action is not None:
                action_kwargs = {}
                correct_answer_action_args = getfullargspec(self.correct_answer_action)._asdict()['args']
                if 'input_button' in correct_answer_action_args:
                    action_kwargs['input_button'] = input_button
                if 'progress' in correct_answer_action_args:
                    action_kwargs['progress'] = self._progress
                if 'tm1638' in correct_answer_action_args:
                    action_kwargs['tm1638'] = self.tm1638
                self.game_seg_display = self.correct_answer_action(**action_kwargs)
        else:
            if self.incorrect_answer_action is not None:
                action_kwargs = {}
                incorrect_answer_action_args = getfullargspec(self.incorrect_answer_action)._asdict()['args']
                if 'input_button' in incorrect_answer_action_args:
                    action_kwargs['input_button'] = input_button
                if 'progress' in incorrect_answer_action_args:
                    action_kwargs['progress'] = self._progress
                if 'tm1638' in incorrect_answer_action_args:
                    action_kwargs['tm1638'] = self.tm1638
                self._progress = self.incorrect_answer_action(**action_kwargs)
            else:
                self.tm1638.display_line("Error")
                sleep(1)
            self._lives -= 1

        # take action if the game has been won or lost
        if self._progress == self._win_length:
            self._show_final_display = True
            self.final_display()
        elif self._lives < 0:
            self._alive = False
            self._show_final_display = True
            self.final_display()
        else:
            # show the game screen by default
            self.tm1638.LEDs(self.game_LED_display)
            self.tm1638.display_line(self.game_seg_display)


class SevenSegButtonGame:
    def __init__(self,
                 stb: int,
                 clk: int,
                 dio: int,
                 test_mode: bool = False) -> None:
        """
        7-segment button game main class

        This object can have multiple games assigned and selects one at random, then
        coordinates gameplay with the selected game.

        :param stb: Specifies the stb pin number
        :param clk: Specifies the clk pin number
        :param dio: Specifies the dio pin number
        """
        self.tm: TM1638Animated = TM1638Animated(stb=stb,
                                                 clk=clk,
                                                 dio=dio,
                                                 brightness=4,
                                                 test_mode=test_mode)

        self._game_register: Dict[str, MiniGame] = {}
        self.selected_game: Optional[MiniGame] = None

        # internal monitoring variables
        self._game_select: int = 0
        self._setup_run: bool = False

        # standby variables
        self.in_standby: bool = True
        self._standby_presses: int = 0

        # internal input monitoring variables
        self._is_pressed: bool = False

        self.test_mode = test_mode

    def register_game(self,
                      game_title: str,
                      game_object: MiniGame) -> None:
        """
        Enables the main object to register

        :param game_title: String of the game's name
        :param game_object: MiniGame object containing the game instance
        """
        assert not self._setup_run, "Games may not be registered after setup() is called"
        self._game_register[game_title] = game_object

        if game_object.tm1638 is None:
            game_object.tm1638 = self.tm

        game_object.test_mode = self.test_mode

    def _check_new_input(self) -> int:
        """
        This function gets the button input, but prevents single presses from being registered multiple times. While a
        button remains pressed, the function will return 0 after the first call, until all buttons are released.

        :return: Integer of allowed button input
        """
        key_pressed = int(self.tm.qyf_keys())
        if key_pressed > 0 and not self._is_pressed:
            self._is_pressed = True
            return key_pressed
        elif key_pressed == 0 and self._is_pressed:
            self._is_pressed = False
        return 0

    def setup(self,
              selected_game_name: str = None) -> None:
        """
        Runs the setup of the registered MiniGame.
            Note: all games should be registered before this function call

        :param selected_game_name: Enables a specific game to be selected and played
        """
        assert len(self._game_register) > 0, "No games registered! Please ragester at least 1 game."
        if selected_game_name is None:
            self._game_select = randint(0, len(self._game_register) - 1)
            selected_game_name = list(self._game_register.keys())[self._game_select]

        self.selected_game = self._game_register[selected_game_name]
        self.selected_game.setup()

        self._setup_run = True

    def show_selected_game(self) -> None:
        """
        Displays the selected game on the LED display by the number of lit LEDs
        """
        game_select_display = (1 << (self._game_select + 1)) - 1
        self.tm.clear_display()
        self.tm.roll()
        sleep(1)
        self.tm.clear_display()
        self.tm.LEDs_from_left(game_select_display)

    def standby_start_loop(self) -> None:
        """
        Executes game display then awaits user activation of the game(s)
        """
        # show selected game number and get the player input
        self.shows_elected_game()
        player_input = self._check_new_input()

        if player_input > 0:
            if player_input == 64:
                self.standby_presses += 1
            else:
                self.selected_game.final_display(set_lose=False)

        # exit standby mode if the correct button is pressed twice
        if self._standby_presses >= 2:
            self.in_standby = False
            self.tm.display_line(self.selected_game.game_seg_display)
            self.tm.LEDs(self.selected_game.game_LED_display)


    def game_loop(self) -> None:
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
            if self.selected_game.show_button_feedback:
                self.tm.LEDs(player_input)
            self.selected_game.play(player_input)
        elif self.selected_game.show_button_feedback:
            self.LEDs(0)
