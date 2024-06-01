from .rpi_tm1638_animations import TM1638Animated
import time

anim = TM1638Animated(stb=26, clk=13, dio=19)
anim.roll()
anim.wave()
anim.load()
anim.unload()
anim.LEDs_from_left(8)
time.sleep(5)
anim.LEDs_from_left(4)
time.sleep(5)
anim.clear_display()
