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

from flask_restful import Api
from .resources.common import BaseRoutes
from .resources.admin import FetchImei, FetchMsisdn
from .resources.system import IncidentNature, CaseStatus
from .resources.case import CaseRoutes, CaseList, InsertCase
from .resources.search import Search
from .resources.stolen_list import StolenList

# noinspection PyUnresolvedReferences
from .assets.error_handlers import *
from app.common.apidoc import ApiDocs
from app import APP_VERSION, app

api = Api(app, prefix='/api/v1', errors=CustomErrors)
apidoc = ApiDocs(app, APP_VERSION)

# noinspection PyTypeChecker
api.add_resource(BaseRoutes, '/')
# noinspection PyTypeChecker
api.add_resource(FetchImei, '/imei/<imei>')
# noinspection PyTypeChecker
api.add_resource(FetchMsisdn, '/msisdn/<msisdn>')
# noinspection PyTypeChecker
api.add_resource(IncidentNature, '/incident_types')
# noinspection PyTypeChecker
api.add_resource(CaseStatus, '/status_types')
# noinspection PyTypeChecker
api.add_resource(CaseRoutes, '/case/<tracking_id>')
# noinspection PyTypeChecker
api.add_resource(InsertCase, '/case')
# noinspection PyTypeChecker
api.add_resource(CaseList, '/cases')
# noinspection PyTypeChecker
api.add_resource(Search, '/search')
# noinspection PyTypeChecker
api.add_resource(StolenList, '/stolenlist')

docs = apidoc.init_doc()


def register():
    """Method to register routes for docs."""
    for route in [BaseRoutes, FetchImei, FetchMsisdn, IncidentNature, CaseStatus, CaseList, CaseStatus, Search,
                  CaseRoutes, InsertCase]:
        docs.register(route)

register()