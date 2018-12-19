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

case_api_url = 'api/v1/case'

data = {
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
    "imeis": [
      "37006822000020",
      "37006822000201"
    ],
    "msisdns": [
      "00923339171007",
      "00923449826511"
    ]
  }
}


def test_insertion(flask_app):
    """Tests case insertion success"""
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['tracking_id'] is not None
    assert response['message'] == "case successfully added"


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
    assert response['message'] == "IMEI: 37006822000020 is a duplicate entry."


def test_pd_input_criteria(flask_app):
    """Tests personal details input validation"""
    data = {
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
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['message'] == "Enter at least one optional field with full name in personal details."


def test_name_format_case1(flask_app):
    """Tests name format validation with empty username"""
    data = {
        "loggedin_user": {
            "user_id": "1215c23-3f64-4af5-8713-35782374713d",
            "username": ""
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['loggedin_user']['username'][0] == 'name should contain more than one character'


def test_name_format_case2(flask_app):
    """Tests name format validation with username having more than 1000 characters"""
    data = {
        "loggedin_user": {
            "user_id": "1215c23-3f64-4af5-8713-35782374713d",
            "username": "aa"*1000
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['loggedin_user']['username'][0] == 'name cannot contain more than 1000 characters'


def test_name_format_case3(flask_app):
    """Tests name format validation with username having special invalid characters"""
    data = {
        "loggedin_user": {
            "user_id": "1215c23-3f64-4af5-8713-35782374713d",
            "username": "#$#$%%#$%#%"
        }
    }
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['loggedin_user']['username'][0] == 'Name cannot contain invalid characters'


def test_date_format(flask_app):
    """Tests date format validation"""
    data = {"incident_details": {"incident_date": "20180202", "incident_nature": 2}}
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['incident_details']['incident_date'][0] == 'Invalid date format'


def test_incident_type_format(flask_app):
    """Tests incident type format validation"""
    data = {"incident_details": {"incident_date": "2018-02-02", "incident_nature": 0}}
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['incident_details']['incident_nature'][0] == 'Invalid value.'


def test_gin_format(flask_app, mocked_config):
    """Tests government identification number format validation"""
    data = {"personal_details": {"full_name": "test user", "gin": "44103-778987", "address": "test address pakistan",
                                 "email": "test@email.com", "dob": "1991-02-02", "number": "03301111112"}}
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['personal_details']['gin'][0] == 'Government Identification Number must contain {range} digits'.format(range=mocked_config['global'].get('gin_length'))


def test_number_format(flask_app):
    """Tests alternate phone number format validation"""
    data = {"personal_details": {"full_name": "test user", "gin": "44103-778987", "address": "test address pakistan",
                                 "email": "test@email.com", "dob": "1991-02-02", "number": "033012"}}
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['personal_details']['number'][0] == 'Alternate phone number is invalid.'


def test_other_parameters_format_case1(flask_app):
    """Tests other parameters format validation"""
    data = {"personal_details": {"full_name": "test user", "gin": "44103-7789877-2", "address": "",
                                 "email": "test@email.com", "dob": "1991-02-02", "number": "033012432423"}}
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['personal_details']['address'][0] == 'address should contain at least 1 character'


def test_other_parameters_format_case2(flask_app):
    """Tests other parameters format validation having more than 1000 characters"""
    data = {"personal_details": {"full_name": "test user", "gin": "44103-7789877-2", "address": "dsa"*1000,
                                 "email": "test@email.com", "dob": "1991-02-02", "number": "033012345678"}}
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['personal_details']['address'][0] == 'address cannot contain more than 1000 characters'


def test_email_format(flask_app):
    """Tests email format validation"""
    data = {"personal_details": {"full_name": "test user", "gin": "44103-778987", "address": "dsajkdhajksd",
                                 "email": "testemail.com", "dob": "1991-02-02", "number": "0330123223424"}}
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['personal_details']['email'][0] == 'Not a valid email address.'


def test_msisdn_format(flask_app):
    """Tests MSISDN format validation"""
    data = {"device_details": {"brand": "huawei", "model_name": "huawei mate 10", "description": "blue",
                               "imeis": ["37006822111120", "37006822111201"],
                               "msisdns": ["009233", "00923449826511"]}}
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['device_details']['msisdns']['0'] == ['MSISDN is invalid.']


def test_imei_format_case1(flask_app):
    """Tests IMEI format validation with IMEI having more than 16 characters"""
    data = {"device_details": {"brand": "huawei", "model_name": "huawei mate 10", "description": "blue",
                               "imeis": ["3700682211112042342", "37006822111201"],
                               "msisdns": ["0092333213122", "00923449826511"]}}
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['device_details']['imeis']['0'] == ['IMEI too long, cannot contain more than 16 characters']


def test_imei_format_case2(flask_app):
    """Tests IMEI format validation with IMEI having less than 14 characters"""
    data = {"device_details": {"brand": "huawei", "model_name": "huawei mate 10", "description": "blue",
                               "imeis": ["37006822111120", "3700682"],
                               "msisdns": ["009233332321", "00923449826511"]}}
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['device_details']['imeis']['1'] == ['IMEI too short, should contain at least 14 characters']


def test_imei_format_case3(flask_app):
    """Tests IMEI format validation with IMEI having invalid characters characters"""
    data = {"device_details": {"brand": "huawei", "model_name": "huawei mate 10", "description": "blue",
                               "imeis": ["37006822111120", "32131dsada2331"],
                               "msisdns": ["009233432422", "00923449826511"]}}
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['messages']['device_details']['imeis']['1'] == ['IMEI is invalid.']

