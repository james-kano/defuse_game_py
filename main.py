from machine import Pin
from random import randint
from time import sleep_ms

from pico_tm1638_animations import TM1638Animated
# from seg_game_tmp import SevenSegButtonGame


class TEST_TM1638(TM1638Animated):
    """
    TM1638Animated inherits from to add animations to the
    existing TM1638 library
    """
    def __init__(self,
                 stb,
                 clk,
                 dio,
                 brightness = 7):

        super().__init__(stb=stb, clk=clk, dio=dio, brightness=brightness)

        self.num_segments = 8 # number of seven-segment displays on board


tm = TEST_TM1638(stb=Pin(2), clk=Pin(3), dio=Pin(4))

tm2 = TEST_TM1638(stb=Pin(2), clk=Pin(3), dio=Pin(4))

# tm = SevenSegButtonGame(stb=2, clk=3, dio=4)


for pos in range(8):
    tm.led(pos, True)
    sleep_ms(200)

sleep_ms(500)

for pos in range(8):
    tm2.led(pos, False)
    sleep_ms(200)
