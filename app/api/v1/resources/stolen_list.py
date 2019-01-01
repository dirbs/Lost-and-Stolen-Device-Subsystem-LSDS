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

from app import db, app
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
            response_data = []  # distinct imeis list
            done = set()  # set of distinct IMEIs
            sql = "select case_status, created_at, i.imei from public.case as c, device_details as d, device_imei as i where d.case_id=c.id and d.id=i.device_id"
            query = db.engine.execute(sql)  # retrieve imeis from case, device and imei models
            for row in reversed(list(query)):  # iterate results
                data = dict((col, val) for col, val in row.items())  # serialize in key, value pairs
                if data['imei'] not in done:  # save distinct imeis
                    done.add(data['imei'])  # note it down for further iterations
                    response_data.append(data)  # append distinct imei
            delta_list = []  # delta list
            for data in response_data:  # iterate distince imeis
                sql = "select imei, status from delta_list where imei='"+data.get('imei')+"'"
                query = db.engine.execute(sql)  # check if imei already exists in delta list model
                result = list(query)
                if result:  # if exists
                    for row in result:
                        if row[1] != data.get('case_status'):  # if imei in delta list and case model have diff status
                            record = OrderedDict()
                            record['imei'] = data.get('imei')
                            record["reporting_date"] = data.get('created_at').strftime("%Y%m%d")
                            # add current status of imei
                            record["status"] = "pending" if data.get('case_status') == 3 else "recovered" if data.get('case_status') == 1 else "blacklist"
                            # update change type in delta list accordingly
                            record["change_type"] = "add" if row[1] == 1 and (data.get('case_status') == 3 or data.get('case_status') == 2) else "update" if row[1] == 3 and data.get('case_status') == 2 else "remove"

                            delta_list.append(record)  # update delta list
                            DeltaList.update(data.get('imei'), data.get('case_status'))   # update delta list model
                else:  # if imei already not in delta list
                    if data.get('case_status') != 1:  # imei should not be in recovered status
                        record = OrderedDict()
                        record['imei'] = data.get('imei')
                        record['reporting_date'] = data.get('created_at').strftime("%Y%m%d")
                        record['status'] = "pending" if data.get('case_status') == 3 else "recovered" if data.get('case_status') == 1 else "blacklist"
                        record['change_type'] = "add"  # assign change type to add for every new imei

                        delta_list.append(record)  # append record to delta list
                        DeltaList.insert(data.get('imei'), data.get('case_status'))  # insert new entry in delta list model
            stolen_delta_list = pd.DataFrame(delta_list)
            report_name = 'stolen_delta_list.csv'
            if not stolen_delta_list.empty:
                stolen_delta_list.to_csv(os.path.join(app.config['dev_config']['UPLOADS']['list_dir'], report_name), sep=',', index=False)  # writing stolen list to .csv file
            return send_from_directory(directory=app.config['dev_config']['UPLOADS']['list_dir'], filename=report_name)  # returns downloadable file
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
