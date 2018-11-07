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

import os
import json

from app import UPLOADS, db, app
from flask import Response, send_from_directory
from flask_restful import Resource
import pandas as pd
from collections import OrderedDict

from ..models.delta_list import DeltaList
from ..assets.error_handlers import MIME_TYPES, CODES


class StolenList(Resource):
    """Flask resource for delta stolen list."""

    @staticmethod
    def get():
        """Generates delta stolen list."""

        try:
            response_data = []
            done = set()
            sql = "select case_status, created_at, i.imei from public.case as c, device_details as d, device_imei as i where d.case_id=c.id and d.id=i.device_id"
            query = db.engine.execute(sql)
            for row in reversed(list(query)):
                data = dict((col, val) for col, val in row.items())
                if data['imei'] not in done:
                    done.add(data['imei'])  # note it down for further iterations
                    response_data.append(data)
            delta_list = []
            for data in response_data:
                sql = "select imei, status from delta_list where imei='"+data.get('imei')+"'"
                query = db.engine.execute(sql)
                result = list(query)
                if result:
                    for row in result:
                        if row[1] != data.get('case_status'):
                            record = OrderedDict()
                            record['imei'] = data.get('imei')
                            record["reporting_date"] = data.get('created_at').strftime("%Y%m%d")
                            record["status"] = "pending" if data.get('case_status') == 3 else "recovered" if data.get('case_status') == 1 else "blacklist"
                            record["change_type"] = "add" if row[1] == 1 and (data.get('case_status') == 3 or data.get('case_status') == 2) else "update" if row[1] == 3 and data.get('case_status') == 2 else "remove"

                            delta_list.append(record)
                            DeltaList.update(data.get('imei'), data.get('case_status'))
                else:
                    if data.get('case_status') != 1:
                        record = OrderedDict()
                        record['imei'] = data.get('imei')
                        record['reporting_date'] = data.get('created_at').strftime("%Y%m%d")
                        record['status'] = "pending" if data.get('case_status') == 3 else "recovered" if data.get('case_status') == 1 else "blacklist"
                        record['change_type'] = "add"

                        delta_list.append(record)
                        DeltaList.insert(data.get('imei'), data.get('case_status'))
            stolen_delta_list = pd.DataFrame(delta_list)
            report_name = 'stolen_delta_list.csv'
            if not stolen_delta_list.empty:
                stolen_delta_list.to_csv(os.path.join(UPLOADS, report_name), sep=',', index=False)  # writing stolen list to .csv file
            return send_from_directory(directory=UPLOADS, filename=report_name)  # returns downloadable file
        except Exception as e:
            app.logger.critical("exception encountered during delta list generation, see blow logs")
            app.logger.exception(e)
            data = {
                "message": "Database connectivity error."
            }
            response = Response(json.dumps(data), status=CODES.get("INTERNAL_SERVER_ERROR"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            return response
        finally:
            db.session.close()
