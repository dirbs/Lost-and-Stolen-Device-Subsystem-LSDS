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
        "imeis": ["37006234500020", "37006234530201"],
        "msisdns": ["00923323471007", "00923442346511"]
    }
}


def test_get_case(flask_app):
    """Tests case by tracking ID"""
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))['tracking_id']
    response = flask_app.get(case_api_url+'/'+response, content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    resp = json.loads(response.get_data(as_text=True))
    assert resp.get('creator') is not None
    assert resp.get('status') is not None
    assert resp.get('updated_at') is not None
    assert resp.get('created_at') is not None
    assert resp.get('comments') is not None
    assert resp.get('tracking_id') is not None
    assert resp.get('incident_details') is not None
    assert resp.get('personal_details') is not None
    assert resp.get('device_details') is not None
    assert resp.get('get_blocked') is not None


def test_get_case_response(flask_app):
    """Test case JSON response"""
    data['device_details']['imeis'] = ["37006234501234", "37006234531234"]
    response = flask_app.post(case_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))['tracking_id']
    response = flask_app.get(case_api_url+'/'+response, content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['incident_details'] is not None
    assert response['status'] is not None
    assert response['personal_details'] is not None
    assert response['creator'] is not None
    assert response['device_details'] is not None
    assert response['get_blocked']


def test_case_not_found(flask_app):
    """Test case with wrong tracking ID"""
    response = flask_app.get(case_api_url+'/sample-id', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 404
    assert response.mimetype == 'application/json'


def test_case_post_method(flask_app):
    """Test post request"""
    response = flask_app.post(case_api_url+'/sample-id', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_case_delete_method(flask_app):
    """Test delete request"""
    response = flask_app.delete(case_api_url+'/sample-id', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_not_found(flask_app):
    """Test case with empty tracking ID"""
    response = flask_app.get(case_api_url + '/""', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 404
    assert response.mimetype == 'application/json'
