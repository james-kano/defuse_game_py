"""
Overrides for the base TMBoards drivers. Base drivers are commonly available in many forks. This
extends functionality of those drivers without creating dependencies on a particular fork.

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

Classes given below are modifications of the TM1638 library written by Mike Causer (2018):
    MicroPython TM1638 7-segment LED display driver with keyscan
    Copyright (c) 2018 Mike Causer
    https://github.com/mcauser/micropython-tm1638
"""

from rpi_TM1638.TMBoards import TMBoards
from rpi_TM1638.TMBoards import Segments
# from drivers.rpi_TM1638.TMBoards import Segments


class SegmentsOverride(object):
	"""
	Class to extend manipulation of the 7-segment displays on the chained TM Boards.
	Wraps the Segments class to enable direct value writes to the segments (this allows individual LEDs
	within the segments to be illuminated even if the value does not represent a character or symbol).
	"""
	def __init__(self, TM):
		"""Initialize the Segment object"""
		self._TM = TM
		self._base_segments = Segments(self._TM)
		self._intern = self._base_segments._intern

	def __setitem__(self, index, value):
		"""
		Extends Segments.__setitem__() to enable writing specified (unmapped) values directly to the segment
		displays.

		:param index: index of the 7-segment, or tuple (i,j)
		:param value: string (or one-character string) when index is a int, otherwise a boolean
		"""
		try:
			self._base_segments[index] = value

		except ValueError:


			if isinstance(index, int):
				# parse string to transform it in list of 8-bit int to send to the TM1638
				# -> allows to parse the '.' characters
				lv = []
				for c in value:
					lv.append(c)
				# send every display if something has changed
				for val in lv:
					# check if something change (otherwise do not send data, it's useless)
					if self._intern[index] != val:
						# store the new intern value
						self._intern[index] = val
						# send the data to the TM
						self._TM.sendData((index % 8) * 2, val, index // 8)
					index += 1

			elif isinstance(index, (list, tuple)):
				# get the 7-segment display index and the led index
				i, j = index
				# determine the new intern value
				if value:
					self._intern[i] |= 1 << j
				else:
					self._intern[i] &= ~(1 << j)
				# send the data to the TM
				self._TM.sendData((i % 8) * 2, self._intern[i], i // 8)