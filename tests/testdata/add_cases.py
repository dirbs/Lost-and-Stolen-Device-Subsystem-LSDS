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
    "gin": "44103-1234567-2",
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
      "37006822000000",
      "37006822111111"
    ],
    "msisdns": [
      "00923339171007",
      "00923449826511"
    ]
  }
}

status = {
 "status_args": {
   "user_id": "1215c23-3f64-4af5-8713-35782374713d",
   "username":"muazzama",
   "case_comment": "Case recovered successfully.",
   "case_status": 1
 }
}


def pending_cases(flask_app):
    # Insert case 1
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    # Insert case 2
    data['device_details']['imeis'] = ["37006822000001", "37006822111112"]
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    # Insert case 3
    data['device_details']['imeis'] = ["37006822000002", "37006822111113"]
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200


def recovered_cases(flask_app):

    status['status_args']['case_status'] = 1
    # Insert case 4
    data['device_details']['imeis'] = ["37006822000003", "37006822111114"]
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    response = json.loads(response.get_data(as_text=True))
    tracking_id = response['tracking_id']

    # Update Status to recovered
    response = flask_app.patch(case_api_url+ '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 200

    # Insert case 5
    data['device_details']['imeis'] = ["37006822000004", "37006822111115"]
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    response = json.loads(response.get_data(as_text=True))
    tracking_id = response['tracking_id']

    # Update Status to recovered
    response = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 200

    # Insert case 6
    data['device_details']['imeis'] = ["37006822000005", "37006822111116"]
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    response = json.loads(response.get_data(as_text=True))
    tracking_id = response['tracking_id']

    # Update Status to recovered
    response = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 200


def blocked_cases(flask_app):
    # Insert case 7
    data['device_details']['imeis'] = ["37006822000006", "37006822111117"]
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    response = json.loads(response.get_data(as_text=True))
    tracking_id = response['tracking_id']

    # Update Status to blocked
    status['status_args']['case_status'] = 2
    response = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 200

    # Insert case 8
    data['device_details']['imeis'] = ["37006822000007", "37006822111118"]
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    response = json.loads(response.get_data(as_text=True))
    tracking_id = response['tracking_id']

    # Update Status to blocked
    status['status_args']['case_status'] = 2
    response = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 200

    # Insert case 9
    data['device_details']['imeis'] = ["37006822000008", "37006822111119"]
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    response = json.loads(response.get_data(as_text=True))
    tracking_id = response['tracking_id']

    # Update Status to blocked
    status['status_args']['case_status'] = 2
    response = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 200

    # Insert case 10
    data['device_details']['imeis'] = ["37006822000009", "37006822111110"]
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    response = json.loads(response.get_data(as_text=True))
    tracking_id = response['tracking_id']

    # Update Status to blocked
    status['status_args']['case_status'] = 2
    response = flask_app.patch(case_api_url + '/' + tracking_id, data=json.dumps(status), content_type='application/json')
    assert response.status_code == 200
