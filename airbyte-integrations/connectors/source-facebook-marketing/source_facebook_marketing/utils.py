from datetime import datetime, timezone


class FutureDateException(Exception):
    def __init__(self, field_name, *args, **kwargs):
        self.field_name = field_name
        self.message = f"{self.field_name} cannot be in the future. Please set today's date or later"
        super().__init__(self.message, *args, **kwargs)

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.__str__()


def validate_date_field(field, date):
    if date > datetime.now(timezone.utc).replace(microsecond=0):
        raise FutureDateException(field)
    return date
