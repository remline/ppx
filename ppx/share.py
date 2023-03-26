"""Shared definitions"""

from enum import Enum

class Mode(Enum):
    """Processing mode"""
    NORMAL = 0
    FOOTNOTES = 1
    TN_DEL = 2
    TN_INS = 3

class Processing(Enum):
    """Instruct the processor to skip parts of an element"""
    SKIP_DATA = 0 # Skip this tag's text and children
    SKIP_TAIL = 1 # Skip this tag's tail
