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

from drivers.rpi_TM1638.TMBoards import TMBoards

class TM1638Animated(TMBoards):
    """
    TM1638Animated inherits from to add animations to the
    existing TM1638 library
    """
    def __init__(self,
                 stb,
                 clk,
                 dio,
                 brightness = 7) -> None:
        super().__init__(stb=stb,
                         clk=clk,
                         dio=dio,
                         brightness=brightness)

        self.num_segments = 8 * self.nbBoards # number of seven-segment displays on board

    def roll(self,
             speed = 250):
        """
        Roll animation
        :param speed: controls the speed of animation.
        """
        pass

    def wave(self,
             speed = 250):
        """
        Wave animation
        :param speed: controls the speed of animation.
        """
        pass

    def load(self,
             speed = 250):
        """
        Load animation
        :param speed: controls the speed of animation.
        """
        pass

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
        for i in range(len(line)):
            self.write(line[i], i)

# ToDo:
# - Add wave / load / unload etc.
# - Add ability to write custom values to display.
