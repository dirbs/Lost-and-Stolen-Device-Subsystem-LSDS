"""
 Copyright (c) 2018 Qualcomm Technologies, Inc.

 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
   following disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or
   promote products derived from this software without specific prior written permission.
 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED
 BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
 SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE,
 DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import json

from app import app, db
from flask_babel import _
from ..assets.response import MIME_TYPES, CODES, MESSAGES
from ..models.case import Case
from ..assets.pagination import Pagination
from ..schema.case import CaseInsertSchema, CaseStatusUpdateSchema, CaseUpdateSchema, CasesSchema, CaseGetBlockedSchema

from flask import Response
from sqlalchemy import desc
from flask_apispec import use_kwargs, MethodResource, doc


class CaseRoutes(MethodResource):
    """Flask resources for case."""

    @doc(description='Get case details', tags=['Case'])
    def get(self, tracking_id):
        """Return case details by tracking id"""

        try:
            if tracking_id:
                case_details = Case.get_case(tracking_id)
                if case_details:
                    response = Response(json.dumps(case_details), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                    return response
                else:
                    data = {

                            "tracking_id": tracking_id,
                            "message": _("Case not found")

                            }

                    response = Response(json.dumps(data), status=CODES.get("NOT_FOUND"),
                                        mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                    return response
            else:

                data = {
                    "message": _(MESSAGES.get("UNDEFINED_TRACKING_ID"))
                }

                response = Response(json.dumps(data), status=CODES.get("BAD_REQUEST"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response
        except Exception as e:
            app.logger.exception(e)

            data = {
                "message": _("Error retrieving case results. Please check tracking id or database connection.")
            }

            response = Response(json.dumps(data), status=CODES.get("INTERNAL_SERVER_ERROR"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            return response

    @doc(description='Update case details', tags=['Case'])
    @use_kwargs(CaseUpdateSchema().fields_dict, locations=['json'])
    def put(self, tracking_id, **kwargs):
        """Update case personal details."""
        try:
            case_id = Case.update_blocked_info(kwargs, tracking_id)
            case_id = Case.update(kwargs, tracking_id)

            if case_id == 406:
                data = {
                    'message': _('Case updation not allowed in this status'),
                }
                response = Response(json.dumps(data), status=CODES.get("NOT_ACCEPTABLE"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response

            if case_id == 400:
                data = {

                    "tracking_id": tracking_id,
                    "message": _("Enter at least one optional field with full name in personal details.")

                }

                response = Response(json.dumps(data), status=CODES.get("BAD_REQUEST"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response

            if case_id:
                data = {
                    'message': _('Case updated successfully'),
                    'tracking_id': tracking_id
                }

                response = Response(json.dumps(data), status=CODES.get("OK"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response
            else:
                data = {

                    "tracking_id": tracking_id,
                    "message": _("Case not found")

                }

                response = Response(json.dumps(data), status=CODES.get("NOT_FOUND"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response

        except Exception as e:
            app.logger.exception(e)
            data = {'message': _('Case update failed!')}
            response = Response(json.dumps(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            return response

    @doc(description='Update case status', tags=['Case'])
    @use_kwargs(CaseStatusUpdateSchema().fields_dict, locations=['json'])
    def patch(self, tracking_id, **kwargs):
        """Update case status."""

        args = kwargs.get('status_args')
        try:
            case_id = Case.update_status(args, tracking_id)

            if case_id == 406:
                data = {
                        'message': _('Unable to update case status. Either Blocking is disabled or case has already been recovered.'),
                    }
                response = Response(json.dumps(data), status=CODES.get("NOT_ACCEPTABLE"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response

            if case_id == 409:
                data = {
                    'message': _('Case already has the same status.'),
                }
                response = Response(json.dumps(data), status=CODES.get("CONFLICT"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response

            if case_id:
                data = {'message': _('Case status updated'), 'tracking_id': tracking_id}
                response = Response(json.dumps(data), status=CODES.get("OK"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response
            else:
                data = {

                    "tracking_id": tracking_id,
                    "message": _("Case not found")

                }

                response = Response(json.dumps(data), status=CODES.get("NOT_FOUND"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response

        except Exception as e:
            app.logger.exception(e)
            data = {'message': _('Case status update failed!')}
            response = Response(json.dumps(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            return response


class CaseList(MethodResource):
    """Flask resource to get list of cases."""

    @staticmethod
    def serialize(cases):
        """Serialize response."""
        case_list = []
        for row in cases:
            case_list.append(dict((col, val) for col, val in row.items()))
        cases = []
        for case in case_list:
            comment_list = []
            for comment in case.get('comments').split('|'):
                comment = json.loads(comment)
                if comment.get('id'):
                    comment_list.append({
                        'comment': comment.get('comment'),
                        'user_id': comment.get('user_id'),
                        'username': comment.get('username'),
                        'comment_date': comment.get('comment_date').split(' ', 1)[0]
                    })
            case_detail = {
                    "get_blocked": case.get('get_blocked'),
                    "creator": {
                        "user_id": case.get('user_id'),
                        "username": case.get('username')
                    },
                    "personal_details": {
                        "address": case.get('address'),
                        "dob": case.get('dob'),
                        "gin": case.get('gin'),
                        "email": case.get('email'),
                        "number": case.get('alternate_number'),
                        "full_name": case.get('full_name')
                    },
                    "tracking_id": case.get('tracking_id'),
                    "comments": comment_list,
                    "incident_details": {
                        "incident_date": case.get('date_of_incident'),
                        "incident_nature": case.get('incident_type')
                    },
                    "created_at": case.get('created_at').strftime("%Y-%m-%d %H:%M:%S"),
                    "device_details": {
                        "description": case.get('physical_description'),
                        "model_name": case.get('model_name'),
                        "imeis": case.get('imeis').split(','),
                        "msisdns": case.get('msisdns').split(','),
                        "brand": case.get('brand')
                    },
                    "status": case.get('status'),
                    "updated_at": case.get('updated_at').strftime("%Y-%m-%d %H:%M:%S")
                }

            cases.append(case_detail)
        return cases

    @doc(description='Get list of cases', tags=['Cases'])
    @use_kwargs(CasesSchema().fields_dict, locations=['query'])
    def get(self, **kwargs):
        """Return list of cases."""

        status = kwargs.get('status')
        try:
            if status:
                sql = "select c.*, cid.date_of_incident, cid.nature_of_incident, cpd.full_name, cpd.address, cpd.alternate_number, cpd.dob, cpd.email, cpd.gin, dd.brand, dd.model_name, dd.physical_description, s.description as status, ni.name as incident_type, string_agg(distinct(di.imei::text), ', '::text) as imeis, string_agg(distinct(msisdn::text), ', '::text) as msisdns, string_agg(distinct(json_build_object('comment',cc.comments, 'comment_date',cc.comment_date, 'user_id',cc.user_id, 'username',cc.username, 'id',cc.id)::text), '| '::text) as comments from public.case as c left join case_comments as cc on cc.case_id=c.id, case_incident_details as cid, case_personal_details as cpd, device_details as dd, device_imei as di, device_msisdn as dm, public.status as s, public.nature_of_incident as ni where c.case_status="+str(status)+" and cid.case_id=c.id and cpd.case_id=c.id and dd.case_id=c.id and di.device_id=dd.id and dm.device_id=dd.id  and s.id=c.case_status and ni.id=cid.nature_of_incident group by c.id, cid.date_of_incident, cid.nature_of_incident, cpd.full_name, cpd.dob, cpd.alternate_number, cpd.address, cpd.email, cpd.gin, dd.brand, dd.model_name, dd.physical_description, s.description, ni.name order by c.updated_at desc"
                cases = db.engine.execute(sql)
                cases = CaseList.serialize(cases)
                if cases:
                    data = Pagination.get_paginated_list(cases, '/cases', start=kwargs.get('start', 1),
                                                         limit=kwargs.get('limit', 3))
                    response = Response(json.dumps(data), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                    return response
                else:
                    data = {
                        "start": kwargs.get('start', 1),
                        "previous": "",
                        "next": "",
                        "cases": cases,
                        "count": 0,
                        "limit": kwargs.get('limit', 2)
                    }
                    response = Response(json.dumps(data, default=str), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                    return response

            cases = [case.serialize for case in Case.query.order_by(desc(Case.updated_at)).all()]
            if cases:
                data = Pagination.get_paginated_list(cases, '/cases', start=kwargs.get('start', 1),
                                                     limit=kwargs.get('limit', 3))
                response = Response(json.dumps(data), status=CODES.get("OK"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                # return data
                return response
            else:
                data = {
                    "start": kwargs.get('start', 1),
                    "previous": "",
                    "next": "",
                    "cases": cases,
                    "count": 0,
                    "limit": kwargs.get('limit', 2)
                }
                response = Response(json.dumps(data, default=str), status=CODES.get("OK"),
                                    mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                return response
        except Exception as e:
            app.logger.exception(e)
            data = {'message': "Database connectivity error. Please check connection parameters."}
            response = Response(json.dumps(data), status=CODES.get("INTERNAL_SERVER_ERROR"),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))

            return response
        finally:
            db.session.close()


class InsertCase(MethodResource):
    """Flak resource for case insertion."""

    @doc(description='Insert case', tags=['Case'])
    @use_kwargs(CaseInsertSchema().fields_dict, locations=['json'])
    def post(self, **kwargs):
        """Insert case details."""
        try:
            tracking_id = Case.create(kwargs)

            if tracking_id.get('code') == 409:
                data = {
                    'message': 'IMEI: ' + tracking_id.get('data') + ' is a duplicate entry.',
                }
                response = Response(json.dumps(data), status=CODES.get("CONFLICT"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response

            if tracking_id.get('code') == 400:
                data = {
                    "message": _("Enter at least one optional field with full name in personal details.")
                }

                response = Response(json.dumps(data), status=CODES.get("BAD_REQUEST"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response

            if tracking_id.get('code') == 200:
                data = {
                    'message': _('case successfully added'),
                    'tracking_id': tracking_id.get('data')
                }

                response = Response(json.dumps(data), status=CODES.get("OK"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response
            else:
                data = {
                    'message': _('case addition failed'),
                }

                response = Response(json.dumps(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                                    mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                return response
        except Exception as e:
            db.session.rollback()
            app.logger.exception(e)

            data = {
                'message': _('case addition failed')
            }

            response = Response(json.dumps(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            return response


class UpdateCase(MethodResource):
    @doc(description='Update case information', tags=['Case'])
    @use_kwargs(CaseGetBlockedSchema().fields_dict, locations=['json'])
    def patch(self, tracking_id, **args):
        """Update case get blocked information."""

        try:
            case_id = Case.update_blocked_info(args, tracking_id)

            if case_id == 406:
                data = {
                    'message': _('Case updation not allowed in this status'),
                }
                response = Response(json.dumps(data), status=CODES.get("NOT_ACCEPTABLE"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response

            if case_id:
                data = {'message': _('Case status updated'), 'tracking_id': tracking_id}
                response = Response(json.dumps(data), status=CODES.get("OK"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response
            else:
                data = {

                    "tracking_id": tracking_id,
                    "message": _("Case not found")

                }

                response = Response(json.dumps(data), status=CODES.get("NOT_FOUND"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response

        except Exception as e:
            app.logger.exception(e)
            data = {'message': _('Update of case information failed!')}
            response = Response(json.dumps(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            return response
