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
update_api_url = 'api/v1/update_case'

creation_data = {
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
        "imeis": [
          "37006234512323",
          "37006234512334"
        ],
        "msisdns": [
          "00923323471007",
          "00923442346511"
        ]
    }
}

status = {
 "status_args": {
   "user_id": "1215c23-3f64-4af5-8713-35782374713d",
   "username":"muazzama",
   "case_comment": "Case blocked successfully.",
   "case_status": 2
 }
}

update_data = {
  "case_details": {
    "get_blocked": False
  },
  "status_args": {
    "case_comment": "string",
    "user_id": "string",
    "username": "string"
  }
}


def test_update_status(flask_app):
    """Test update case success response"""
    response = flask_app.post(case_api_url, data=json.dumps(creation_data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    tracking_id = json.loads(response.get_data(as_text=True))['tracking_id']

    status['status_args']['case_status'] = 3
    response = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 409
    assert response.mimetype == 'application/json'

    status['status_args']['case_status'] = 2
    response = flask_app.patch(case_api_url+'/'+tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['message'] is not None

    status['status_args']['case_status'] = 1
    response = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['message'] is not None
    assert response['tracking_id'] == tracking_id

    status['status_args']['case_status'] = 2
    response = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 406
    assert response.mimetype == 'application/json'


def test_get_blocked_scenario1(flask_app):
    """Test update case JSON response"""
    creation_data['device_details']['imeis'] = ["37002344561234", "37054332331234"]
    creation_data['case_details']['get_blocked'] = False

    # insert new case
    response = flask_app.post(case_api_url, data=json.dumps(creation_data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    tracking_id = json.loads(response.get_data(as_text=True))['tracking_id']

    # get case
    response = flask_app.get(case_api_url + '/' + tracking_id, content_type='application/json')
    response = json.loads(response.get_data(as_text=True))
    assert response['personal_details'] == {"full_name": "test user", "gin": "44103-7789877-2",
                                            "address": "test address pakistan", "email": "test@email.com",
                                            "dob": "1991-02-02", "number": "03301111112"}
    assert response['status'] is not None

    # update case status to blocked while get blocked is false
    tracking_id = response['tracking_id']
    response = flask_app.patch(case_api_url+'/'+tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 406
    assert response.mimetype == 'application/json'

    # update case status to pending
    status['status_args']['case_status'] = 3
    resp = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert resp.status_code == 409
    assert resp.mimetype == 'application/json'

    # update case status to recovered while get blocked is false
    status['status_args']['case_status'] = 1
    resp = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'


def test_get_blocked_scenario2(flask_app):
    """Test update case JSON response"""
    creation_data['device_details']['imeis'] = ["37002334561234", "37052332331234"]
    creation_data['case_details']['get_blocked'] = False

    # insert new case
    response = flask_app.post(case_api_url, data=json.dumps(creation_data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    tracking_id = json.loads(response.get_data(as_text=True))['tracking_id']

    # get case
    response = flask_app.get(case_api_url + '/' + tracking_id, content_type='application/json')
    response = json.loads(response.get_data(as_text=True))
    assert response['personal_details'] == {"full_name": "test user", "gin": "44103-7789877-2",
                                            "address": "test address pakistan", "email": "test@email.com",
                                            "dob": "1991-02-02", "number": "03301111112"}
    assert response['status'] is not None

    # update case status to blocked while get blocked is false
    tracking_id = response['tracking_id']
    status['status_args']['case_status'] = 2
    response = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status),
                               content_type='application/json')
    assert response.status_code == 406
    assert response.mimetype == 'application/json'

    # update case status to pending
    status['status_args']['case_status'] = 3
    resp = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert resp.status_code == 409
    assert resp.mimetype == 'application/json'

    # update get blocked information to true
    update_data['case_details']['get_blocked'] = True
    response = flask_app.patch(update_api_url + '/' + tracking_id, data=json.dumps(update_data),
                               content_type='application/json')
    assert response.status_code == 200
    response = json.loads(response.get_data(as_text=True))
    assert response['message'] is not None

    # update case status to blocked
    tracking_id = response['tracking_id']
    status['status_args']['case_status'] = 2
    response = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status),
                               content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    # update case status to recovered while get blocked is false
    status['status_args']['case_status'] = 1
    resp = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'


def test_input_format(flask_app):
    """Test update case input format"""
    creation_data['device_details']['imeis'] = ["37002000001238", "37054000031267"]
    response = flask_app.post(case_api_url, data=json.dumps(creation_data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    tracking_id = json.loads(response.get_data(as_text=True))['tracking_id']

    update_data['case_details']['get_blocked'] = ""
    response = flask_app.patch(update_api_url + '/' + tracking_id, data=json.dumps(update_data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['messages']['case_details']['get_blocked'][0] is not None


def test_case_not_found(flask_app):
    """Test update case with invalid tracking ID"""
    update_data['case_details']['get_blocked'] = True
    response = flask_app.patch(update_api_url+'/sample-id', data=json.dumps(update_data), content_type='application/json')
    assert response.status_code == 404
    assert response.mimetype == 'application/json'
