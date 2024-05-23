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
import time

from decorators import testing_wrapper
from display_mocks import seg_mock, led_mock


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

        self.num_segments: int = 8
        self.num_leds: int = 8

        self.TM1638: object = None

        if not test_mode:
            from rpi_TM1638.TMBoards import TMBoards
            from rpi_tm1638_overrides import SegmentsOverride
            # from drivers.rpi_TM1638.TMBoards import TMBoards
            self.TM1638: TMBoards = TMBoards(stb=stb,
                                             clk=clk,
                                             dio=dio,
                                             brightness=brightness)
            # Functionally extend the TM driver
            self.TM1638._segments = SegmentsOverride(self.TM1638)

            self.num_segments: int = 8 * self.TM1638.nbBoards # number of seven-segment displays on board

            self.leds = self.TM1638.leds
            self.segments = self.TM1638.segments
            self.switches = self.TM1638.switches

        self.test_mode: bool = test_mode
        self.bit_format: str = f'0{self.num_segments}b'


    @testing_wrapper(message="Performing <ROLL animation>")
    def roll(self,
             speed: int = 10,
             rolls: int = 3):
        """
        Roll animation
        :param speed: controls the speed of animation.
        :param rolls: number of rolls to be executed.
        """
        self.clear_display()
        for num in range(rolls):
            led_bit = 1
            while led_bit < 64:
                line = [led_bit for i in range(self.num_segments)]
                self.display_line(line)
                led_bit = led_bit << 1
                time.sleep(1/speed)

    @testing_wrapper(message="Performing <WAVE animation>")
    def wave(self,
             speed: int = 10,
             waves: int = 2):
        """
        Wave animation
        :param speed: controls the speed of animation.
        :param waves: number of waves to display.
        """
        self.clear_display()
        for wave in range(waves):
            for place in range(6):
                line = [1 << pos + place if pos + place < 6
                        else 1 << pos + place - 6
                        for pos in range(8)]
                self.display_line(line)
                time.sleep(1/speed)

    @testing_wrapper(message="Performing <LOAD animation>")
    def load(self,
             speed: int = 10):
        """
        Load animation
        :param speed: controls the speed of animation.
        """
        self.clear_display()
        for pos in range(self.num_segments):
            self.display_line(' .' * pos)
            time.sleep(1/speed)

    @testing_wrapper(message="Performing <UNLOAD animation>")
    def unload(self,
               speed: int = 10):
        """
        Unload animation
        :param speed: controls the speed of animation.
        """
        self.clear_display()
        pos = self.num_segments
        while pos >= 0:
            self.display_line(' ' * self.num_segments)
            self.display_line(' .' * pos)
            pos -= 1
            time.sleep(1/speed)

    def display_line(self,
                     line: str):
        """
        Displays a line of custom values
        :param line:
        """
        check_line = line
        if isinstance(line, str):
            check_line = line.replace('.', '')
            line = f"{line}{' ' * (self.num_segments - len(line))}"
        elif isinstance(line, float):
            check_line = str(line).replace('.', '')
        assert len(check_line) <= self.num_segments, \
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
        Displays LEDs based on binary form of integer as byte

        NOTE: to display the LED based in the LED's integer number, use leds[i] = <bool>
        """
        if self.test_mode:
            test_leds = led_mock(self.num_leds)
            test_leds.print_val(value)
            return

        # Output the LED value
        val_byte = str(format(value, self.bit_format))
        val_i = 0
        for bit in val_byte:
            self.TM1638.leds[val_i] = int(bit)
            val_i += 1

    def LEDs_from_left(self,
                       value: int) -> None:
        """
        Displays a number expressed as LEDs illuminated from the left
        e.g. 4 = 1,1,1,1,0,0,0,0 (first 4 LEDs illuminated)
        """
        if self.test_mode:
            test_leds = led_mock(self.num_leds)
            test_leds.print_val_from_left(value)
            return

        # Clear and output LEDs
        for led in range(self.num_segments):
            self.TM1638.leds[led] = False or (led < value)

    @testing_wrapper(message="<clear display>")
    def clear_display(self):
        """
        Clears the display
        """
        self.TM1638.clearDisplay()

    def check_button_values(self) -> int:
        """
        Returns the value of any button presses as an integer representation of a byte
            e.g. second button from right -> 00000010 = 2
        """
        buttons_pressed = []
        for button in range(self.num_segments):
            buttons_pressed.append(str(int(self.switches[button])))

        buttons_str = ''.join(buttons_pressed)
        button_int = int(buttons_str, 2)

        # sleep 0.05 prevents the board getting confused
        time.sleep(0.05)
        return button_int
