import re
from marshmallow import ValidationError
from app import app
from flask_babel import _


def validate_name(val):
    """Validate username format."""
    if len(val) < 1:
        raise ValidationError(_("name should contain more than one character"))
    if len(val) > 1000:
        raise ValidationError(_("name cannot contain more than 1000 characters"))


def validate_comment(val):
    """Validate comment format."""
    if len(val) < 1:
        raise ValidationError(_("Comment should contain more than one character"))
    if len(val) > 1000:
        raise ValidationError(_("Comment cannot contain more than 1000 characters"))


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


def validate_others(val, min_range, max_range, field):
    """Validate other fields format."""
    if len(val) < min_range:
        raise ValidationError(_("%(field)s should contain at least %(min)s character", field=field, min=min_range))
    if len(val) > max_range:
        raise ValidationError(_("%(field)s cannot contain more than %(max)s characters", field=field, max=max_range))


def block_duplicates(list):
    """Validate list to prevent duplicates insertion."""
    seen = set()
    for x in list:
        if x not in seen:
            seen.add(x)
        else:
            raise ValidationError(_("System cannot accept duplicate Values"))


def validate_lang_based_variables(args):
    keys_to_avoid = ['case_details', 'Accept-Language', 'incident_details']
    errors = {"messages": {}}
    for record_type in args:
        if record_type not in keys_to_avoid:
            for values in args[record_type]:
                if values in app.config['system_config']['regex'][args.get('Accept-Language', 'en')].keys():
                    match = re.match(app.config['system_config']['regex'][args.get('Accept-Language', 'en')][values], args[record_type][values])
                    if match is not None:
                        if record_type not in errors['messages']:
                            errors['messages'][record_type] = {}
                            errors['messages'][record_type][values] = [_('Value is invalid. Does not match the selected language or invalid format.')]
                        errors['messages'][record_type][values] = [_('Value is invalid. Does not match the selected language or invalid format.')]
    if len(errors['messages'])>0:
        raise ValidationError(errors)
