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

from app import db, app
from app.api.v1.models.eshelper import es
from app.api.v1.helpers.common_resources import CommonResources
from app.api.v1.helpers.bulk_helpers import BulkCommonResources


class DataMigration:

    @staticmethod
    def fetch_data():
        sql = "select c.*, cid.date_of_incident, cid.nature_of_incident, cpd.full_name, cpd.address, cpd.alternate_number, cpd.email, cpd.gin, dd.brand, dd.model_name, dd.physical_description, s.description as status, ni.name as incident_type, string_agg(distinct(di.imei::text), ', '::text) as imeis, string_agg(distinct(msisdn::text), ', '::text) as msisdns, string_agg(distinct(json_build_object('comment',cc.comments, 'comment_date',cc.comment_date, 'user_id',cc.user_id, 'username',cc.username, 'id',cc.id)::text), '| '::text) as comments from public.case as c left join case_comments as cc on cc.case_id=c.id, case_incident_details as cid, case_personal_details as cpd, device_details as dd, device_imei as di, device_msisdn as dm, public.status as s, public.nature_of_incident as ni where cid.case_id=c.id and cpd.case_id=c.id and dd.case_id=c.id and di.device_id=dd.id and dm.device_id=dd.id  and s.id=c.case_status and ni.id=cid.nature_of_incident group by c.id, cid.date_of_incident, cid.nature_of_incident, cpd.full_name, cpd.alternate_number, cpd.address, cpd.email, cpd.gin, dd.brand, dd.model_name, dd.physical_description, s.description, ni.name order by c.updated_at desc"
        cases = db.session.execute(sql)
        cases = CommonResources.serialize_cases(cases)
        bulk = db.session.execute('select * from public.bulk')
        bulk_cases = BulkCommonResources.serialize_bulk_cases(bulk)
        return cases+bulk_cases

    @staticmethod
    def clean_data(cases):
        new_list = []
        for case in cases:
            new_case = {}
            for k, v in case.items():
                if isinstance(v, dict):
                    for x, y in v.items():
                        if isinstance(y, str):
                            v[x] = y.replace("\r\n", "").replace("\n", "")
                            new_case[k] = v
                        else:
                            v[x] = y
                            new_case[k] = v
                else:
                    new_case[k] = v
            new_list.append({"index": {"_index": app.config['system_config']['Database']['Database'], "_type": "_doc", "_id": new_case['tracking_id']}})
            new_list.append(new_case)
        return new_list

    @staticmethod
    def clean_data_send(case):
        new_case = {}
        for k, v in case.items():
            if isinstance(v, dict):
                for x, y in v.items():
                    if isinstance(y, str):
                        v[x] = y.replace("\r\n", "").replace("\n", "")
                        new_case[k] = v
                    else:
                        v[x] = y
                        new_case[k] = v
            else:
                new_case[k] = v
        return new_case

    @staticmethod
    def gendata(new_list):
        for word in new_list:
            yield word

    @staticmethod
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    @staticmethod
    def bulk_insert():
        cases = DataMigration.fetch_data()
        chunked_cases = DataMigration.chunks(cases, 1000)
        for chunk in chunked_cases:
            new_list = DataMigration.clean_data(chunk)
            es.bulk(DataMigration.gendata(new_list), request_timeout=1000)
        return str(len(cases))+" records migrated successfully."

    @staticmethod
    def single_insert():
        cases = DataMigration.fetch_data()
        for i, case in enumerate(cases):
            cleaned_case = DataMigration.clean_data_send(case)
            es.index(index=app.config['system_config']['Database']['Database'], id=cleaned_case['tracking_id'], body=cleaned_case)
        return str(len(cases)) + " inserted successfully."
