"""
 SPDX-License-Identifier: BSD-4-Clause-Clear

 Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided with the distribution.
 * All advertising materials mentioning features or use of this software, or any deployment of this software, or
   documentation accompanying any distribution of this software, must display the trademark/logo as per the details
   provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
   products derived from this software without specific prior written permission.

 SPDX-License-Identifier: ZLIB-ACKNOWLEDGEMENT

 Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

 This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable
 for any damages arising from the use of this software.

 Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter
 it and redistribute it freely, subject to the following restrictions:

 * The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If
   you use this software in a product, an acknowledgment is required by displaying the trademark/logo as per the details
   provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
 * Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
 * This notice may not be removed or altered from any source distribution.

 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
 THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.                                                               #
"""

from app import app
import requests


class CommonResources:
    """Common functionality used across the system."""

    @staticmethod
    def get_imei(imei):
        """Return IMEI response fetched from DIRBS core."""

        imei_url = requests.get(
            '{base}/{version}/imei/{imei}'.format(base=app.config['dev_config']['dirbs_core']['base_url'], version=app.config['dev_config']['dirbs_core']['version'], imei=imei))  # dirbs core imei api call
        try:
            if imei_url.status_code == 200:
                response = imei_url.json()
                return response
            else:
                return None
        except Exception as error:
            raise error

    @staticmethod
    def get_tac(tac):
        """Return TAC response fetched from DIRBS core."""

        try:
            tac_response = requests.get('{}/{}/tac/{}'.format(app.config['dev_config']['dirbs_core']['base_url'], app.config['dev_config']['dirbs_core']['version'], tac))  # dirbs core tac api call
            if tac_response.status_code == 200:
                resp = tac_response.json()
                return resp
            return {"gsma": None}
        except Exception as error:
            raise error

    @staticmethod
    def get_reg(imei):
        """Return registration information fetched from DIRBS core."""

        try:
            reg_response = requests.get(
                '{base}/{version}/imei/{imei}/info'.format(base=app.config['dev_config']['dirbs_core']['base_url'], version=app.config['dev_config']['dirbs_core']['version'], imei=imei))
            if reg_response.status_code == 200:
                resp = reg_response.json()
                return resp
            return {}
        except Exception as error:
            raise error

    @staticmethod
    def serialize_gsma_data(tac_resp, reg_resp):
        """Return serialized device details."""

        response = dict()
        if tac_resp['gsma'] and reg_resp:
            response = CommonResources.serialize(response, tac_resp['gsma'], reg_resp)
            return response
        elif reg_resp and not tac_resp['gsma']:
            response = CommonResources.serialize_reg(response, reg_resp)
            return response
        elif tac_resp['gsma'] and not reg_resp:
            response = CommonResources.serialize_gsma(response, tac_resp['gsma'])
            return response
        else:
            return {"gsma": None}

    @staticmethod
    def subscribers(imei):
        """Return subscriber's details fetched from DIRBS core."""
        try:
            seen_with_url = requests.get('{base}/{version}/imei/{imei}/subscribers?order=Descending'.format(base=app.config['dev_config']['dirbs_core']['base_url'], version=app.config['dev_config']['dirbs_core']['version'], imei=imei))  # dirbs core imei api call
            seen_with_resp = seen_with_url.json()
            result_size = seen_with_resp.get('_keys').get('result_size')
            seen_with_url = requests.get('{base}/{version}/imei/{imei}/subscribers?order=Descending&limit={result_size}'.format(base=app.config['dev_config']['dirbs_core']['base_url'], version=app.config['dev_config']['dirbs_core']['version'],imei=imei,result_size=result_size))  # dirbs core imei api call
            seen_with_resp = seen_with_url.json()
            data = seen_with_resp.get('subscribers')
            seen = set()
            result = [x for x in data if [(x['msisdn'], x['imsi']) not in seen, seen.add((x['msisdn'], x['imsi']))][0]]

            return {'subscribers': result}
        except Exception as error:
            raise error

    @staticmethod
    def serialize(response, gsma_resp, reg_resp):
        """Serialize device details from GSMA/registration data."""

        try:
            response['brand'] = reg_resp.get('brand_name') if reg_resp.get('brand_name') else gsma_resp.get('brand_name')
            response['model_name'] = reg_resp.get('model') if reg_resp.get('model') else gsma_resp.get('model_name')
            response['model_number'] = reg_resp.get('model_number') if reg_resp.get('model_number') else gsma_resp.get('marketing_name')
            response['device_type'] = reg_resp.get('device_type') if reg_resp.get('device_type') else gsma_resp.get('device_type')
            response['operating_system'] = reg_resp.get('operating_system') if reg_resp.get('operating_system') else gsma_resp.get('operating_system')
            response['radio_access_technology'] = reg_resp.get('radio_interface') if reg_resp.get('radio_interface') else gsma_resp.get('bands')
            return {'gsma': response}
        except Exception as error:
            raise error

    @staticmethod
    def serialize_reg(response, status_response):
        """Serialize device details from registration data."""

        try:
            response['brand'] = status_response.get('brand_name')
            response['model_name'] = status_response.get('model')
            response['model_number'] = status_response.get('model_number')
            response['device_type'] = status_response.get('device_type')
            response['operating_system'] = status_response.get('operating_system')
            response['radio_access_technology'] = status_response.get('radio_interface')
            return {'gsma': response}
        except Exception as error:
            raise error

    @staticmethod
    def serialize_gsma(response, status_response):
        """Serialize device details from GSMA data."""
        try:
            response['brand'] = status_response.get('brand_name')
            response['model_name'] = status_response.get('model_name')
            response['model_number'] = status_response.get('marketing_name')
            response['device_type'] = status_response.get('device_type')
            response['operating_system'] = status_response.get('operating_system')
            response['radio_access_technology'] = status_response.get('bands')
            return {'gsma': response}
        except Exception as error:
            raise error
