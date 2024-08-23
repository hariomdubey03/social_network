from cerberus import Validator
import re


class CustomValidator(Validator):
    def _validate_regex(self, regex, field, value):
        """Override the default regex validation error message"""
        if not re.match(regex, value):
            self._error(field, f"Invalid {field}")
