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

from app import app, db
from flask_babel import _
import requests
import json
from ..models.case import Case


class CommonResources:
    """Common functionality used across the system."""

    @staticmethod
    def get_imei(imei):
        """Return IMEI response fetched from DIRBS core."""

        imei_url = requests.get(
            '{base}/{version}/imei/{imei}'.format(base=app.config['system_config']['dirbs_core']['base_url'],
                                                  version=app.config['system_config']['dirbs_core']['version'],
                                                  imei=imei))  # dirbs core imei api call
        try:
            if imei_url.status_code == 200:
                response = imei_url.json()
                return response
            else:
                return None
        except Exception as error:
            raise error

    @staticmethod
    def get_tac(tac):
        """Return TAC response fetched from DIRBS core."""

        try:
            tac_response = requests.get('{}/{}/tac/{}'.format(app.config['system_config']['dirbs_core']['base_url'], app.config['system_config']['dirbs_core']['version'], tac))  # dirbs core tac api call
            if tac_response.status_code == 200:
                resp = tac_response.json()
                return resp
            return {"gsma": None}
        except Exception as error:
            raise error

    @staticmethod
    def get_reg(imei):
        """Return registration information fetched from DIRBS core."""

        try:
            reg_response = requests.get(
                '{base}/{version}/imei/{imei}/info'.format(base=app.config['system_config']['dirbs_core']['base_url'], version=app.config['system_config']['dirbs_core']['version'], imei=imei))
            if reg_response.status_code == 200:
                resp = reg_response.json()
                return resp
            return {}
        except Exception as error:
            raise error

    @staticmethod
    def serialize_gsma_data(tac_resp, reg_resp):
        """Return serialized device details."""

        response = dict()
        if tac_resp['gsma'] and reg_resp:
            response = CommonResources.serialize(response, tac_resp['gsma'], reg_resp)
            return response
        elif reg_resp and not tac_resp['gsma']:
            response = CommonResources.serialize_reg(response, reg_resp)
            return response
        elif tac_resp['gsma'] and not reg_resp:
            response = CommonResources.serialize_gsma(response, tac_resp['gsma'])
            return response
        else:
            return {"gsma": None}

    @staticmethod
    def subscribers(imei):
        """Return subscriber's details fetched from DIRBS core."""
        try:
            seen_with_url = requests.get('{base}/{version}/imei/{imei}/subscribers?limit=10&offset=0&order=DESC'.format(base=app.config['system_config']['dirbs_core']['base_url'], version=app.config['system_config']['dirbs_core']['version'], imei=imei))  # dirbs core imei api call
            seen_with_resp = seen_with_url.json()
            result_size = seen_with_resp.get('_keys').get('result_size')
            result = []
            if result_size>0:
                seen_with_url = requests.get('{base}/{version}/imei/{imei}/subscribers?offset=0&order=DESC&limit={result_size}'.format(base=app.config['system_config']['dirbs_core']['base_url'], version=app.config['system_config']['dirbs_core']['version'],imei=imei,result_size=result_size))  # dirbs core imei api call
                seen_with_resp = seen_with_url.json()
                data = seen_with_resp.get('subscribers')
                seen = set()
                result = [x for x in data if [(x['msisdn'], x['imsi']) not in seen, seen.add((x['msisdn'], x['imsi']))][0]]

            return {'subscribers': result}
        except Exception as error:
            raise error

    @staticmethod
    def serialize(response, gsma_resp, reg_resp):
        """Serialize device details from GSMA/registration data."""

        try:
            response['brand'] = reg_resp.get('brand_name') if reg_resp.get('brand_name') else gsma_resp.get('brand_name')
            response['model_name'] = reg_resp.get('model') if reg_resp.get('model') else gsma_resp.get('model_name')
            response['model_number'] = reg_resp.get('model_number') if reg_resp.get('model_number') else gsma_resp.get('marketing_name')
            response['device_type'] = reg_resp.get('device_type') if reg_resp.get('device_type') else gsma_resp.get('device_type')
            response['operating_system'] = reg_resp.get('operating_system') if reg_resp.get('operating_system') else gsma_resp.get('operating_system')
            response['radio_access_technology'] = reg_resp.get('radio_interface') if reg_resp.get('radio_interface') else gsma_resp.get('bands')
            return {'gsma': response}
        except Exception as error:
            raise error

    @staticmethod
    def serialize_reg(response, status_response):
        """Serialize device details from registration data."""

        try:
            response['brand'] = status_response.get('brand_name')
            response['model_name'] = status_response.get('model')
            response['model_number'] = status_response.get('model_number')
            response['device_type'] = status_response.get('device_type')
            response['operating_system'] = status_response.get('operating_system')
            response['radio_access_technology'] = status_response.get('radio_interface')
            return {'gsma': response}
        except Exception as error:
            raise error

    @staticmethod
    def serialize_gsma(response, status_response):
        """Serialize device details from GSMA data."""
        try:
            response['brand'] = status_response.get('brand_name')
            response['model_name'] = status_response.get('model_name')
            response['model_number'] = status_response.get('marketing_name')
            response['device_type'] = status_response.get('device_type')
            response['operating_system'] = status_response.get('operating_system')
            response['radio_access_technology'] = status_response.get('bands')
            return {'gsma': response}
        except Exception as error:
            raise error

    @staticmethod
    def serialize_cases(cases):
        """Serialize response."""
        case_list = []
        for row in cases:
            case_list.append(dict((col, val) for col, val in row.items()))
        cases = []
        for case in case_list:
            comment_list = []
            for comment in case.get('comments').split('|'):
                comment = json.loads(comment)
                if comment.get('id'):
                    comment_list.append({
                        'comment': comment.get('comment'),
                        'user_id': comment.get('user_id'),
                        'username': comment.get('username'),
                        'comment_date': comment.get('comment_date').split(' ', 1)[0]
                    })
            case_detail = {
                "get_blocked": case.get('get_blocked'),
                "creator": {
                    "user_id": case.get('user_id'),
                    "username": case.get('username')
                },
                "personal_details": {
                    "address": _(case.get('address')),
                    "gin": _(case.get('gin')),
                    "email": _(case.get('email')),
                    "number": _(case.get('alternate_number')),
                    "full_name": case.get('full_name'),
                    "father_name": case.get('father_name'),
                    "mother_name": case.get('mother_name'),
                    "district": case.get('district')
                },
                "tracking_id": case.get('tracking_id'),
                "comments": comment_list,
                "incident_details": {
                    "incident_date": case.get('date_of_incident'),
                    "incident_nature": _(case.get('incident_type'))
                },
                "created_at": case.get('created_at').strftime("%Y-%m-%d %H:%M:%S"),
                "device_details": {
                    "description": case.get('physical_description'),
                    "model_name": case.get('model_name'),
                    "imeis": case.get('imeis').replace(' ','').split(','),
                    "msisdns": case.get('msisdns').replace(' ','').split(','),
                    "brand": case.get('brand')
                },
                "status": _(case.get('status')),
                "updated_at": case.get('updated_at').strftime("%Y-%m-%d %H:%M:%S"),
                "source": "LSDS"
            }
            cases.append(case_detail)
        return cases

    @staticmethod
    def get_pending_cases():
        trigger = 'SET ROLE case_user; COMMIT;'
        db.session.execute(trigger)
        sql = "select c.*, cid.date_of_incident, cid.nature_of_incident, cpd.full_name, cpd.address, cpd.alternate_number, cpd.email, cpd.gin, cpd.father_name, cpd.mother_name, cpd.district, cpd.landline_number, dd.brand, dd.model_name, dd.physical_description, s.description as status, ni.name as incident_type, string_agg(distinct(di.imei::text), ', '::text) as imeis, string_agg(distinct(msisdn::text), ', '::text) as msisdns, string_agg(distinct(json_build_object('comment',cc.comments, 'comment_date',cc.comment_date, 'user_id',cc.user_id, 'username',cc.username, 'id',cc.id)::text), '| '::text) as comments from public.case as c left join case_comments as cc on cc.case_id=c.id, case_incident_details as cid, case_personal_details as cpd, device_details as dd, device_imei as di, device_msisdn as dm, public.status as s, public.nature_of_incident as ni where c.case_status=" + str(
            3) + " and cid.case_id=c.id and cpd.case_id=c.id and dd.case_id=c.id and di.device_id=dd.id and dm.device_id=dd.id  and s.id=c.case_status and ni.id=cid.nature_of_incident group by c.id, cid.date_of_incident, cid.nature_of_incident, cpd.full_name, cpd.alternate_number, cpd.address, cpd.email, cpd.gin,cpd.father_name, cpd.mother_name, cpd.district, cpd.landline_number, dd.brand, dd.model_name, dd.physical_description, s.description, ni.name order by c.updated_at desc"
        cases = db.session.execute(sql)
        cases = CommonResources.serialize_cases(cases)
        return cases

    @staticmethod
    def get_seen_with(cases):
        success_list = []
        failed_list = []
        for case in cases:
            if case['get_blocked']:
                for imei in case['device_details']['imeis']:
                    subscribers = CommonResources.subscribers(imei)
                    msisdn = [subs['msisdn'] for subs in subscribers['subscribers']]
                    if msisdn:
                        if (set(case['device_details']['msisdns']) & set(msisdn)):
                            result = db.session.query(Case).filter_by(tracking_id=case['tracking_id']).first()
                            result.case_status = 2
                            db.session.commit()
                            cases.remove(case)
                            success_list.append(imei)
                        else:
                            failed_list.append({"imei": imei, "status": "Data does not match, User has been notified"})
                    else:
                        failed_list.append({"imei": imei, "status": "IMEI couldn't be seen on network, User has been notified"})
            else:
                failed_list.append({"imei": case['device_details']['imeis'], "status": "IMEI cannot be blocked, Get Blocked is False. User has been notified"})
        return cases, success_list, failed_list

    @staticmethod
    def notify_users(cases):
        failed_to_notify = []
        if cases:
            for case in cases:
                response = requests.get('{base}?username={username}&password={password}&to={to}&text={text}&from={from_no}'.
                             format(base=app.config['system_config']['SMSC']['BaseUrl'],
                                    username=app.config['system_config']['SMSC']['Username'],
                                    to=case['personal_details']['number'],
                                    text=app.config['system_config']['SMSC']['Text'],
                                    password=app.config['system_config']['SMSC']['Password'],
                                    from_no=app.config['system_config']['SMSC']['From']))
                if response.status_code != 202:
                    failed_to_notify.append({"imei": case['device_details']['imeis'], "status": "User could not been notified because "+response.text})
            return failed_to_notify
        else:
            return cases
