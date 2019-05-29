import re
from marshmallow import ValidationError
from app import app
from flask_babel import _


def validate_username(val):
    """Validate username format."""
    if len(val) < 1:
        raise ValidationError(_("Username should contain more than one character"))
    if len(val) > 1000:
        raise ValidationError(_("Username cannot contain more than 1000 characters"))
    match = re.match(app.config['system_config']['regex'][app.config['system_config']['language_support']['default']]['username'],val)
    if match is None:
        raise ValidationError(_("Username is invalid. Does not match the selected language or invalid format."))


def validate_fullname(val):
    """Validate username format."""
    if len(val) < 1:
        raise ValidationError(_("Fullname should contain more than one character"))
    if len(val) > 1000:
        raise ValidationError(_("Fullname cannot contain more than 1000 characters"))
    match = re.match(app.config['system_config']['regex'][app.config['system_config']['language_support']['default']]['full_name'],val)
    if match is None:
        raise ValidationError(_("Fullname is invalid. Does not match the selected language or invalid format."))


def validate_comment(val):
    """Validate comment format."""
    if len(val) < 1:
        raise ValidationError(_("Comment should contain more than one character"))
    if len(val) > 1000:
        raise ValidationError(_("Comment cannot contain more than 1000 characters"))
    match = re.match(app.config['system_config']['regex'][app.config['system_config']['language_support']['default']]['case_comment'],val)
    if match is None:
        raise ValidationError(_("Comment is invalid. Does not match the selected language or invalid format."))


def validate_description(val):
    """Validate comment format."""
    if len(val) < 1:
        raise ValidationError(_("Description should contain more than one character"))
    if len(val) > 1000:
        raise ValidationError(_("Description cannot contain more than 1000 characters"))
    match = re.match(app.config['system_config']['regex'][app.config['system_config']['language_support']['default']]['description'],val)
    if match is None:
        raise ValidationError(_("Description is invalid. Does not match the selected language or invalid format."))


def validate_number(val):
    """Validate phone number format."""
    match = re.match(app.config['system_config']['validation'].get('number'), val)
    if match is None:
        raise ValidationError(_("Alternate phone number is invalid."))


def validate_date(val):
    """Validate date format."""
    match = re.match(app.config['system_config']['validation'].get('date'), str(val))
    if match is None:
        raise ValidationError(_("Invalid date format"))


def validate_imei(val):
    """Validate IMEI format."""
    match = re.match(app.config['system_config']['validation'].get('imei'), val)
    min_imei_length = app.config['system_config']['global'].get('min_imei_length')
    max_imei_length = app.config['system_config']['global'].get('max_imei_length')
    if len(val) < min_imei_length:
        raise ValidationError(_("IMEI too short, should contain at least %(min)s characters", min=min_imei_length))
    if len(val) > max_imei_length:
        raise ValidationError(_("IMEI too long, cannot contain more than %(max)s characters", max=max_imei_length))
    if match is None:
        raise ValidationError(_("IMEI is invalid."))


def validate_msisdn(val):
    """Validate MSISDN format."""
    match = re.match(app.config['system_config']['validation'].get('number'),val)
    if match is None:
        raise ValidationError(_("MSISDN is invalid."))


def validate_gin(val):
    """Validate government identification number format."""
    match = re.match(app.config['system_config']['validation'].get('gin'), val)
    gin_length = app.config['system_config']['global'].get('gin_length')
    if match is None:
        raise ValidationError(_("Government Identification Number must contain %(range)s digits", range=gin_length))


def validate_address(val):
    """Validate other fields format."""
    if len(val) < 1:
        raise ValidationError(_("Address should contain at least 1 character"))
    if len(val) > 1000:
        raise ValidationError(_("Address cannot contain more than 1000 characters"))
    match = re.match(app.config['system_config']['regex'][app.config['system_config']['language_support']['default']]['address'],val)
    if match is None:
        raise ValidationError(_("Address is invalid. Does not match the selected language or invalid format."))


def validate_brand(val):
    """Validate other fields format."""
    if len(val) < 1:
        raise ValidationError(_("Brand should contain at least 1 character"))
    if len(val) > 1000:
        raise ValidationError(_("Brand cannot contain more than 1000 characters"))
    match = re.match(app.config['system_config']['regex'][app.config['system_config']['language_support']['default']]['brand'],val)
    if match is None:
        raise ValidationError(_("Brand is invalid. Does not match the selected language or invalid format."))


def validate_model_name(val):
    """Validate other fields format."""
    if len(val) < 1:
        raise ValidationError(_("Model name should contain at least 1 character"))
    if len(val) > 1000:
        raise ValidationError(_("Model name cannot contain more than 1000 characters"))
    match = re.match(app.config['system_config']['regex'][app.config['system_config']['language_support']['default']]['model_name'],val)
    if match is None:
        raise ValidationError(_("Model name is invalid. Does not match the selected language or invalid format."))


def block_duplicates(list):
    """Validate list to prevent duplicates insertion."""
    seen = set()
    for x in list:
        if x not in seen:
            seen.add(x)
        else:
            raise ValidationError(_("System cannot accept duplicate Values"))
