"""
File to print out mock-ups of the tm1638 display (7-segment and LEDs)
"""
from typing import Dict, List, Optional


class font:
    """
    class for ease of font changes
    """
    black: str = '\x1b[0m'
    grey: str = '\033[97m'
    red: str = '\x1b[31m'
    bold: str = '\033[1m'
    

class seg_mock:
    """
    Class to represent a seven segment display and print the output
    """
    def __init__(self,
                 num_segs: int = 1):
        
        self.num_segs: int = num_segs
        self.display_bytes: List[int]
        self._ints: List[int] = [63, 6, 91, 79, 102, 109, 125, 7, 127, 111] #103
        self._chars: Dict[str, int] = {'-': 64,
                                       '_': 8,
                                       ' ': 0,
                                       'a': 119,
                                       'e': 121,
                                       'f': 113,
                                       'o': 92,
                                       'r': 80,
                                       's': 109}
        self._dot: int = 128
        
        
    def _colour_red(self,
                    red_str: str) -> str:
        """
        Wraps a given string in red colouring (then returns to black)
        """
        return f"{font.bold}{font.red}{red_str}{font.black}"
    
    def _colour_grey(self,
                     grey_str: str) -> str:
        """
        Wraps a given string in grey colouring (then returns to black)
        """
        return f"{font.grey}{grey_str}{font.black}"
        
        
    def print_segs(self,
                   _input: Optional[float]):
        """
        The printing function to represent a single segment
        """
        
        if isinstance(_input, list):
            try:
                inputs = ''.join(_input)
            except:
                inputs = _input
        else:
            inputs = str(_input)
        
            
        # Segment element orders:
        #               [dot,  m,   tl,  bl,  b,   br,  tr,  t]
        element_chars = ['.', '_', '|', '|', '_', '|', '|', '_',]            
            
        tops = []
        mids = []
        bottoms = []
        
        input_i = 0
        while input_i < len(inputs):
        
            try:
                input_int = int(inputs[input_i])
                input_int = self._ints[input_int]
            except:
                input_int = self._chars[inputs[input_i].lower()]
                
            # Handle the dot if provided
            if input_i+1 < len(inputs):
                if inputs[input_i+1] == '.':
                    input_int += self._dot
                    input_i += 1
            
            # Convert to binary byte fro binary values
            input_byte_str = str(format(input_int, '08b'))
            
            # Covent the byte into individual lights (elements on/off)
            display_elements = []
            i_val = 0
            for val in input_byte_str:
                val = int(val)
                if val:
                    display_elements.append(self._colour_red(element_chars[i_val]))
                else:
                    display_elements.append(self._colour_grey(element_chars[i_val]))
                i_val += 1
            
            
            tops.append(f' {display_elements[7]}  ')
            mids.append(f'{display_elements[2]}{display_elements[1]}{display_elements[6]} ')
            bottoms.append(f'{display_elements[3]}{display_elements[4]}{display_elements[5]}{display_elements[0]}')
        
            input_i += 1
        
                                
        print("".join(tops))
        print("".join(mids))
        print("".join(bottoms))