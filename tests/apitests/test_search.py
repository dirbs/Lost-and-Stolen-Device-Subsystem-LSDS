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
from datetime import datetime, timedelta

search_api_url = 'api/v1/search'


def test_search(flask_app):
    data = {
        "limit": 100,
        "start": 1,
        "search_args": {

        }
    }
    response = flask_app.post(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert len(response['cases']) > 0


def test_search_get_method(flask_app):
    data = {}
    response = flask_app.get(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_search_put_method(flask_app):
    data = {}
    response = flask_app.put(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_search_patch_method(flask_app):
    data = {}
    response = flask_app.patch(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_search_delete_method(flask_app):
    data = {}
    response = flask_app.delete(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_search_status(flask_app):
    data = {
        "limit": 100,
        "start": 1,
        "search_args": {
            "status": "Pending"
        }
    }
    response = flask_app.post(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert len(response['cases']) > 0


def test_search_imei(flask_app):
    data = {
        "limit": 100,
        "start": 1,
        "search_args": {
            "status": "Pending",
            "imeis": ["37006822000000", "37006822000002", "37006822000003", "37006822111112"]
        }
    }
    response = flask_app.post(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert len(response['cases']) > 0


def test_search_msisdn(flask_app):
    data = {
        "limit": 100,
        "start": 1,
        "search_args": {
            "status": "Recovered",
            "msisdns": ["00923339171007"]
        }
    }
    response = flask_app.post(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert len(response['cases']) > 0


def test_search_incident_date(flask_app):
    data = {
        "limit": 100,
        "start": 1,
        "search_args": {
            "status": "Recovered",
            "date_of_incident": "2018-02-02,2018-02-04"
        }
    }
    response = flask_app.post(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert len(response['cases']) > 0


def test_search_no_cases(flask_app):
    data = {
        "limit": 100,
        "start": 1,
        "search_args": {
            "status": "sample"
        }
    }
    response = flask_app.post(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert len(response['cases']) == 0


def test_search_exception(flask_app):
    data = {
        "limit": 100,
        "start": 1,
        "search_args": {
            "status": "Recovered",
            "date_of_incident": "2018-02-02-2018-02-04"
        }
    }
    response = flask_app.post(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 503
    assert response.mimetype == 'application/json'


def test_search_validation(flask_app):
    data = {
        "limit": 0,
        "start": 0,
        "search_args": {
            "status": "sample",
            "date_of_incident": ["2018-02-02-2018-02-04"]
        }
    }
    response = flask_app.post(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 422
    assert response.mimetype == 'application/json'


def test_search_on_strings(flask_app):
    data = {
        "limit": 100,
        "start": 1,
        "search_args": {
            "status": "Recovered",
            "dob": "1991-02-02",
            "email": "test@email.com",
            "alternate_number": "03301111112",
            "full_name": "test user",
            "gin": "44103-1234567-2",
            "address": "test address pakistan",
            "incident": "lost",
            "brand": "huawei",
            "model": "huawei mate 10",
            "description": "blue"
        }
    }
    response = flask_app.post(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert len(response['cases']) > 0


def test_search_tracking_id(flask_app):
    creation_data = {
        "case_details": {
            "get_blocked": True
        },
        "loggedin_user": {
            "user_id": "1215c23-3f64-4af5-8713-35782374713d",
            "username": "muazzama anwar"
        },
        "incident_details": {
            "incident_date": "2016-02-02",
            "incident_nature": 2
        },
        "personal_details": {
            "full_name": "test search user",
            "gin": "44103-1234567-3",
            "address": "test address islamabad pakistan",
            "email": "test@email.com",
            "dob": "1991-02-02",
            "number": "03301111112"
        },
        "device_details": {
            "brand": "huawei",
            "model_name": "huawei mate 10",
            "description": "huawei's phone",
            "imeis": [
                "37006822006789",
                "37006822009087"
            ],
            "msisdns": [
                "00923339171007",
                "00923449826511"
            ]
        }
    }

    response = flask_app.post('api/v1/case', data=json.dumps(creation_data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    tracking_id = json.loads(response.get_data(as_text=True))['tracking_id']

    updated_at_min = datetime.now().strftime("%Y-%m-%d")
    updated_at_max = datetime.now() + timedelta(hours=23, minutes=59, seconds=59)
    updated_at_max = updated_at_max.strftime("%Y-%m-%d")

    updated_at = updated_at_min + "," + updated_at_max
    data = {
        "limit": 100,
        "start": 1,
        "search_args": {
            "tracking_id": tracking_id,
            "description": "huawei's",
            "updated_at": updated_at
        }
    }
    response = flask_app.post(search_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert len(response['cases']) == 1
