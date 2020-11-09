"""
Copyright (c) 2018-2019 Qualcomm Technologies, Inc.
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
    The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
    Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
    This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                               #
"""

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


def validate_fullname(val, name):
    """Validate username format."""
    if len(val) < 1:
        raise ValidationError(_(name + " should contain more than one character"))
    if len(val) > 1000:
        raise ValidationError(_(name + " cannot contain more than 1000 characters"))
    match = re.match(app.config['system_config']['regex'][app.config['system_config']['language_support']['default']]['full_name'],val)
    if match is None:
        raise ValidationError(_(name + " is invalid. Does not match the selected language or invalid format."))


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


def validate_email(val):
    """Validate phone number format."""
    match = re.match(app.config['system_config']['validation'].get('email'), val)
    if match is None:
        raise ValidationError(_("Email is invalid."))


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
        raise ValidationError(_("IMEI too short, should contain at least %(min)d characters", min=min_imei_length))
    if len(val) > max_imei_length:
        raise ValidationError(_("IMEI too long, cannot contain more than %(max)d characters", max=max_imei_length))
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
