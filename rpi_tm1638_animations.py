"""
TM1638 Animation library adds animations to Mike Causer's TM1628 Micropython library

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

This program requires the TM1638 library written by Mike Causer (2018):
    MicroPython TM1638 7-segment LED display driver with keyscan
    Copyright (c) 2018 Mike Causer
    https://github.com/mcauser/micropython-tm1638

Please install the library using the library's included setup.py to enable importing in this file.
    Command example: python3 rpi-TM1638/setup.py install

    Note: the import for this is only used in TM1638Animated if not in test_mode. This enables test_mode
    to be run on non raspberry pi devices that do not have GPIO etc.
"""

from decorators import testing_wrapper
from display_mocks import seg_mock, led_mock
from rpi_tm1638_overrides import SegmentsOverride


class TM1638Animated():
    """
    TM1638Animated implements existing TM1638 library to add animations.
    """
    def __init__(self,
                 stb: int,
                 clk: int,
                 dio: int,
                 brightness: int = 1,
                 test_mode: bool = False) -> None:

        self.num_segments = 8
        self.num_leds = 8

        self.TM1638 = None

        if not test_mode:
            # from rpi_TM1638.TMBoards import TMBoards
            from drivers.rpi_TM1638.TMBoards import TMBoards
            self.TM1638 = TMBoards(stb=stb,
                                   clk=clk,
                                   dio=dio,
                                   brightness=brightness)
            # Functionally extend the TM driver
            self.TM1638._segments = SegmentsOverride(self.TM1638)

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

    def display_line(self,
                     line):
        """
        Displays a line of custom values
        :param line:
        """
        assert len(line) <= self.num_segments, \
            f"This board is currently configured for a maximum of {self.num_segments} segment displays. " \
            "Use self.scroll() for longer display lines"

        if self.test_mode:
            test_seg = seg_mock()
            test_seg.print_segs(line)
            return

        self.TM1638.segments[0] = line

    def LEDs(self,
             value: int) -> None:
        """
        Displays LEDs based on binary integer from right
        """
        if self.test_mode:
            test_leds = led_mock(self.num_leds)
            test_leds.print_val(value)
            return

        # ToDo: add the interface to the driver to display as required

    def LEDs_from_left(self,
                       value: int) -> None:
        """
        Displays a number expressed as LEDs illuminated from the left
        e.g. 4 = 1,1,1,1,0,0,0,0 (first 4 leds illuminated)
        """
        if self.test_mode:
            test_leds = led_mock(self.num_leds)
            test_leds.print_val_from_left(value)
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
