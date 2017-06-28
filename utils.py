from __future__ import print_function


class TFTUtils(object):
    """
    Utilities for the TensorFlow-Tacyt system.

    Attributes:
        VERBOSITY: verbosity level (0-3), default 0
                   set to max verbosity if verbosity entered
                   outside 0-3 range
    """

    # Define verbosity levels:
    SILENT = -1
    ERROR = 1
    WARNING = 2
    DEBUG = 3

    def __init__(self, verbosity=SILENT):
        if verbosity <= self.DEBUG and verbosity >= self.SILENT:
            self.VERBOSITY = verbosity
        else:
            self.VERBOSITY = self.DEBUG
        print("Verbosity level set to: ", self.VERBOSITY)

    def vPrint(self, message, verbosity=0):
        if verbosity <= self.VERBOSITY:
            print(message)
