# utility functions
import json

from string import printable
from binascii import b2a_hex

def compare_items(obj1, obj2, f_error):
    """
    Compares two JSON objects. Nonzero float fields are compared using :func:`compare_floats`

    :param obj1: The first object
    :param obj2: The second object
    :param f_error: A margin of error
    """
    if type(obj1) != type(obj2):
        print('Type mismatch: ' + str(type(obj1)) + ' != ' + str(type(obj2)))
        return False
    if type(obj1) is list:
        if len(obj1) != len(obj2):
            print('Length mismatch: ' + str(len(obj1)) + ' != ' + str(len(obj2)))
            return False
        length = len(obj1)
        for i in range(0, length):
            if compare_items(obj1[i], obj2[i], f_error) == False:
                return False
        return True
    if type(obj1) is dict:
        keys1 = sorted(obj1.keys())
        keys2 = sorted(obj2.keys())
        if keys1 != keys2:
            print('Key mismatch')
            return False
        for key in keys1:
            if compare_items(obj1[key], obj2[key], f_error) == False:
                return False
        return True
    if type(obj1) is float:
        matches = compare_floats(obj1, obj2, f_error)
        if not matches:
            print('Outside error margin')
        return matches
    return obj1 == obj2

def compare_floats(float1, float2, f_error=0.01, zero_tolerance=1e-8, inf_tolerance=1e80):
    """
    Compare two numeric objects according to the following algorithm:

    1. If float1 < zero_tolerance and float2 < zero_tolerance, then returns True.
    2. If abs(float1) > inf_tolerance and abs(float2) > inf_tolerance, and
       sign(float1) = sign(float2), then returns True.
    3. If zero_tolerance < abs(float1, float2) < inf_tolerance, and
       2*abs(float1 - float2)/(abs(float1) + abs(float2)) <= f_error, return True.
    4. Otherwise, return False.

    :param float1: First numeric field.
    :param float2: Second numeric field.

    :param f_error: Fractional margin of error (default: 0.01)
    :param zero_tolerance: Zero tolerance (default: 1e-8)
    :param inf_tolerance: Infinite tolerance (default: 1e80)
    """
    if abs(float1) < zero_tolerance and abs(float2) < zero_tolerance:
        return True
    elif abs(float1) > inf_tolerance and abs(float2) > inf_tolerance:
        if float1/float2 > 0:
            return True
        else:
            return False
    elif 2*abs(float1 - float2)/(abs(float1) + abs(float2)) <= f_error:
        return True
    else:
        return False

def ts(avroType):
    """Create a human-readable type string of a type.

    :type avroType: codec.datatype.AvroType
    :param avroType: type to print out
    :rtype: string
    :return: string representation of the type.
    """
    return repr(avroType)

uniqueFixedNameCounter = 0
def uniqueFixedName():
    """Provide a fixed type name, incrementing
    fastscore.utils.uniqueFixedNameCounter to ensure uniqueness of values
    supplied by this function."""
    sys.modules["fastscore.utils"].uniqueFixedNameCounter += 1
    return "Fixed_{0}".format(sys.modules["fastscore.utils"].uniqueFixedNameCounter)

uniqueEngineNameCounter = 0
def uniqueEngineName():
    """Provide an engine name, incrementing fastscore.utils.uniqueEngineNameCounter
    to ensure uniqueness of values supplied by this function."""
    sys.modules["fastscore.utils"].uniqueEngineNameCounter += 1
    return "Engine_{0}".format(sys.modules["fastscore.utils"].uniqueEngineNameCounter)

uniqueRecordNameCounter = 0
def uniqueRecordName():
    """Provide a record type name, incrementing fastscore.utils.uniqueRecordNameCounter
    to ensure uniqueness of values supplied by this function."""
    sys.modules["fastscore.utils"].uniqueRecordNameCounter += 1
    return "Record_{0}".format(sys.modules["fastscore.utils"].uniqueRecordNameCounter)

uniqueEnumNameCounter = 0
def uniqueEnumName():
    """Provide an enum type name, incrementing fastscore.utils.uniqueEnumNameCounter
    to ensure uniqueness of values supplied by this function."""
    sys.modules["fastscore.utils"].uniqueEnumNameCounter += 1
    return "Enum_{0}".format(sys.modules["fastscore.utils"].uniqueEnumNameCounter)

def format_record(rec, seqno=1):
    """Format a data record for printing."""

    if all([ x in printable for x in rec ]):
        return "{:4d}: {}".format(seqno, rec)
    else:

##   1: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  0123456701234567
##      01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01

        chunks = [ rec[s:s + 16] for s in range(0, len(rec), 16) ]
        if chunks == []:
            return "{:4d}: (empty)".format(seqno)
        else:
            lines = []
            lines.append("{:4d}: {}  {}".format(seqno, hex_pane(chunks[0]), str_pane(chunks[0])))
            for x in chunks[1:]:
                lines.append("      {}  {}".format(hex_pane(x), str_pane(x)))
            return "\n".join(lines)

def hex_pane(s):
    x = [ b2a_hex(s[i]) if i < len(s) else "  " for i in range(16) ]
    return " ".join(x)

def str_pane(s):
    x = [ s[i] if i < len(s) and s[i] in printable else '.' for i in range(16) ]
    return "".join(x)

