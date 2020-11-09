"""
 SPDX-License-Identifier: BSD-4-Clause-Clear

 Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided with the distribution.
 * All advertising materials mentioning features or use of this software, or any deployment of this software, or
   documentation accompanying any distribution of this software, must display the trademark/logo as per the details
   provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
   products derived from this software without specific prior written permission.

 SPDX-License-Identifier: ZLIB-ACKNOWLEDGEMENT

 Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

 This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable
 for any damages arising from the use of this software.

 Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter
 it and redistribute it freely, subject to the following restrictions:

 * The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If
   you use this software in a product, an acknowledgment is required by displaying the trademark/logo as per the details
   provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
 * Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
 * This notice may not be removed or altered from any source distribution.

 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
 THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.                                                               #
"""

# noinspection PyProtectedMember
from sqlalchemy.orm.collections import InstrumentedList
from app import db
from ..assets.response import CODES
from .eshelper import ElasticSearchResource
from datetime import datetime


class Bulk(db.Model):
    """Case database model"""
    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(20))
    msisdn = db.Column(db.String(20))
    alternate_number = db.Column(db.String(20))
    status = db.Column(db.Integer, db.ForeignKey('status.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __init__(self, imei, msisdn, status, alternate_number):
        """Constructor."""
        self.imei = imei
        self.status = status
        self.msisdn = msisdn
        self.alternate_number = alternate_number

    @property
    def serialize(self):
        """Serialize data."""
        return {
            "imei": self.imei,
            "msisdn": self.msisdn,
            "alternate_number": self.alternate_number,
            "created_at": self.created_at,
            "status": self.status,
            "updated_at": self.updated_at,
            "tracking_id": self.id
            }

    # pass instrumented list object to get string value
    @staticmethod
    def __get_obj(instr_obj):
        """Return string value from instrumented list object."""
        try:
            if type(instr_obj) == InstrumentedList:
                return instr_obj[0]
            return None
        except Exception:
            raise Exception

    @classmethod
    def create(cls, imei, msisdn, status, alternate_number):
        """Insert data into database."""
        try:
            case = cls(imei, msisdn, status, alternate_number)
            db.session.add(case)
            db.session.commit()
            document = Bulk.get_case(imei)
            doc = {
                "device_details": {
                    "imeis": [document['imei']],
                    "msisdns": [document['msisdn']]
                },
                "incident_details": {},
                "get_blocked": True,
                "updated_at": document['updated_at'].strftime("%Y-%m-%d %H:%M:%S"),
                "created_at": document['created_at'].strftime("%Y-%m-%d %H:%M:%S"),
                "personal_details": {
                    "alternate_number": document['alternate_number']
                },
                "tracking_id": document['tracking_id'],
                "creator": {},
                "status": "Recovered" if document['status'] == 1 else "Blocked" if document['status'] == 2 else "Pending",
                "comments": {}
            }
            ElasticSearchResource.insert_doc(doc, "Bulk")
            return CODES.get('OK')
        except Exception:
            db.session.rollback()
            raise Exception
        finally:
            db.session.close()

    @staticmethod
    def get_case(imei):
        """Retrieve data by imei."""
        try:
            case = Bulk.query.filter_by(imei=imei).first()
            if case:
                return case.serialize
            return {}
        except Exception:
            raise Exception


    @classmethod
    def update_status(cls, imei):
        """Update status."""
        try:
            case = cls.query.filter_by(imei=imei).first()
            if case:
                if case.status == 2:
                    case.status = 1
                    case.updated_at = db.func.now()
                    db.session.commit()
                    ElasticSearchResource.update_doc(case.id, {"doc": {
                        "status": "Recovered" if case.status == 1 else "Blocked" if case.status == 2 else "Pending",
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})
                elif case.status == 1:
                    case.status = 2
                    case.updated_at = db.func.now()
                    db.session.commit()
                    ElasticSearchResource.update_doc(case.id, {"doc": {
                        "status": "Recovered" if case.status == 1 else "Blocked" if case.status == 2 else "Pending",
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})
                else:
                    return CODES.get('NOT_ACCEPTABLE')
        except Exception:
            db.session.rollback()
            raise Exception
        finally:
            db.session.close()

    @staticmethod
    def find_bulk_data(imeis):
        """Check if data already exists."""
        try:
            for imei in imeis:
                flag = Bulk.get_case(imei)
                if flag and flag.get('status') == 2:
                    return flag
            return {}
        except Exception:
            db.session.rollback()
            raise Exception

    @staticmethod
    def find_bulk(imeis):
        """Check if data already exists."""
        try:
            for imei in imeis:
                flag = Bulk.get_case(imei)
                if flag:
                    return flag
            return {}
        except Exception:
            db.session.rollback()
            raise Exception