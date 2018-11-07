#######################################################################################################################
#                                                                                                                     #
# Copyright (c) 2018 Qualcomm Technologies, Inc.                                                                      #
#                                                                                                                     #
# All rights reserved.                                                                                                #
#                                                                                                                     #
# Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the      #
# limitations in the disclaimer below) provided that the following conditions are met:                                #
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following  #
#   disclaimer.                                                                                                       #
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the         #
#   following disclaimer in the documentation and/or other materials provided with the distribution.                  #
# * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or       #
#   promote products derived from this software without specific prior written permission.                            #
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED  #
# BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED #
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT      #
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR   #
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE,      #
# DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,      #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,   #
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                                  #
#                                                                                                                     #
#######################################################################################################################

import re

from app import GLOBAL_CONF
from webargs import fields, ValidationError


def validate_name(val):
    """Validate username format."""
    match = re.match(r'[a-zA-Z0-9\s][^\x01-\x1F]{0,1000}$', val)
    if len(val) < 1:
        raise ValidationError("name should contain more than one character")
    if len(val) > 1000:
        raise ValidationError("name cannot contain more than 1000 characters")
    if match is None:
        raise ValidationError("Name cannot contain invalid characters")


def validate_comment(val):
    """Validate comment format."""
    match = re.match(r'[a-zA-Z0-9\s][^\x01-\x1F]{0,1000}$', val)
    if len(val) < 1:
        raise ValidationError("Comment should contain more than one character")
    if len(val) > 1000:
        raise ValidationError("Comment cannot contain more than 1000 characters")
    if match is None:
        raise ValidationError("Comment cannot have invalid characters")


def validate_number(val):
    """Validate phone number format."""
    match = re.match('^\+?[0-9]{7,15}$', val)
    if match is None:
        raise ValidationError("Alternate phone number is invalid.")


def date_validation(val):
    """Validate date format."""
    match = re.match('^((19|20)\d{2})\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$', str(val))
    if match is None:
        raise ValidationError("Invalid date format")


def validate_imei(val):
    """Validate IMEI format."""
    match = re.match('^[a-fA-F0-9]{14,16}$', val)
    if len(val) < GLOBAL_CONF.get('min_imei_length'):
        raise ValidationError("IMEI too short, should contain at least {min} characters".format(min=GLOBAL_CONF.get('min_imei_length')))
    if len(val) > GLOBAL_CONF.get('max_imei_length'):
        raise ValidationError("IMEI too long, cannot contain more than {max} characters".format(max= GLOBAL_CONF.get('max_imei_length')))
    if match is None:
        raise ValidationError("IMEI is invalid.")


def validate_msisdn(val):
    """Validate MSISDN format."""
    match = re.match('^\+?[0-9]{7,15}$',val)
    if match is None:
        raise ValidationError("MSISDN is invalid.")


def validate_gin(val):
    """Validate Government identification number format."""
    match = re.match(GLOBAL_CONF.get('gin_regex'), val)
    if match is None:
        raise ValidationError("Government Identification Number must contain {range} digits".format(range=GLOBAL_CONF.get('gin_length')))


def validate_others(val, min_range, max_range, field):
    """Validate other fields format."""
    if len(val) < min_range:
        raise ValidationError("{field} should contain at least {min} character".format(field=field, min=min_range))
    if len(val) > max_range:
        raise ValidationError("{field} cannot contain more than {max} characters".format(field=field, max=max_range))


case_args = {
    'loggedin_user': fields.Nested({
    'user_id': fields.Str(required=True),
    'username': fields.Str(required=True, validate=validate_name)
    }),
    'incident_details': fields.Nested({
        'incident_date': fields.Str(required=True, validate=date_validation),
        'incident_nature': fields.Int(required=True, validate=lambda p: p == 1 or p == 2)
    }),
    'personal_details': fields.Nested({
        'full_name': fields.Str(required=True, validate=validate_name),
        'dob': fields.Str(validate=date_validation),
        'address': fields.Str(validate=lambda p: validate_others(p, 1, 1000, 'address')),
        'gin': fields.Str(validate=validate_gin),
        'number': fields.Str(validate=validate_number),
        'email': fields.Email()
    }),
    'device_details': fields.Nested({
        'brand': fields.Str(required=True, validate=lambda p: validate_others(p, 1, 1000, 'brand name')),
        'model_name': fields.Str(required=True, validate=lambda p: validate_others(p, 1, 1000, 'model name')),
        'description': fields.Str(required=True, validate=lambda p: validate_others(p, 1, 1000, 'description')),
        'imeis': fields.List(fields.Str(required=True, validate=validate_imei)),
        'msisdns': fields.List(fields.Str(required=True, validate=validate_msisdn))
    })
}

case_update_args = {
    'status_args': fields.Nested({
    'user_id': fields.Str(required=True),
    'username': fields.Str(required=True, validate=validate_name),
    'case_comment': fields.Str(required=True, validate=validate_comment)
    }),
    'personal_details': fields.Nested({
        'full_name': fields.Str(required=True, validate=validate_name),
        'dob': fields.Str(validate=date_validation),
        'address': fields.Str(validate=lambda p: validate_others(p, 1, 1000, 'address')),
        'gin': fields.Str(validate=validate_gin),
        'number': fields.Str(validate=validate_number),
        'email': fields.Email()
    })
}

case_status_args = {
    'status_args': fields.Nested({
    'user_id': fields.Str(required=True),
    'username': fields.Str(required=True, validate=validate_name),
    'case_status': fields.Int(required=True, validate=lambda p: p == 1 or p == 2 or p == 3),
    'case_comment': fields.Str(required=True, validate=validate_comment)
    })
}

get_cases = {
    'status': fields.Int(required=False, validate=lambda p: p == 1 or p == 2 or p == 3),
    'start': fields.Int(required=False),
    'limit': fields.Int(required=False)
}
