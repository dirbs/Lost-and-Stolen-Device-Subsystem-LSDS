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

from os import path
import pandas as pd
from app.api.v1.models.delta_list import DeltaList

list_api_url = 'api/v1/stolenlist'
upload_dir = path.dirname(path.dirname(__file__))


def test_list_gen_new_imeis(flask_app):
    """Test list generation with new IMEIs"""
    response = flask_app.get(list_api_url, content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'

    report = path.join(upload_dir+"/uploads", "stolen_delta_list.csv")
    task_file = pd.read_csv(report, sep=',', index_col=0)
    task_list = task_file.to_dict(orient='records')
    assert len(task_list) >= 10


def test_list_gen_existing_imeis(flask_app):
    """Test list generation with existing IMEIs"""
    data = [
        {
            'imei': '37006234531234',
            'case_status': 3
        },
        {
            'imei': '37006234501234',
            'case_status': 3
        },
        {
            'imei': '37006822111110',
            'case_status': 3
        },
        {
            'imei': '37006822000009',
            'case_status': 3
        },
        {
            'imei': '37006822000003',
            'case_status': 2
        },
        {
            'imei': '37006822000004',
            'case_status': 2
        },
        {
            'imei': '37006822000005',
            'case_status': 3
        },
        {
            'imei': '37006822111115',
            'case_status': 3
        }
    ]
    for d in data:
        DeltaList.insert(d.get('imei'), d.get('case_status'))
    response = flask_app.get(list_api_url, content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'

    report = path.join(upload_dir+"/uploads", "stolen_delta_list.csv")
    task_file = pd.read_csv(report, sep=',', index_col=0)
    task_list = task_file.to_dict(orient='records')
    assert len(task_list) >= 6


def test_list_post_method(flask_app):
    """Test post request"""
    response = flask_app.post(list_api_url, content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_list_put_method(flask_app):
    """Test put request"""
    response = flask_app.put(list_api_url, content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_list_patch_method(flask_app):
    """Test patch request"""
    response = flask_app.patch(list_api_url, content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_list_delete_method(flask_app):
    """Test delete request"""
    response = flask_app.delete(list_api_url, content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'
