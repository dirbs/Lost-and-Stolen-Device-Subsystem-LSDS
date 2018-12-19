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


def test_index(flask_app):
    """Tests index route"""
    response = flask_app.get('/', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['message'] == "Welcome to LSDS"


def test_db_status(db):
    """Tests status types seeding"""
    query = "select * from public.status"
    data = db.engine.execute(query)
    assert len([d for d in data]) == 3


def test_db_incident_types(db):
    """Tests incident types seeding"""
    query = "select * from public.nature_of_incident"
    data = db.engine.execute(query)
    assert len([d for d in data]) == 2


def test_connections(flask_app):
    """Test DB connection"""
    response = flask_app.get('api/v1/', content_type='application/json')
    assert response.status_code == 200
    response = json.loads(response.get_data(as_text=True))
    assert response['db_status'] == 'Database connected successfully'
