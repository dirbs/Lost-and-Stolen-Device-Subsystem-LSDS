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

from app import app
from flask import Response, request
from flask_apispec import MethodResource, doc
from flask_babel import _

from ..assets.response import MIME_TYPES, CODES
from ..requests.args_validation import validate_imei, validate_msisdn
from app.api.v1.helpers.common_resources import CommonResources


class FetchImei(MethodResource):
    """Flask resource to fetch IMEI data."""

    @doc(description="Fetch IMEI's relevant details", tags=['IMEI'])
    def get(self, imei):
        """Return IMEI relevant information."""
        try:
            validate_imei(imei)

            seen_with = request.args.get('seen_with')

            imei_data = CommonResources.get_imei(imei)
            if imei_data:
                gsma_data = CommonResources.get_tac(imei[:8])  # get gsma data from tac
                registration = CommonResources.get_reg(imei)
                gsma = CommonResources.serialize_gsma_data(tac_resp=gsma_data, reg_resp=registration)
                response = dict(imei_data, **gsma)

                if seen_with:
                    if seen_with == '1':
                        seen_with_data = CommonResources.subscribers(imei)
                        response = dict(response, **seen_with_data)

                        response = Response(json.dumps(response), status=200, mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                        return response

                response = Response(json.dumps(response), status=200, mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                return response
            else:
                data = {
                    "message": _("Failed to retrieve IMEI response from core system.")
                }
                return Response(json.dumps(data), status=CODES.get("SERVICE_UNAVAILABLE"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except ValueError as error:
            data = {
                "message": str(error)
            }

            response = Response(json.dumps(data), status=CODES.get("BAD_REQUEST"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            return response
        except Exception as e:
            app.logger.critical("exception encountered during GET api/v1/imei, see logs below")
            data = {
                    "message": _("Error generating IMEI response. Check dirbs core url.")
                }

            response = Response(json.dumps(data), status=CODES.get("SERVICE_UNAVAILABLE"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            return response


class FetchMsisdn(MethodResource):
    """Flask resource to fetch MSISDN data."""

    @doc(description="Fetch MSISDN's relevant details", tags=['MSISDN'])
    def get(self, msisdn):
        """Fetch MSISDN relevant information"""
        try:
            validate_msisdn(msisdn)

            url = '{base_url}/{version}/msisdn/{msisdn}'.format(
                base_url=app.config['system_config']['dirbs_core']['base_url'],
                version=app.config['system_config']['dirbs_core']['version'],
                msisdn=msisdn
            )

            res = requests.get(url)
            data = res.json()

            if data['results']:
                seen = set()
                data['results'] = [x for x in data['results'] if [(x['imei_norm'], x['imsi']) not in seen, seen.add((x['imei_norm'], x['imsi']))][0]]

                tac_list = list(set([imei['imei_norm'][:8] for imei in data['results']]))

                batch_req = {
                    "tacs": tac_list
                }
                headers = {'content-type': 'application/json', 'charset': 'utf-8'}
                tac_response = requests.post('{base_url}/{version}/tac'.format(base_url=app.config['system_config']['dirbs_core']['base_url'], version=app.config['system_config']['dirbs_core']['version']), data=json.dumps(batch_req), headers=headers)  # dirbs core batch tac api call

                tac_response = tac_response.json()

                for tac in tac_response['results']:
                    for records in data['results']:
                        if tac['tac'] == records['imei_norm'][:8]:
                            registration = CommonResources.get_reg(records['imei_norm'])
                            gsma = CommonResources.serialize_gsma_data(tac_resp=tac, reg_resp=registration)
                            del records['registration']
                            records['gsma'] = gsma['gsma']

            data['results'] = [x for x in sorted(data['results'], key=lambda x: x['last_seen'], reverse=True)]
            response = Response(json.dumps(data), status=200, mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            return response
        except ValueError as error:
            data = {
                    "message": _(str(error))
                }
            response = Response(json.dumps(data), status=CODES.get("BAD_REQUEST"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            return response
        except Exception:
            data = {
                    "message": _("Error generating MSISDN response. Check dirbs core url.")
                }
            response = Response(json.dumps(data), status=CODES.get("SERVICE_UNAVAILABLE"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            return response

