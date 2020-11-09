from flask import abort
from functools import wraps
from ..models.case import Case


def restricted(f):
    @wraps(f)
    def user_level(self, tracking_id, **kwargs):
        case = Case.get_case(tracking_id)
        if case and case['creator']['user_id'] != kwargs.get('status_args').get('user_id') and kwargs.get('status_args').get('role') == "staff":
            abort(401, description="Unauthorized Access")
        return f(self, tracking_id=tracking_id, **kwargs)

    return user_level
