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
from .apitests.test_basiccApis import BasicTestCase
from .apitests.test_adminApis import AdminApisTests


def base_api_test_suite():
    print('------ Base APIs Test Suite ------')
    test_suite = unittest.TestSuite()
    test_suite.addTest(BasicTestCase('test_index_route'))
    test_suite.addTest(BasicTestCase('test_base_route'))

    return test_suite


def admin_api_test_suite():
    print('------ Admin APIs Test Suite ------')
    test_suite = unittest.TestSuite()
    test_suite.addTest(AdminApisTests('test_imei_on_valid_imei'))
    test_suite.addTest(AdminApisTests('test_imei_on_seen_with'))
    test_suite.addTest(AdminApisTests('test_imei_on_post_method'))
    test_suite.addTest(AdminApisTests('test_msisdn_route_on_valid_params'))
    test_suite.addTest(AdminApisTests('test_msisdn_route_on_invalid_params'))
    test_suite.addTest(AdminApisTests('test_msisdn_route_on_post'))
    test_suite.addTest(AdminApisTests('test_msisdn_route_on_put'))
    test_suite.addTest(AdminApisTests('test_msisdn_route_on_delete'))

    return test_suite


if __name__ == '__main__':
    print('------ Running Test Cases ------')
    runner = unittest.TextTestRunner()
    runner.run(base_api_test_suite())
    runner.run(admin_api_test_suite())
