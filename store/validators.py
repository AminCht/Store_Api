from django.core.exceptions import ValidationError


def validate_file_size(file):
    max_file_size = 0.1
    if file.size > max_file_size * 1024:
        raise ValidationError(f'Uploaded files can not be larger than{max_file_size} KB')