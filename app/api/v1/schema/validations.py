import re
from marshmallow import ValidationError
from app import app
from flask_babel import _


def validate_name(val):
    """Validate username format."""
    match = re.match(r'^(?! )[A-Za-z0-9 ]*[^\x01-\x1F]{0,1000}(?<! )$', val)
    if len(val) < 1:
        raise ValidationError(_("name should contain more than one character"))
    if len(val) > 1000:
        raise ValidationError(_("name cannot contain more than 1000 characters"))
    if match is None:
        raise ValidationError(_("Name cannot contain invalid characters"))


def validate_comment(val):
    """Validate comment format."""
    match = re.match(r'^(?! )[A-Za-z0-9 ]*[^\x01-\x1F]{0,1000}(?<! )$', val)
    if len(val) < 1:
        raise ValidationError(_("Comment should contain more than one character"))
    if len(val) > 1000:
        raise ValidationError(_("Comment cannot contain more than 1000 characters"))
    if match is None:
        raise ValidationError(_("Comment cannot have invalid characters"))


def validate_number(val):
    """Validate phone number format."""
    match = re.match('^\+?[0-9]{7,15}$', val)
    if match is None:
        raise ValidationError(_("Alternate phone number is invalid."))


def validate_date(val):
    """Validate date format."""
    match = re.match('^((19|20)\d{2})\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$', str(val))
    if match is None:
        raise ValidationError(_("Invalid date format"))


def validate_imei(val):
    """Validate IMEI format."""
    match = re.match('^[a-fA-F0-9]{14,16}$', val)
    if len(val) < app.config['system_config']['global'].get('min_imei_length'):
        raise ValidationError(_("IMEI too short, should contain at least {min} characters").format(min=app.config['system_config']['global'].get('min_imei_length')))
    if len(val) > app.config['system_config']['global'].get('max_imei_length'):
        raise ValidationError(_("IMEI too long, cannot contain more than {max} characters").format(max= app.config['system_config']['global'].get('max_imei_length')))
    if match is None:
        raise ValidationError(_("IMEI is invalid."))


def validate_msisdn(val):
    """Validate MSISDN format."""
    match = re.match('^\+?[0-9]{7,15}$',val)
    if match is None:
        raise ValidationError(_("MSISDN is invalid."))


def validate_gin(val):
    """Validate government identification number format."""
    match = re.match(app.config['system_config']['global'].get('gin_regex'), val)
    if match is None:
        raise ValidationError(_("Government Identification Number must contain {range} digits").format(range=app.config['system_config']['global'].get('gin_length')))


def validate_others(val, min_range, max_range, field):
    """Validate other fields format."""
    if len(val) < min_range:
        raise ValidationError(_("{field} should contain at least {min} character").format(field=field, min=min_range))
    if len(val) > max_range:
        raise ValidationError(_("{field} cannot contain more than {max} characters").format(field=field, max=max_range))