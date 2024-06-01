# coding=utf-8

"""
setup.py file for the rpi-TM1638 game engine and driver enhancements.

This enables easy creation of puzzle games on the TM1638 interface board with Raspberry Pi.

Copyright (C) 2024  James Kano

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

The package is designed to be compatible with the TM1638 library written by Mike Causer (2018) or similar:
    MicroPython TM1638 7-segment LED display driver with keyscan
    Copyright (c) 2018 Mike Causer
    https://github.com/mcauser/micropython-tm1638


see https://github.com/james-kano/defuse_game_py
"""

from setuptools import setup

setup(name='tm1638_game_engine',
      version='0.1',
      description='A Raspberry Pi game engine for TM1638 boards',
      keywords='TM1638 puzzle game engine raspberry pi',
      url='https://github.com/james-kano/defuse_game_py',
      author='James Kano',
      license='GPL3',
      packages=['tm1638_game_engine'],
      install_requires=['rpi_TM1638'],
      include_package_data=True,
      zip_safe=False)
