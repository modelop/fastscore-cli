class AvroException(RuntimeError):
    """Exception for errors in deserializing or serializing Avro data."""
    pass

class SchemaParseException(RuntimeError):
    """Exception for errors in parsing an Avro schema."""
    pass

class FastScoreError(Exception):
    """
    A FastScore exception.

    SDK functions throw only FastScoreError exceptions. An SDK function
    either succeeds or throws an exception. The return value of a SDK function
    is always valid.
    """

    def __init__(self, message, caused_by=None):
        self.message = message
        self.caused_by = caused_by

    def __str__(self):
        if self.caused_by != None:
            return "Error: %s\n  Caused by: %s" % (self.message,self.caused_by)
        else:
            return "Error: %s" % self.message
