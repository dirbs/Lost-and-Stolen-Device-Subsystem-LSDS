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
from app import app
import pandas as pd
import uuid
import tempfile
import requests
from ..models.bulk import Bulk
from ..models.case import Case
from ..helpers.common_resources import CommonResources


class BulkCommonResources:
    """Common functionality used across the system."""
    @staticmethod
    def save_file(file):
        tempdir = tempfile.mkdtemp()
        filepath = os.path.join(tempdir, file.filename)
        file.save(filepath)
        return filepath

    @staticmethod
    def clean_data(data):
        data = pd.DataFrame(data).astype(str)
        matched = data['imei'].str.match('^[a-fA-F0-9]{14,16}$')
        filtered_data = list(data[matched].T.to_dict().values())
        invalid_data = [{"imei": d['imei'], "status": "Invalid Data"} for d in data[~matched].T.to_dict().values()]
        for data in filtered_data:
            if data['alternate_number']=='nan':
                invalid_data.append({"imei": data['imei'], "status": "Missing alternate number"})
                filtered_data.remove(data)
        return filtered_data, invalid_data

    @staticmethod
    def block(filtered_data):
        failed_list = []
        success_list = []
        for data in filtered_data:
            flag = Case.find_data([data['imei']])
            flag2 = Bulk.find_bulk_data([data['imei']])
            if flag:
                BulkCommonResources.notify_users(data, app.config['system_config']['SMSC']['AlreadyExist'])
                failed_list.append({"imei": data['imei'], "status": "Exists in LSDS, reported at "+
                                                                    flag.get('created_at').strftime("%Y-%m-%d %H:%M:%S")
                                                                    +" with tracking id "+flag.get('tracking_id')+"."})
            elif flag2:
                BulkCommonResources.notify_users(data, app.config['system_config']['SMSC']['AlreadyExist'])
                failed_list.append({"imei": data['imei'], "status": "Exists in Bulk , reported at "+flag2.get('created_at').strftime("%Y-%m-%d %H:%M:%S")})
            else:
                subscribers = CommonResources.subscribers(data['imei'])
                if subscribers['subscribers']:
                    msisdns = [subs['msisdn'] for subs in subscribers['subscribers']]
                    if data['msisdn'] in msisdns:
                        if Bulk.find_bulk([data['imei']]):
                            Bulk.update_status(data['imei'])
                        else:
                            Bulk.create(data['imei'], data['msisdn'], 2, data['alternate_number'])
                        BulkCommonResources.notify_users(data, app.config['system_config']['SMSC']['Blocked'])
                        success_list.append(data['imei'])
                    else:
                        failed_list.append({"imei": data['imei'], "status": "Data does not match"})
                        BulkCommonResources.notify_users(data, app.config['system_config']['SMSC']['InfoMismatch'])
                else:
                    failed_list.append({"imei": data['imei'], "status": "Data does not match"})
                    BulkCommonResources.notify_users(data, app.config['system_config']['SMSC']['InfoMismatch'])
        return failed_list, success_list

    @staticmethod
    def unblock(filtered_data):
        failed_list = []
        success_list = []
        for data in filtered_data:
            flag = Bulk.get_case(data['imei'])
            if flag:
                if flag.get('status') == 1:
                    failed_list.append({"imei": data['imei'], "status": "Already unblocked"})
                    BulkCommonResources.notify_users(data, app.config['system_config']['SMSC']['AlreadyExist'])
                else:
                    Bulk.update_status(data['imei'])
                    success_list.append(data['imei'])
                    BulkCommonResources.notify_users(data, app.config['system_config']['SMSC']['Unblocked'])
            else:
                failed_list.append({"imei": data['imei'], "status": "Does not exist"})
                BulkCommonResources.notify_users(data, app.config['system_config']['SMSC']['DoesNotExist'])
        return failed_list, success_list

    @staticmethod
    def generate_report(failed_list, invalid_data, report_name):
        """Return non compliant report for DVS bulk request."""
        try:
            final_list = failed_list+invalid_data
            if final_list:
                complaint_report = pd.DataFrame(final_list)
                report_name = report_name + str(uuid.uuid4()) + '.tsv'
                complaint_report.to_csv(os.path.join(app.config['system_config']['UPLOADS']['report_dir'], report_name), sep= '\t')
            else:
                report_name = "report not generated."
            return report_name
        except Exception as e:
            app.logger.info("Error occurred while generating report.")
            app.logger.exception(e)
            raise e

    @staticmethod
    def notify_users(data, message):
        return requests.get('{base}?username={username}&password={password}&to={to}&text={text}&from={from_no}'.
                            format(base=app.config['system_config']['SMSC']['BaseUrl'],
                                   username=app.config['system_config']['SMSC']['Username'],
                                   to=data['alternate_number'], text=message,
                                   password=app.config['system_config']['SMSC']['Password'],
                                   from_no=app.config['system_config']['SMSC']['From']))

    @staticmethod
    def serialize_bulk_cases(cases):
        """Serialize response."""
        case_list = []
        for row in cases:
            case_list.append(dict((col, val) for col, val in row.items()))
        cases = []
        for case in case_list:
            case_detail = {
                "get_blocked": case.get('get_blocked'),
                "creator": {
                    "user_id": case.get('user_id'),
                    "username": case.get('username')
                },
                "personal_details": {
                    "address": case.get('address'),
                    "gin": case.get('gin'),
                    "email": case.get('email'),
                    "number": case.get('alternate_number'),
                    "full_name": case.get('full_name')
                },
                "tracking_id": str(case.get('id')),
                "comments": case.get('comments'),
                "incident_details": {
                    "incident_date": case.get('date_of_incident'),
                    "incident_nature": case.get('incident_type')
                },
                "created_at": case.get('created_at').strftime("%Y-%m-%d %H:%M:%S"),
                "device_details": {
                    "description": case.get('physical_description'),
                    "model_name": case.get('model_name'),
                    "imeis": [case.get('imei').replace(' ','')],
                    "msisdns": [case.get('msisdn').replace(' ','')],
                    "brand": case.get('brand')
                },
                "status": "Recovered" if case.get("status") == 1 else "Blocked" if case.get("status") == 2 else "Pending",
                "updated_at": case.get('updated_at').strftime("%Y-%m-%d %H:%M:%S"),
                "source": "Bulk"
            }
            cases.append(case_detail)
        return cases
