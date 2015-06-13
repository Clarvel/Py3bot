class IRCError(Exception):
    """
    Exception thrown by IRC command handlers to notify client of a
    server/client error.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)