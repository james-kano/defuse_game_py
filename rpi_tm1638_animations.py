# """
# TM1638 Animation library adds animations to Mike Causer's TM1628 Micropython library
#
# Copyright (C) 2023  James Kano
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# This program requires the TM1638 library written by Mike Causer (2018):
#     MicroPython TM1638 7-segment LED display driver with keyscan
#     Copyright (c) 2018 Mike Causer
#     https://github.com/mcauser/micropython-tm1638
# """

from decorators import testing_wrapper

class TM1638Animated():
    """
    TM1638Animated implements existing TM1638 library to add animations.
    """
    def __init__(self,
                 stb,
                 clk,
                 dio,
                 brightness = 7,
                 test_mode = False) -> None:

        self.num_segments = 8
        self.num_leds = 8

        if not test_mode:
            from drivers.rpi_TM1638.TMBoards import TMBoards
            from machine import Pin
            self.TM1638 = TMBoards(stb=Pin(stb),
                                   clk=Pin(clk),
                                   dio=Pin(dio),
                                   brightness=brightness)

            self.num_segments = 8 * self.TM1638.nbBoards # number of seven-segment displays on board
        self.test_mode = test_mode

    @testing_wrapper(message="Performing <ROLL animation>")
    def roll(self,
             speed = 250):
        """
        Roll animation
        :param speed: controls the speed of animation.
        """
        pass

    @testing_wrapper(message="Performing <WAVE animation>")
    def wave(self,
             speed = 250):
        """
        Wave animation
        :param speed: controls the speed of animation.
        """
        pass

    @testing_wrapper(message="Performing <LOAD animation>")
    def load(self,
             speed = 250):
        """
        Load animation
        :param speed: controls the speed of animation.
        """
        pass

    @testing_wrapper(message="Performing <UNLOAD animation>")
    def unload(self,
               speed = 250):
        """
        Unload animation
        :param speed: controls the speed of animation.
        """
        pass

    @testing_wrapper(message="Performing <display LINE>")
    def display_line(self,
                     line):
        """
        Displays a line of custom values
        :param line:
        """
        assert len(line) <= self.num_segments, \
            f"This board is currently configured for a maximum of {self.num_segments} segment displays. " \
            "Use self.scroll() for longer display lines"
        for i in range(len(line)):
            self.write(line[i], i)

    def LEDs(self,
             value: int) -> None:
        """
        Displays LEDs based on binary integer from right
        """
        if self.test_mode:
            bin_format = f"0{self.num_leds}b"
            bin_str = str(format(value, bin_format))
            test_print_list = ['*' if digit == '1' else 'O' for digit in bin_str]
            test_print_list = str(test_print_list).replace(',', '').replace("'", '')
            print(f"LEDs: {test_print_list}")

        # ToDo: add the interface to the driver to display as required

    def LEDs_from_left(self,
                       value: int) -> None:
        """
        Displays a number expressed as LEDs illuminated from the left
        e.g. 4 = 1,1,1,1,0,0,0,0 (first 4 leds illuminated)
        """
        if self.test_mode:
            test_print_list = ["*" if i < value
                               else "O"
                               for i in range(self.num_leds)]
            test_print_list = str(test_print_list).replace(',', '').replace("'", '')
            print(f"LEDs: {test_print_list}")
            return

        # ToDo: add the interface to the driver to display as required

    @testing_wrapper(message="<clear dislpay>")
    def clear_display(self):
        """
        Clears the display
        """
        self.TM1638.clearDisplay()




# ToDo:
# - Add roll / wave / load / unload etc.
# - Add ability to write custom values to display.
