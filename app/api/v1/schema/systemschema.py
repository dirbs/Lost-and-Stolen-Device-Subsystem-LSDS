from marshmallow import Schema, fields


class IncidentNatureSchema(Schema):
    """Incident types response schema."""
    Id = fields.Str(attribute='id')
    Type = fields.Str(attribute='name')


class CaseStatusSchema(Schema):
    """Stolen types response schema."""
    Id = fields.Str(attribute='id')
    Type = fields.Str(attribute='description')


class ResponseSchema(Schema):
    """Response schema."""
    message = fields.Str()
