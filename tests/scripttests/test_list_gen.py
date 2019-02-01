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
from scripts.stolen_list import GenList


def test_list_gen_new_imeis(app):
    """Test list generation with new IMEIs"""
    assert GenList.create_list()=="List has been saved successfully."
    report = path.join(app.config['dev_config']['UPLOADS']['list_dir'], "stolen_delta_list.csv")
    task_file = pd.read_csv(report, sep=',', index_col=0)
    task_list = task_file.to_dict(orient='records')
    assert len(task_list) >= 10


def test_list_gen_existing_imeis(app, flask_app):
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
    assert GenList.create_list()=="List has been saved successfully."

    report = path.join(app.config['dev_config']['UPLOADS']['list_dir'], "stolen_delta_list.csv")
    task_file = pd.read_csv(report, sep=',', index_col=0)
    task_list = task_file.to_dict(orient='records')
    assert len(task_list) >= 6
