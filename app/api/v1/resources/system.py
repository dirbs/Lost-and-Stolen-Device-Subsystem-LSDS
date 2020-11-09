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

from app import app
from flask import Response
from flask_apispec import MethodResource, doc, marshal_with
from flask_babel import _

from ..models.natureofincident import NatureOfIncident
from ..models.status import Status
from ..assets.response import CODES, MIME_TYPES
from ..schema.systemschema import IncidentNatureSchema, ResponseSchema, CaseStatusSchema


class IncidentNature(MethodResource):
    """Flask resource to get incident types."""

    @doc(description='Get type of incidents', tags=['Incident Types'])
    @marshal_with(IncidentNatureSchema(many=True), code=200, description='On success show list of incident types')
    @marshal_with(ResponseSchema(), code=500, description='Internal server error')
    def get(self):
        """Return types of incidents."""
        try:
            incident_types = NatureOfIncident().query.all()
            response = Response(IncidentNatureSchema(many=True).dumps(incident_types), status=CODES.get('OK'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            return response
        except Exception as e:
            app.logger.critical("exception encountered during GET api/v1/incident_types, see blow logs")
            app.logger.exception(e)

            data = {
                "message": _("Database connectivity error. Please check connection parameters.")
            }

            response = Response(json.dumps(data), status=CODES.get("INTERNAL_SERVER_ERROR"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            return response


class CaseStatus(MethodResource):
    """Flask resource to get lost/stolen status types."""

    @doc(description='Get type of case statuses', tags=['Case Status'])
    @marshal_with(CaseStatusSchema(many=True), code=200, description='On success show list of case status')
    @marshal_with(ResponseSchema(), code=500, description='Internal server error')
    def get(self):
        """Return types of lost/stolen status."""
        try:
            case_statuses = Status().query.all()
            response = Response(CaseStatusSchema(many=True).dumps(case_statuses), status=CODES.get("OK"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            return response
        except Exception as e:
            app.logger.critical("exception encountered during GET api/v1/status_types, see below logs")
            app.logger.exception(e)

            data = {
                "message": _("Database connectivity error. Please check connection parameters.")
            }

            response = Response(json.dumps(data), status=CODES.get("INTERNAL_SERVER_ERROR"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            return response
