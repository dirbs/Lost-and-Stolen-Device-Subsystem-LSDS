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

case_api_url = 'api/v1/case'

data = {
    "case_details": {
            "get_blocked": True
        },
    "loggedin_user": {
        "user_id": "1215c23-3f64-4af5-8713-35782374713d",
        "username": "muazzama anwar"
    },
    "incident_details": {
        "incident_date": "2018-02-02",
        "incident_nature": 2
    },
    "personal_details": {
        "full_name": "test user",
        "gin": "44103-7789877-2",
        "address": "test address pakistan",
        "email": "test@email.com",
        "dob": "1991-02-02",
        "number": "03301111112"
    },
    "device_details": {
        "brand": "huawei",
        "model_name": "huawei mate 10",
        "description": "blue",
        "imeis": ["37006822000020", "37006822000201"],
        "msisdns": ["00923339171007", "00923449826511"]
    }
}


def test_insertion(flask_app):
    """Tests case insertion success"""
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['tracking_id'] is not None
    assert response['message'] is not None


def test_insertion_get_method(flask_app):
    """Test get request"""
    response = flask_app.get(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_insertion_put_method(flask_app):
    """Tests put request"""
    response = flask_app.put(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_insertion_patch_method(flask_app):
    """Tests patch request"""
    response = flask_app.patch(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_insertion_delete_method(flask_app):
    """Tests delete request"""
    response = flask_app.delete(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_duplicate_case(flask_app):
    """Tests duplicate case insertion"""
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 409
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['message'] is not None


def test_pd_input_criteria(flask_app):
    """Tests personal details input validation"""
    case_data = {
        "case_details": {
            "get_blocked": True
        },
        "loggedin_user": {
            "user_id": "1215c23-3f64-4af5-8713-35782374713d",
            "username": "muazzama anwar"
        },
        "incident_details": {
            "incident_date": "2018-02-02",
            "incident_nature": 2
        },
        "personal_details": {
            "full_name": "test user"
        },
        "device_details": {
            "brand": "huawei",
            "model_name": "huawei mate 10",
            "description": "blue",
            "imeis": [
                "37006822111120",
                "37006822111201"
            ],
            "msisdns": [
                "00923339171007",
                "00923449826511"
            ]
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(case_data), content_type='application/json')
    assert response.status_code == 400
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['message'] is not None


def test_name_format_case1(flask_app):
    """Tests name format validation with empty username"""
    user_data = {
        "loggedin_user": {
            "user_id": "1215c23-3f64-4af5-8713-35782374713d",
            "username": ""
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(user_data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['loggedin_user']['username'][0] is not None


def test_name_format_case2(flask_app):
    """Tests name format validation with username having more than 1000 characters"""
    user_data = {
        "loggedin_user": {
            "user_id": "1215c23-3f64-4af5-8713-35782374713d",
            "username": "aa"*1000
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(user_data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['loggedin_user']['username'][0] is not None


def test_name_format_case3(flask_app):
    """Tests name format validation with username having special invalid characters"""
    user_data = {
        "loggedin_user": {
            "user_id": "1215c23-3f64-4af5-8713-35782374713d",
            "username": "#$#$%%#$%#%"
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(user_data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['loggedin_user']['username'][0] is not None


def test_date_format(flask_app):
    """Tests date format validation"""
    incident_data = {
        "incident_details": {
            "incident_date": "20180202",
            "incident_nature": 2
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(incident_data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['incident_details']['incident_date'][0] is not None


def test_incident_type_format(flask_app):
    """Tests incident type format validation"""
    incident_data = {
        "incident_details": {
            "incident_date": "2018-02-02",
            "incident_nature": 0
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(incident_data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['incident_details']['incident_nature'][0] is not None


def test_gin_format(flask_app, mocked_config):
    """Tests government identification number format validation"""
    personal_details = {
        "personal_details": {
            "full_name": "test user",
            "gin": "44103-778987",
            "address": "test address pakistan",
            "email": "test@email.com",
            "dob": "1991-02-02",
            "number": "03301111112"
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(personal_details), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['personal_details']['gin'][0] is not None


def test_number_format(flask_app):
    """Tests alternate phone number format validation"""
    personal_details = {
        "personal_details": {
            "full_name": "test user",
            "gin": "44103-778987",
            "address": "test address pakistan",
            "email": "test@email.com",
            "dob": "1991-02-02",
            "number": "033012"
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(personal_details), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['personal_details']['number'][0] is not None


def test_other_parameters_format_case1(flask_app):
    """Tests other parameters format validation"""
    personal_details = {
        "personal_details": {
            "full_name": "test user",
            "gin": "44103-7789877-2",
            "address": "",
            "email": "test@email.com",
            "dob": "1991-02-02",
            "number": "033012432423"
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(personal_details), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['personal_details']['address'][0] is not None


def test_other_parameters_format_case2(flask_app):
    """Tests other parameters format validation having more than 1000 characters"""
    personal_details = {
        "personal_details": {
            "full_name": "test user",
            "gin": "44103-7789877-2",
            "address": "dsa"*1000,
            "email": "test@email.com",
            "dob": "1991-02-02",
            "number": "033012345678"
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(personal_details), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['personal_details']['address'][0] is not None


def test_email_format(flask_app):
    """Tests email format validation"""
    personal_details = {
        "personal_details": {
            "full_name": "test user",
            "gin": "44103-778987",
            "address": "dsajkdhajksd",
            "email": "testemail.com",
            "dob": "1991-02-02",
            "number": "0330123223424"
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(personal_details), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['personal_details']['email'][0] is not None


def test_msisdn_format(flask_app):
    """Tests MSISDN format validation"""
    device_details = {
        "device_details": {
            "brand": "huawei",
            "model_name": "huawei mate 10",
            "description": "blue",
            "imeis": ["37006822111120", "37006822111201"],
            "msisdns": ["009233", "00923449826511"]
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(device_details), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['device_details']['msisdns']['0'][0] is not None


def test_imei_format_case1(flask_app):
    """Tests IMEI format validation with IMEI having more than 16 characters"""
    device_details = {
        "device_details": {
            "brand": "huawei",
            "model_name": "huawei mate 10",
            "description": "blue",
            "imeis": ["3700682211112042342", "37006822111201"],
            "msisdns": ["0092333213122", "00923449826511"]
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(device_details), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['device_details']['imeis']['0'][0] is not None


def test_imei_format_case2(flask_app):
    """Tests IMEI format validation with IMEI having less than 14 characters"""
    device_details = {
        "device_details": {
            "brand": "huawei",
            "model_name": "huawei mate 10",
            "description": "blue",
            "imeis": ["37006822111120", "3700682"],
            "msisdns": ["009233332321", "00923449826511"]
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(device_details), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['device_details']['imeis']['1'][0] is not None


def test_imei_format_case3(flask_app):
    """Tests IMEI format validation with IMEI having invalid characters characters"""
    device_details = {
        "device_details": {
            "brand": "huawei",
            "model_name": "huawei mate 10",
            "description": "blue",
            "imeis": ["37006822111120", "32131dsada2331"],
            "msisdns": ["009233432422", "00923449826511"]
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(device_details), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['device_details']['imeis']['1'][0] is not None
