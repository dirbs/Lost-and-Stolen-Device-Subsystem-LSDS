from marshmallow import fields, Schema, pre_dump
from .validations import *


class UserSchema(Schema):
    """User schema."""
    user_id = fields.Str(required=True)
    username = fields.Str(required=True, validate=validate_name)
    case_comment = fields.Str(required=True, validate=validate_comment)
    case_status = fields.Int(required=True, validate=lambda p: p == 1 or p == 2 or p == 3)


class PersonalDetailsSchema(Schema):
    """Personal details schema."""
    full_name = fields.Str(required=True, validate=validate_name)
    gin = fields.Str(validate=validate_gin)
    address = fields.Str(validate=lambda p: validate_others(p, 1, 1000, 'address'))
    email = fields.Email()
    dob = fields.Str(validate=validate_date)
    number = fields.Str(validate=validate_number)


class IncidentDetailsSchema(Schema):
    """Incident details schema."""
    incident_date = fields.Str(required=True, validate=validate_date)
    incident_nature = fields.Int(required=True, validate=lambda p: p == 1 or p == 2)


class DeviceDetailsSchema(Schema):
    """Device details schema."""
    brand = fields.Str(required=True, validate=lambda p: validate_others(p, 1, 1000, 'brand name'))
    model_name = fields.Str(required=True, validate=lambda p: validate_others(p, 1, 1000, 'model name'))
    description = fields.Str(required=True, validate=lambda p: validate_others(p, 1, 1000, 'description'))
    imeis = fields.List(fields.Str(required=True, validate=validate_imei))
    msisdns = fields.List(fields.Str(required=True, validate=validate_msisdn))


class CaseInsertSchema(Schema):
    """Case Insertion schema."""
    loggedin_user = fields.Nested(UserSchema, only=['username', 'user_id'])
    incident_details = fields.Nested(IncidentDetailsSchema)
    personal_details = fields.Nested(PersonalDetailsSchema)
    device_details = fields.Nested(DeviceDetailsSchema)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class CaseUpdateSchema(Schema):
    """Update case schema."""
    status_args = fields.Nested(UserSchema, only=['username', 'user_id', 'case_comment'], required=True)
    personal_details = fields.Nested(PersonalDetailsSchema, required=True)

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
    start = fields.Int()
    limit = fields.Int()

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class SearchArgsSchema(Schema):
    """Search arguments schema."""
    tracking_id = fields.Str()
    status = fields.Str()
    updated_at = fields.Str()
    imeis = fields.List(fields.Str())
    msisdns = fields.List(fields.Str())
    dob = fields.Str()
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


class SearchResponseSchema(Schema):
    """Search response schema."""
    tracking_id = fields.Str(attribute='tracking_id')
    status = fields.Str(attribute='status')
    updated_at = fields.Str(attribute='updated_at')
    incident_details = fields.Dict(attribute='incident_details')
    personal_details = fields.Dict(attribute='personal_details')
    creator = fields.Dict(attribute='creator')
    device_details = fields.Dict(attribute='device_details')

    @pre_dump
    def serialize_data(self, data):
        data['updated_at'] = data['updated_at'].strftime("%Y-%m-%data %H:%M:%S")
        data['incident_details'] = {
            "incident_date": data.get('date_of_incident'),
            "incident_nature": data.get('incident')
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
