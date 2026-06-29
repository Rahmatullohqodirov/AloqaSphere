import re
from django.core.exceptions import ValidationError
def phone_number_validation(data):
    pattern = re.compile(r"\+998\d{2}\d{7}")
    if not pattern.match(data):
        raise ValidationError("number is wrong, example number is +998771234567")
    return data 