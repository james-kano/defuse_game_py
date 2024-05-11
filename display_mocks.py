"""
File to render a mock-up of the tm1638 display (7-segment and LEDs).

To render the display in full, make the following calls in this order:
    led_mock.print_val(<value>)
    seg_mock.print_segs(<line>)
    
Appearance of rendered display:

     •   •   •   •   •   •   •   •  
     _   _   _   _   _   _   _   _  
    |_| |_| |_| |_| |_| |_| |_| |_| 
    |_|.|_|.|_|.|_|.|_|.|_|.|_|.|_|.
    
The printed (rendered) version shows bold red for illuminated and grey for off. Lit LEDs appear as a red star.
For colour-blindness accessibility, please comment out font.on and uncomment the alternative font.on for blue.

"""
from typing import Dict, List, Optional
from copy import deepcopy


class font:
    """
    class for ease of font changes
    """
    black: str = '\x1b[0m'
    off: str = '\033[97m' # grey
    on: str = '\x1b[31m' # red
    # on: str = '\033[94m' # blue
    bold: str = '\033[1m'
    
    
def colour_on(on_str: str) -> str:
        """
        Wraps a given string in on colouring (then returns to black)
        """
        return f"{font.bold}{font.on}{on_str}{font.black}"
    

def colour_off(off_str: str) -> str:
        """
        Wraps a given string in off colouring (then returns to black)
        """
        return f"{font.off}{off_str}{font.black}"
    

    
class seg_mock:
    """
    Class to represent a seven segment display and print the output
    """
    def __init__(self,
                 num_segs: int = 8) -> None:
        
        self.num_segs: int = num_segs
        self.display_bytes: List[int]
        self._ints: List[int] = [63, 6, 91, 79, 102, 109, 125, 7, 127, 111]
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
        
        
    def print_segs(self,
                   _input: Optional[float]) -> None:
        """
        The printing function to represent a single segment
        """
        if isinstance(_input, list):
            try:
                inputs = ''.join(_input)
            except:
                # list of ints provided
                inputs = deepcopy(_input)
        else:
            inputs = str(_input)
            
        # Detect the input mode (mappable character, mappable number, raw displayable bytes)
        input_modes = []
        for item in inputs:
            try:
                item = int(item)
                if item < len(self._ints):
                    input_modes.append('number')
                else:
                    input_modes.append('bytes')
            except:
                if item.lower() in self._chars:
                    input_modes.append('string')
                else:
                    raise Exception(f'Unsupported character passed in input: {item}')
                    
                    
        input_mode = 'bytes'
        if 'bytes' not in input_modes:
            if 'string' in input_modes:
                input_mode = 'string'
            else:
                input_mode = 'number'
                        
                        
        
        assert len(inputs) <= self.num_segs, f'Input cannot be longer than {self.num_segs}'
        # render any unused segments
        if len(inputs) < self.num_segs:
            if input_mode == 'bytes':
                while len(inputs) < self.num_segs:
                    inputs.append(0)
            else:
                inputs += ' ' * (self.num_segs - len(inputs))
        
            
        # Segment element orders:
        #               [dot,  m,   tl,  bl,  b,   br,  tr,  t]
        element_chars = ['.', '_', '|', '|', '_', '|', '|', '_',]            
            
        tops = []
        mids = []
        bottoms = []
        
        input_i = 0
        
        while input_i < len(inputs):
            
            # Cycle through individual characters and render
            if input_mode == 'number':
                input_int = int(inputs[input_i])
                input_int = self._ints[input_int]
            elif input_mode == 'string':
                # Can be alphanumeric
                try:
                    input_int = int(inputs[input_i])
                    input_int = self._ints[input_int]
                except:
                    input_int = self._chars[inputs[input_i].lower()]
            else:
                # Input must be displayed as a raw byte (unmapped value)
                input_int = int(inputs[input_i])
                
            # Handle the dot if provided
            if input_i+1 < len(inputs):
                if inputs[input_i+1] == '.':
                    input_int += self._dot
                    input_i += 1
            
            # Convert to binary byte from binary values
            input_byte_str = str(format(input_int, '08b'))
                        
            # Covent the byte into individual lights (elements on/off)
            display_elements = []
            i_val = 0
            for val in input_byte_str:
                val = int(val)
                if val:
                    display_elements.append(colour_on(element_chars[i_val]))
                else:
                    display_elements.append(colour_off(element_chars[i_val]))
                i_val += 1
            
            
            tops.append(f' {display_elements[7]}  ')
            mids.append(f'{display_elements[2]}{display_elements[1]}{display_elements[6]} ')
            bottoms.append(f'{display_elements[3]}{display_elements[4]}{display_elements[5]}{display_elements[0]}')
        
            input_i += 1
        
                                
        print("".join(tops))
        print("".join(mids))
        print("".join(bottoms))



class led_mock:
    """
    Class to represent a tm1638 LED display and print the output
    """
    def __init__(self,
                 num_leds: int) -> None:
        self.num_leds: int = num_leds
        self.display_bits: List[int]    
    
        
    def print_val(self,
                  value: int) -> None:
        """
        Prints the LEDs as a binary representation of an integer
        """
        bin_format = f"0{self.num_leds}b"
        bin_str = str(format(value, bin_format))
        test_print_list = [colour_on(' *  ') if digit == '1' 
                           else colour_off(' •  ') 
                           for digit in bin_str]
        print("".join(test_print_list))
    
    
    def print_val_from_left(self,
                            value: int) -> None:
        """
        Prints the number as number of LEDs lit
        """
        test_print_list = [colour_on(' *  ') if i < value
                           else colour_off(' •  ')
                           for i in range(self.num_leds)]
        print("".join(test_print_list))
        
    
        
    