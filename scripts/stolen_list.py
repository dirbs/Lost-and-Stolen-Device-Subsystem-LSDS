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

import os
import time
from app import db, app
import pandas as pd
from collections import OrderedDict
from datetime import datetime

from app.api.v1.models.delta_list import DeltaList
from tqdm import *


class GenList:
    """Class for list generation."""

    @staticmethod
    def get_distinct_imeis():
        try:
            app.logger.info("Delta list generation has started.")
            response_data = []  # distinct imeis list
            done = set()  # set of distinct IMEIs
            sql = "select case_status, created_at, i.imei from public.case as c, device_details as d, device_imei as i where d.case_id=c.id and d.id=i.device_id"
            query = db.engine.execute(sql)  # retrieve imeis from case, device and imei models
            for row in reversed(list(query)):  # iterate results
                data = dict((col, val) for col, val in row.items())  # serialize in key, value pairs
                if data['imei'] not in done:  # save distinct imeis
                    done.add(data['imei'])  # note it down for further iterations
                    response_data.append(data)  # append distinct imei
            app.logger.info("Distinct IMEI list from Database generated successfully")
            return response_data
        except Exception as e:
            app.logger.critical("Exception occurred while getting distinct imeis in list generation process")
            app.logger.exception(e)
            return "Exception occurred while getting distinct imeis."

    @staticmethod
    def get_distinct_bulk_imeis():
        try:
            app.logger.info("getting IMEIs from Bulk.")
            response_data = []  # distinct imeis list
            done = set()  # set of distinct IMEIs
            sql = "select status, created_at, imei, msisdn from public.bulk"
            query = db.engine.execute(sql)  # retrieve imeis from case, device and imei models
            for row in reversed(list(query)):  # iterate results
                data = dict((col, val) for col, val in row.items())  # serialize in key, value pairs
                if data['imei'] not in done:  # save distinct imeis
                    done.add(data['imei'])  # note it down for further iterations
                    data['case_status'] = data['status']
                    response_data.append(data)  # append distinct imei
            app.logger.info("Distinct IMEI list from Database generated successfully")
            return response_data
        except Exception as e:
            app.logger.critical("Exception occurred while getting distinct imeis in list generation process")
            app.logger.exception(e)
            return "Exception occurred while getting distinct imeis."

    @staticmethod
    def create_list():
        """Generates delta stolen list."""
        try:
            trigger = 'SET ROLE delta_list_user; COMMIT;'
            db.session.execute(trigger)
            resp1 = GenList.get_distinct_imeis()
            resp2 = GenList.get_distinct_bulk_imeis()
            resp = resp1+resp2
            app.logger.info("Comparing IMEIs with previous delta...")
            delta_list = []  # delta list
            for data in tqdm(resp):  # iterate distince imeis
                time.sleep(0.1)
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
            if len(delta_list)>0:
                app.logger.info("Delta list prepared successfully")
                return GenList.upload_list(delta_list, 'StolenDeltaList')
            else:
                return "No IMEIs to export. Exiting!!"
        except Exception as e:
            app.logger.critical("exception encountered during delta list generation, see blow logs")
            app.logger.exception(e)
            return "Exception occurred check logs."
        finally:
            db.session.close()

    @staticmethod
    def upload_list(list, name):
        try:
            stolen_delta_list = pd.DataFrame(list)
            time = datetime.now().strftime("%m-%d-%YT%H%M%S")
            report_name = name+time+'.csv'
            stolen_delta_list.to_csv(os.path.join(app.config['system_config']['UPLOADS']['list_dir'], report_name), sep=',', index=False)  # writing stolen list to .csv file
            app.logger.info("Delta list saved successfully")
            return "List "+report_name+" has been saved successfully."
        except Exception as e:
            app.logger.critical("Exception occurred while uploading delta list")
            app.logger.exception(e)
            return "Exception occurred while uploading list."

    @staticmethod
    def get_full_list():
        try:
            trigger = 'SET ROLE delta_list_user; COMMIT;'
            db.session.execute(trigger)
            app.logger.info("Full List generation has started.")
            response_data = []  # distinct imeis list
            sql = "select case_status, created_at, i.imei from public.case as c, device_details as d, device_imei as i where d.case_id=c.id and d.id=i.device_id"
            query = db.engine.execute(sql)  # retrieve imeis from case, device and imei models
            resp1 = list(query)
            resp2 = GenList.get_distinct_bulk_imeis()
            results = resp1 + resp2
            with tqdm(total=len(results)) as pbar:
                for row in reversed(results):  # iterate results
                    tqdm.update(pbar)
                    time.sleep(0.2)
                    data = dict((col, val) for col, val in row.items())  # serialize in key, value pairs
                    if data['case_status']!=1:
                        record = OrderedDict()
                        record['imei'] = data.get('imei')
                        record["reporting_date"] = data.get('created_at').strftime("%Y%m%d")
                        # add current status of imei
                        record["status"] = "pending" if data.get('case_status') == 3 else "recovered" if data.get(
                            'case_status') == 1 else "blacklist"
                        response_data.append(record)  # append distinct imei
            app.logger.info("Full list prepared successfully")
            return GenList.upload_list(response_data, 'StolenFullList')
        except Exception as e:
            app.logger.critical("Exception occurred while getting distinct imeis in list generation process")
            app.logger.exception(e)
            return "Exception occurred while getting distinct imeis."

