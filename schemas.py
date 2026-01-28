from marshmallow import Schema, fields


class DailyTrackingSchema(Schema):
    id = fields.Int()
    organization_name = fields.Str()
    service_requested = fields.Str()
    remarks = fields.Str()


class FileTrackingSchema(Schema):
    id = fields.Int()
    organization_name = fields.Str()
    service_requested = fields.Str()
    status = fields.Str()
    date_received = fields.Date()
    date_correction_required = fields.Date()
