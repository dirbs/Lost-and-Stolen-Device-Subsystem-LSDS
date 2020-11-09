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

from marshmallow import fields, Schema, pre_dump
from .validations import *
from flask_babel import _

from datetime import datetime


class CaseDetailsSchema(Schema):
    """Case details"""
    get_blocked = fields.Boolean(required=True)


class UserSchema(Schema):
    """User schema."""
    user_id = fields.Str(required=True)
    username = fields.Str(required=True, validate=validate_username)
    role = fields.Str(required=True)
    case_comment = fields.Str(required=True, validate=validate_comment)
    case_status = fields.Int(required=True, validate=lambda p: p == 1 or p == 2 or p == 3)


class PersonalDetailsSchema(Schema):
    """Personal details schema."""
    full_name = fields.Str(required=True, validate=lambda p: validate_fullname(val=p, name="Fullname"))
    gin = fields.Str(required=True, validate=validate_gin)
    address = fields.Str(validate=validate_address)
    email = fields.Str(validate=validate_email)
    dob = fields.Str(validate=validate_date)
    number = fields.Str(required=True, validate=validate_number)


class IncidentDetailsSchema(Schema):
    """Incident details schema."""
    incident_date = fields.Str(required=True, validate=validate_date)
    incident_nature = fields.Int(required=True, validate=lambda p: p == 1 or p == 2)
    region = fields.Str(required=True)


class DeviceDetailsSchema(Schema):
    """Device details schema."""
    brand = fields.Str(required=True, validate=validate_brand)
    model_name = fields.Str(required=True, validate=validate_model_name)
    description = fields.Str(required=True, validate=validate_description)
    imeis = fields.List(fields.Str(required=True, validate=validate_imei), validate=block_duplicates, required=True)
    msisdns = fields.List(fields.Str(required=True, validate=validate_msisdn), validate=block_duplicates, required=True)


class CaseInsertSchema(Schema):
    """Case Insertion schema."""
    case_details = fields.Nested(CaseDetailsSchema)
    loggedin_user = fields.Nested(UserSchema, only=['username', 'user_id', 'role'])
    incident_details = fields.Nested(IncidentDetailsSchema)
    personal_details = fields.Nested(PersonalDetailsSchema)
    device_details = fields.Nested(DeviceDetailsSchema)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class CaseUpdateSchema(Schema):
    """Update case schema."""
    status_args = fields.Nested(UserSchema, only=['username', 'user_id', 'case_comment', 'role'], required=True)
    personal_details = fields.Nested(PersonalDetailsSchema)
    case_details = fields.Nested(CaseDetailsSchema)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class CaseGetBlockedSchema(Schema):
    """Update case schema."""
    status_args = fields.Nested(UserSchema, only=['username', 'user_id', 'case_comment', 'role'], required=True)
    case_details = fields.Nested(CaseDetailsSchema)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class CaseStatusUpdateSchema(Schema):
    """Update case status schema."""
    status_args = fields.Nested(UserSchema, required=True)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class CasesSchema(Schema):
    """request schema to get case list"""
    status = fields.Int(validate=lambda p: p == 1 or p == 2 or p == 3)
    start = fields.Int(validate=lambda p: p >= 1)
    limit = fields.Int(validate=lambda p: p >= 1)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class SearchArgsSchema(Schema):
    """Search arguments schema."""
    tracking_id = fields.Str()
    status = fields.Str()
    source = fields.Str()
    updated_at = fields.Str()
    imeis = fields.List(fields.Str())
    msisdns = fields.List(fields.Str())
    email = fields.Str()
    alternate_number = fields.Str()
    full_name = fields.Str()
    gin = fields.Str()
    address = fields.Str()
    incident = fields.Str()
    date_of_incident = fields.Str()
    brand = fields.Str()
    model = fields.Str()
    description = fields.Str()


class SearchSchema(Schema):
    """Search schema."""
    limit = fields.Int(validate=lambda p: p >= 1)
    start = fields.Int(validate=lambda p: p >= 1)
    search_args = fields.Nested(SearchArgsSchema, required=True)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class SearchResponseSchemaES(Schema):
    """Search response schema."""
    tracking_id = fields.Str(attribute='tracking_id')
    status = fields.Str(attribute='status')
    updated_at = fields.Str(attribute='updated_at')
    get_blocked = fields.Boolean(attribute='get_blocked')
    incident_details = fields.Dict(attribute='incident_details')
    personal_details = fields.Dict(attribute='personal_details')
    creator = fields.Dict(attribute='creator')
    device_details = fields.Dict(attribute='device_details')
    comments = fields.List(fields.Dict(), attribute='comments')
    source = fields.Str(attribute='source')

    @pre_dump
    def serialize_data(self, data):
        data = data['_source']
        data['status'] = _(data.get('status'))
        return data


class SearchResponseSchema(Schema):
    """Search response schema."""
    tracking_id = fields.Str(attribute='tracking_id')
    status = fields.Str(attribute='status')
    updated_at = fields.Str(attribute='updated_at')
    get_blocked = fields.Boolean(attribute='get_blocked')
    incident_details = fields.Dict(attribute='incident_details')
    personal_details = fields.Dict(attribute='personal_details')
    creator = fields.Dict(attribute='creator')
    device_details = fields.Dict(attribute='device_details')
    comments = fields.List(fields.Dict(), attribute='comments')

    @pre_dump
    def serialize_data(self, data):
        data['incident_details'] = {
            "incident_date": data.get('date_of_incident'),
            "incident_nature": _(data.get('incident'))
        }
        data['personal_details'] = {
            "full_name": data.get('full_name'),
            "dob": data.get('dob'),
            "address": data.get('address'),
            "gin": data.get('gin'),
            "number": data.get('alternate_number'),
            "email": data.get('email')
        }
        data['device_details'] = {
            "brand": data.get('brand'),
            "model_name": data.get('model'),
            "description": data.get('description'),
            "imeis": data.get('imeis').split(','),
            "msisdns": data.get('msisdns').split(',')
        }
        data['creator'] = {
            "user_id": data.get('user_id'),
            "username": data.get('username')
        }
        return data


class BulkInsertSchema(Schema):
    """Case Insertion schema."""
    action = fields.Str(required=True, validate=lambda p: p == "block" or p == "unblock")
    file = fields.Str(description="Submit tsv/txt file path containing bulk IMEIs")

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields
