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
import requests

from flask import Response
from app import app
from ..models.status import Status
from flask_apispec import MethodResource, doc
from flask_babel import _


@app.route('/')
def index_route():
    """Flask base route"""
    data = {
        'message': _('Welcome to LSDS')
    }

    response = Response(json.dumps(data), status=200, mimetype='application/json')
    return response


class BaseRoutes(MethodResource):
    """Flask resource to check DIRBS core and database connection."""

    @doc(description='System version', tags=['Base'])
    def get(self):
        """Check system's connection with DIRBS core and database."""
        try:
            resp = requests.get('{base}/{version}/version'.format(base=app.config['system_config']['dirbs_core']['base_url'], version=app.config['system_config']['dirbs_core']['version']))  # dirbs core imei api call
            if resp.status_code == 200:
                data = {
                    "core_status": _("CORE connected successfully.")
                }
            else:
                data = {
                    "core_status": _("CORE connection failed.")
                }
        except requests.ConnectionError:
            data = {
                "core_status": _("CORE connection failed.")
            }
        try:
            Status().query.all()
            data['db_status'] = _("Database connected successfully")
        except:
            data['db_status'] = _("Database connection failed")

        return Response(json.dumps(data), status=200, mimetype='application/json')
