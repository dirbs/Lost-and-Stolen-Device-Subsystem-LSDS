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

imei_api_url = '/api/v1/imei'


def test_imei_gsma_reg(dirbs_core_mock, flask_app):
    """Test IMEI with GSMA and registration data"""
    response = flask_app.get(imei_api_url+'/12345678901234', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    resp = json.loads(response.get_data(as_text=True))
    assert resp.get('gsma') is not None
    assert resp['gsma']['radio_access_technology'] == "radio_interface"
    assert resp['gsma']['model_number'] == "modelnumber"
    assert resp['gsma']['operating_system'] is None
    assert resp['gsma']['device_type'] == "devicetype"
    assert resp['gsma']['brand'] == "brandsname"
    assert resp['gsma']['model_name'] == "model"


def test_imei_gsma(dirbs_core_mock, flask_app):
    """Test IMEI with GSMA data"""
    response = flask_app.get(imei_api_url+'/12345678904321', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    resp = json.loads(response.get_data(as_text=True))
    assert resp.get('gsma') is not None
    assert resp['gsma']['radio_access_technology'] == "sample-bands-data"
    assert resp['gsma']['model_number'] == "sample-marketing-name"
    assert resp['gsma']['operating_system'] is None
    assert resp['gsma']['device_type'] == "sample-device-type"
    assert resp['gsma']['brand'] == "sample-brand-name"
    assert resp['gsma']['model_name'] == "sample-model-name"


def test_imei_reg(dirbs_core_mock, flask_app):
    """Test IMEI with registration data"""
    response = flask_app.get(imei_api_url+'/87654321904321', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    resp = json.loads(response.get_data(as_text=True))
    assert resp['gsma']['radio_access_technology'] == "radio_interface"
    assert resp['gsma']['model_number'] == "modelnumber"
    assert resp['gsma']['operating_system'] is None
    assert resp['gsma']['device_type'] == "devicetype"
    assert resp['gsma']['brand'] == "brandsname"
    assert resp['gsma']['model_name'] == "model"


def test_imei(dirbs_core_mock, flask_app):
    """Test IMEI with no GSMA and registration data"""
    response = flask_app.get(imei_api_url+'/87654321901234', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    resp = json.loads(response.get_data(as_text=True))
    assert resp.get('gsma') is None


def test_gsma_failure(dirbs_core_mock, flask_app):
    """Test IMEI in case of GSMA and registration call failure"""
    response = flask_app.get(imei_api_url+'/89764532901234', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    resp = json.loads(response.get_data(as_text=True))
    assert resp.get('gsma') is None


def test_imei_request_method(flask_app):
    """Tests IMEI allowed request methods"""
    response = flask_app.post(imei_api_url+'/12345678901234', content_type='application/json')
    assert response.status_code == 405
    response = flask_app.put(imei_api_url+'/12345678901234', content_type='application/json')
    assert response.status_code == 405
    response = flask_app.patch(imei_api_url+'/12345678901234', content_type='application/json')
    assert response.status_code == 405
    response = flask_app.delete(imei_api_url+'/12345678901234', content_type='application/json')
    assert response.status_code == 405


def test_imei_input_format(flask_app):
    """Test IMEI input format validation"""

    # IMEI having more than 16 characters
    response = flask_app.get(imei_api_url+'/12344329x00060000', content_type='application/json')
    assert response.status_code == 400
    assert json.loads(response.get_data(as_text=True))["message"] is not None

    # IMEI having invalid characters
    response = flask_app.get(imei_api_url+'/1234567890123s3', content_type='application/json')
    assert response.status_code == 400
    assert json.loads(response.get_data(as_text=True))['message'] is not None

    # IMEI having less than 14 characters
    response = flask_app.get(imei_api_url+'/12344329000', content_type='application/json')
    assert response.status_code == 400
    assert json.loads(response.get_data(as_text=True))["message"] is not None


def test_imei_failure_resp(dirbs_core_mock, flask_app):
    """Tests IMEI in case if imei call failure"""
    response = flask_app.get(imei_api_url+'/12345678909999', content_type='application/json')
    assert response.status_code == 503


def test_imei_response(dirbs_core_mock, flask_app):
    """Test IMEI JSON response."""
    response = flask_app.get(imei_api_url+'/12345678901111?seen_with=1', content_type='application/json')
    response = json.loads(response.get_data(as_text=True))
    assert response.get('registration_status') is not None
    assert response.get('stolen_status') is not None
    assert response.get('gsma') is not None
    assert response.get('gsma') == {'model_name': 'model', 'model_number': 'modelnumber', 'operating_system': None,
                                    'device_type': 'devicetype', 'brand': 'brandsname',
                                    'radio_access_technology': 'radio_interface'}
    assert response.get('subscribers') is not None
    assert response.get('classification_state') is not None


def test_imei_seenwith_response(dirbs_core_mock, flask_app):
    """Test IMEI having subscribers data"""
    response = flask_app.get(imei_api_url+'/12345678901111', content_type='application/json')
    response = json.loads(response.get_data(as_text=True))
    assert response.get('subscribers') is None
