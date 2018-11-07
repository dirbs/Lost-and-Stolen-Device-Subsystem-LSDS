#######################################################################################################################
#                                                                                                                     #
# Copyright (c) 2018 Qualcomm Technologies, Inc.                                                                      #
#                                                                                                                     #
# All rights reserved.                                                                                                #
#                                                                                                                     #
# Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the      #
# limitations in the disclaimer below) provided that the following conditions are met:                                #
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following  #
#   disclaimer.                                                                                                       #
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the         #
#   following disclaimer in the documentation and/or other materials provided with the distribution.                  #
# * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or       #
#   promote products derived from this software without specific prior written permission.                            #
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED  #
# BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED #
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT      #
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR   #
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE,      #
# DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,      #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,   #
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                                  #
#                                                                                                                     #
#######################################################################################################################

import unittest
import json
from app import app


class AdminApisTests(unittest.TestCase):

    # Don't need db here yet
    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_imei_on_valid_imei(self):
        print('* test_fetch_valid_imei_info')
        imei = 12345678901234
        url = '/api/v1/imei/{imei}'.format(imei=imei)

        response = self.client.get(url)

        # check if response status is 200
        self.assertEqual(response.status_code, 200)

        # check if response length > 0
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_imei_on_seen_with(self):
        print('* test_fetch_imei_seen_with')
        imei = 12345678901234
        url = '/api/v1/imei/{imei}?seen_with=1'.format(imei=imei)

        response = self.client.get(url)

        # check if reponse is correct
        self.assertEqual(response.status_code, 200)

        # check if response length > 0
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_imei_on_post_method(self):
        print('* test_imei_on_post_method')
        url = '/api/v1/imei/123456789'

        response = self.client.post(url)

        # check if response code is not 200 OK
        self.assertNotEqual(response.status_code, 200)

        # check if response code is 405
        self.assertEqual(response.status_code, 405)

        # check the correct message
        data = json.loads(response.data)
        self.assertIn('The method is not allowed for the requested URL.', data.get('message'))

    def test_imei_on_put_method(self):
        print('* test_imei_on_put_method')
        url = '/api/v1/imei/123456789'

        response = self.client.put(url)

        # check if response code is not 200 OK
        self.assertNotEqual(response.status_code, 200)

        # check if response code is 405
        self.assertEqual(response.status_code, 405)

        # check the correct message
        data = json.loads(response.data)
        self.assertIn('The method is not allowed for the requested URL.', data.get('message'))

    def test_imei_on_delete_method(self):
        print('* test_imei_on_delete_method')
        url = '/api/v1/imei/123456789'

        response = self.client.delete(url)

        # check if response code is not 200 OK
        self.assertNotEqual(response.status_code, 200)

        # check if response code is 405
        self.assertEqual(response.status_code, 405)

        # check the correct message
        data = json.loads(response.data)
        self.assertIn('The method is not allowed for the requested URL.', data.get('message'))

    def test_msisdn_route_on_valid_params(self):
        print('* test_msisdn_route_on_valid_params')
        msisdn = 923339171007
        url = '/api/v1/msisdn/{msisdn}'.format(msisdn=msisdn)

        response = self.client.get(url)

        # check if response code is 200 OK
        self.assertEqual(response.status_code, 200)

        # check if data exists in the response
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_msisdn_route_on_invalid_params(self):
        print('* test_msisdn_route_on_invalid_params')
        msisdn = 00000
        url = '/api/v1/msisdn/{msisdn}'.format(msisdn=msisdn)

        response = self.client.get(url)

        # check if response is 200 OK
        self.assertEqual(response.status_code, 200)

        # check if data set is empty
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

    def test_msisdn_route_on_post(self):
        print('* test_msisdn_route_on_post')
        url = '/api/v1/msisdn/000000'

        response = self.client.post(url)

        # check if response code is not 200 OK
        self.assertNotEqual(response.status_code, 200)

        # check if response code is 405
        self.assertEqual(response.status_code, 405)

        # check the correct message
        data = json.loads(response.data)
        self.assertIn('The method is not allowed for the requested URL.', data.get('message'))

    def test_msisdn_route_on_put(self):
        print('* test_msisdn_route_on_put')
        url = '/api/v1/msisdn/000000'

        response = self.client.put(url)

        # check if response code is not 200 OK
        self.assertNotEqual(response.status_code, 200)

        # check if response code is 405
        self.assertEqual(response.status_code, 405)

        # check the correct message
        data = json.loads(response.data)
        self.assertIn('The method is not allowed for the requested URL.', data.get('message'))

    def test_msisdn_route_on_delete(self):
        print('* test_msisdn_route_on_delete')
        url = '/api/v1/msisdn/000000'

        response = self.client.delete(url)

        # check if response code is not 200 OK
        self.assertNotEqual(response.status_code, 200)

        # check if response code is 405
        self.assertEqual(response.status_code, 405)

        # check the correct message
        data = json.loads(response.data)
        self.assertIn('The method is not allowed for the requested URL.', data.get('message'))
