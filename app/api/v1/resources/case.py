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

import json

from app import db
from flask_babel import _
from ..assets.response import MIME_TYPES, CODES, MESSAGES
from ..models.case import Case
from ..models.summary import Summary
from ..assets.pagination import Pagination
from ..schema.case import CaseInsertSchema, CaseStatusUpdateSchema, CaseUpdateSchema, CasesSchema, CaseGetBlockedSchema
from ..schema.validations import *
from ..helpers.common_resources import CommonResources
from ..helpers.tasks import CeleryTasks
from ..helpers.decorators import restricted

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
    @use_kwargs(CaseUpdateSchema().fields_dict, location='json')
    @restricted
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
    @use_kwargs(CaseStatusUpdateSchema().fields_dict, location='json')
    @restricted
    def patch(self, tracking_id, **kwargs):
        """Update case status."""

        args = kwargs.get('status_args')
        try:
            case_id = Case.update_status(args, tracking_id)

            if case_id == 401:
                data = {
                    'message': _('Only admins can update case status.'),
                }
                response = Response(json.dumps(data), status=CODES.get("UNAUTHORIZED"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                return response

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

    @doc(description='Get list of cases', tags=['Cases'])
    @use_kwargs(CasesSchema().fields_dict, location='query')
    def get(self, **kwargs):
        """Return list of cases."""

        status = kwargs.get('status')
        try:
            if status:
                trigger = 'SET ROLE case_user; COMMIT;'
                db.session.execute(trigger)
                sql = "select c.*, cid.date_of_incident, cid.nature_of_incident, cpd.full_name, cpd.address, cpd.alternate_number, cpd.email, cpd.gin, cpd.father_name, cpd.mother_name, cpd.district, cpd.landline_number, dd.brand, dd.model_name, dd.physical_description, s.description as status, ni.name as incident_type, string_agg(distinct(di.imei::text), ', '::text) as imeis, string_agg(distinct(msisdn::text), ', '::text) as msisdns, string_agg(distinct(json_build_object('comment',cc.comments, 'comment_date',cc.comment_date, 'user_id',cc.user_id, 'username',cc.username, 'id',cc.id)::text), '| '::text) as comments from public.case as c left join case_comments as cc on cc.case_id=c.id, case_incident_details as cid, case_personal_details as cpd, device_details as dd, device_imei as di, device_msisdn as dm, public.status as s, public.nature_of_incident as ni where c.case_status="+str(status)+" and cid.case_id=c.id and cpd.case_id=c.id and dd.case_id=c.id and di.device_id=dd.id and dm.device_id=dd.id  and s.id=c.case_status and ni.id=cid.nature_of_incident group by c.id, cid.date_of_incident, cid.nature_of_incident, cpd.full_name, cpd.alternate_number, cpd.address, cpd.email, cpd.gin,cpd.father_name, cpd.mother_name, cpd.district, cpd.landline_number, dd.brand, dd.model_name, dd.physical_description, s.description, ni.name order by c.updated_at desc"
                cases = db.session.execute(sql)
                cases = CommonResources.serialize_cases(cases)
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
            data = {'message': _("Database connectivity error. Please check connection parameters.")}
            response = Response(json.dumps(data), status=CODES.get("INTERNAL_SERVER_ERROR"),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))

            return response
        finally:
            db.session.close()


class InsertCase(MethodResource):
    """Flak resource for case insertion."""

    @doc(description='Insert case', tags=['Case'])
    @use_kwargs(CaseInsertSchema().fields_dict, location='json')
    def post(self, **kwargs):
        """Insert case details."""
        try:
            tracking_id = Case.create(kwargs)
            if tracking_id.get('code') == 409:
                if tracking_id.get('reason') == "LSDS":
                    data = {
                        'message': _('IMEI: %(imei)s is a duplicate entry already reported at %(created_at)s with tracking id %(id)s.', imei=tracking_id.get('data')['imei'], created_at=tracking_id.get('data')['created_at'].strftime("%Y-%m-%d %H:%M:%S"), id=tracking_id.get('data')['tracking_id']),
                    }
                    response = Response(json.dumps(data), status=CODES.get("CONFLICT"),
                                        mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                    return response
                else:
                    data = {
                        'message': _('IMEI: %(imei)s is already reported and blocked through Bulk.', imei=tracking_id.get('data').get('imei')),
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
    @use_kwargs(CaseGetBlockedSchema().fields_dict, location='json')
    @restricted
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


class BlockAll(MethodResource):
    @doc(description='Block all pending cases', tags=['Cases'])
    @use_kwargs(CasesSchema().fields_dict, location='query')
    def get(self):
        response = (CeleryTasks.block_all.s() |
                    CeleryTasks.log_results.s(input=None)).apply_async()
        summary_data = {
            "tracking_id": response.parent.id,
            "status": response.state
        }
        Summary.create(summary_data)
        data = {
            "message": _("You can track your request using this id"),
            "task_id": response.parent.id,
            "state": response.state
        }
        return Response(json.dumps(data), status=CODES.get('OK'), mimetype=MIME_TYPES.get('APPLICATION_JSON'))


class CheckStatus(MethodResource):
    """Flask resource to check bulk processing status."""

    @doc(description="Check bulk request status", tags=['bulk'])
    def post(self, task_id):
        """Returns bulk processing status and summary if processing is completed."""
        try:
            result = Summary.find_by_trackingid(task_id)
            if result is None:
                response = {
                    "state": _("task not found.")
                }
            else:
                if result['status'] == 'PENDING':
                    # job is in progress yet
                    response = {
                        'state': _('PENDING')
                    }
                elif result['status'] == 'SUCCESS':
                    response = {
                        "state": _(result['status']),
                        "result": result['response']['response']
                    }
                else:
                    # something went wrong in the background job
                    response = {
                        'state': _('Processing Failed.')
                    }
            return Response(json.dumps(response), status=CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))
        except Exception as e:
            app.logger.info("Error occurred while retrieving status.")
            app.logger.exception(e)
            return Response(MESSAGES.get('INTERNAL_SERVER_ERROR'), CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('JSON'))