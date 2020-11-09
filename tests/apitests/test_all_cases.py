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

from tests.testdata.add_cases import *

case_api_url = 'api/v1/cases'


def test_empty_db(flask_app):
    """Tests all cases in case of empty database"""
    response = flask_app.get(case_api_url, content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['count'] == 0


def test_empty_pending_cases(flask_app):
    """Tests all pending cases in case of empty database"""
    response = flask_app.get(case_api_url+'?start=1&limit=10&status=3', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['count'] == 0


def test_empty_blocked_cases(flask_app):
    """Tests all blocked cases in case of empty database"""
    response = flask_app.get(case_api_url+'?start=1&limit=10&status=2', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['count'] == 0


def test_empty_recovered_cases(flask_app):
    """Tests all recovered cases in case of empty database"""
    response = flask_app.get(case_api_url+'?start=1&limit=10&status=1', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['count'] == 0


def test_pending_cases(flask_app):
    """Tests all pending cases"""
    pending_cases(flask_app)
    response = flask_app.get(case_api_url+'?start=1&limit=10&status=3', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['count'] > 0


def test_blocked_cases(flask_app):
    """Tests all blocked cases"""
    blocked_cases(flask_app)
    response = flask_app.get(case_api_url+'?start=1&limit=10&status=2', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['count'] > 0


def test_recovered_cases(flask_app):
    """Tests all recovered cases"""
    recovered_cases(flask_app)
    response = flask_app.get(case_api_url+'?start=1&limit=10&status=1', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['count'] > 0


def test_all_cases(flask_app):
    """Tests all cases"""
    response = flask_app.get(case_api_url+'?start=1&limit=11', content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response = json.loads(response.get_data(as_text=True))
    assert response['count'] > 0


def test_case_post_method(flask_app):
    """Tests post request"""
    response = flask_app.post(case_api_url, content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_case_delete_method(flask_app):
    """Tests delete request"""
    response = flask_app.delete(case_api_url, content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_case_put_method(flask_app):
    """Tests put request"""
    response = flask_app.post(case_api_url, content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'


def test_case_patch_method(flask_app):
    """Tests patch request"""
    response = flask_app.delete(case_api_url, content_type='application/json')
    assert response.status_code == 405
    assert response.mimetype == 'application/json'
