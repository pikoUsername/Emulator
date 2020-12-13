class BaseNotFound(Exception):
    def __init__(self, ctx):

class UserNotFound(BaseNotFound):
    pass
