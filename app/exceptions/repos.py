class NotFoundException(Exception):
    pass


class UniqueViolationException(Exception):
    pass


class ForeignKeyViolationException(Exception):
    pass


class NotNullViolationException(Exception):
    pass
