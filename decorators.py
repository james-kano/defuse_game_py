"""
Decorators used to add intermediary or inverse-specification style testing to functions
"""

import functools

def testing_wrapper(message,
                    test_and_run = False,
                    test_mode_attr = 'test_mode'):
    """
    Prints a testing message and may / may not run the function as desired.

    DESIGNED FOR CLASS FUNCTIONS (hence use of self_obj for self passthrough)

    :param message: the test message to be printed.
    :param test_and_run: defaults to False. if True, the wrapper will pring the tests statement AND execute the
        function passed in.
    """
    def testing_wrapper_decorator(func):
        @functools.wraps(func)
        def print_test_message(self_obj, *args, **kwargs):
            # obj is substitution for self

            if getattr(self_obj, test_mode_attr):
                print(message)
                if args or kwargs:
                    print(f'args: {args}, kwargs: {kwargs}')
                if test_and_run:
                    return func(self_obj, *args, **kwargs)
            else:
                return func(self_obj, *args, **kwargs)
            
        return print_test_message
    return testing_wrapper_decorator
