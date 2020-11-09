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

import pytest
from app.api.v1.models.case import Case


def test_case_insertion(session):
    """Test case insertion"""
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
            "imeis": [
                "123456789009876",
                "123456789098765"
            ],
            "msisdns": [
                "00923339171007",
                "00923449826511"
            ]
        }
    }

    tracking_id = Case.create(data)
    tracking_id = tracking_id['data']

    # check entry in database
    res = session.execute("SELECT * FROM public.case WHERE tracking_id='"+tracking_id+"'").fetchone()
    assert res.user_id == data['loggedin_user']['user_id']
    assert res.username == data['loggedin_user']['username']
    assert res.case_status == 3
    assert res.tracking_id == tracking_id

    resp = Case.create(data)
    assert resp['code'] == 409

    with pytest.raises(Exception) as excinfo:
        data['device_details']['imeis'] = [256351763527134, 4327864278462]
        Case.create(data)
    assert str(excinfo.value) is not None

    data['personal_details'] = {"full_name": "test user"}
    data['device_details']['imeis'] = ["123456789012345", "123456789123456"]

    response = Case.create(data)
    assert response['code'] == 400


def test_update_case(session):
    """Test case information update"""
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
            "imeis": [
                "876543219009876",
                "876543219098765"
            ],
            "msisdns": [
                "00923339171007",
                "00923449826511"
            ]
        }
    }

    tracking_id = Case.create(data)
    tracking_id = tracking_id['data']

    # check entry in database
    res = session.execute("SELECT * FROM public.case WHERE tracking_id='" + tracking_id + "'").fetchone()
    assert res.user_id == data['loggedin_user']['user_id']
    assert res.username == data['loggedin_user']['username']
    assert res.case_status == 3
    assert res.tracking_id == tracking_id

    data = {
        "status_args": {
            "user_id": "12132-cds3213-d3242",
            "case_comment": "case updated",
            "username": "abc"
        },
        "personal_details": {
            "full_name": "yasir zeeshan",
            "dob": "1990-12-03",
            "address": "peshawar pakistan",
            "gin": "1720181482510",
            "number": "00923358907123",
            "email": "yasir@example.com"
        }
    }

    Case.update(data, tracking_id)

    # check entry in database
    res = Case.get_case(tracking_id)

    assert res['tracking_id'] == tracking_id
    assert res['personal_details']['full_name'] == data['personal_details']['full_name']
    assert res['personal_details']['dob'] == data['personal_details']['dob']
    assert res['personal_details']['email'] == data['personal_details']['email']
    assert res['personal_details']['gin'] == data['personal_details']['gin']
    assert res['personal_details']['address'] == data['personal_details']['address']
    assert res['personal_details']['number'] == data['personal_details']['number']

    with pytest.raises(Exception) as excinfo:
        data['personal_detas']['number'] = 437642784682376
        Case.update(data, tracking_id)
    assert str(excinfo.value) is not None


def test_update_case_status(session):
    """Test update case status"""
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
            "imeis": [
                "876543219123456",
                "876543219098712"
            ],
            "msisdns": [
                "00923339171007",
                "00923449826511"
            ]
        }
    }

    tracking_id = Case.create(data)
    tracking_id = tracking_id['data']

    # check entry in database
    res = session.execute("SELECT * FROM public.case WHERE tracking_id='" + tracking_id + "'").fetchone()
    assert res.user_id == data['loggedin_user']['user_id']
    assert res.username == data['loggedin_user']['username']
    assert res.case_status == 3
    assert res.tracking_id == tracking_id

    data = {
        "status_args": {
            "user_id": "1215c23-3f64-4af5-8713-35782374713d",
            "username": "muazzama",
            "case_comment": "Case blocked successfully.",
            "case_status": 2
        }
    }

    resp = Case.update_status(data['status_args'], tracking_id)

    # check entry in database
    res = Case.get_case(resp)

    assert res['status'] == "Blocked"

    resp = Case.update_status(data['status_args'], tracking_id)

    assert resp == 409

    data['status_args']['case_status'] = 3

    resp = Case.update_status(data['status_args'], tracking_id)

    assert resp == 406

    resp = Case.update_status(data['status_args'], "sample-id")

    assert resp is None

    resp = Case.update_case(tracking_id)
    assert resp is None


def test_find_data():
    """Test if data exists"""
    imeis = ["876543219123456", "876543219098712"]

    resp = Case.find_data(imeis)
    assert resp['imei'] is not None

    imeis = ["4732894623784", "34627842784632"]
    resp = Case.find_data(imeis)
    assert resp['imei'] is None

    with pytest.raises(Exception, message="Exception expected.") as execinfo:
        imeis = [256351763527134, 4327864278462]
        Case.find_data(imeis)
    assert str(execinfo.value) is not None
