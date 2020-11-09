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

# noinspection PyProtectedMember
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy import or_, and_
from datetime import datetime
from app import db
# noinspection PyUnresolvedReferences
from ..models.caseincidentdetails import CaseIncidentDetails
# noinspection PyUnresolvedReferences
from ..models.casepersonaldetails import CasePersonalDetails
# noinspection PyUnresolvedReferences
from ..models.devicedetails import DeviceDetails
# noinspection PyUnresolvedReferences
from ..models.deviceimei import DeviceImei
# noinspection PyUnresolvedReferences
from ..models.casecomments import CaseComments
from ..models.bulk import Bulk
from ..assets.response import CODES

from .eshelper import ElasticSearchResource


class Case(db.Model):
    """Case database model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100))
    username = db.Column(db.String(1000))
    user_role = db.Column(db.String(20))
    case_status = db.Column(db.Integer, db.ForeignKey('status.id'))
    tracking_id = db.Column(db.String(64))  # Generate unique case tracking id
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    get_blocked = db.Column(db.Boolean)
    case_incident_details = db.relationship("CaseIncidentDetails", backref="case", passive_deletes=True, lazy=True)
    case_personal_details = db.relationship("CasePersonalDetails", backref="case", passive_deletes=True, lazy=True)
    device_details = db.relationship("DeviceDetails", backref="case", passive_deletes=True, lazy=True)
    case_comments = db.relationship("CaseComments", backref="case", passive_deletes=True, lazy=True)

    def __init__(self, args, case_status=3):
        """Constructor."""
        self.user_id = args.get("loggedin_user").get("user_id")
        self.username = args.get("loggedin_user").get("username")
        self.user_role = args.get("loggedin_user").get("role")
        self.case_status = case_status
        self.get_blocked = args.get("case_details").get("get_blocked")

    @property
    def serialize(self):
        """Serialize data."""
        return {
            "creator": {
                "user_id": self.user_id,
                "username": self.username
            },
            "tracking_id": self.tracking_id,
            "status": self.Status.serialize,
            "get_blocked": self.get_blocked,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else 'N/A',
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else 'N/A',
            "incident_details": self.__get_obj(self.case_incident_details).serialize,
            "personal_details": self.__get_obj(self.case_personal_details).serialize,
            "device_details": self.__get_obj(self.device_details).serialize,
            "comments": sorted([{"user_id": comment.user_id, "comment": comment.comments,
                                 "comment_date": comment.comment_date.strftime("%Y-%m-%d %H:%M:%S"),
                                 "username": comment.username} for comment in self.case_comments],
                               key=lambda k: k['comment_date'], reverse=True)
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

    @staticmethod
    def get_case(tracking_id):
        """Retrieve data by tracking id."""
        try:
            if tracking_id:
                trigger = 'SET ROLE case_user; COMMIT;'
                db.session.execute(trigger)
                case = Case.query.filter_by(tracking_id=tracking_id).first()
                if case:
                    return case.serialize
            return {}
        except Exception:
            raise Exception

    @staticmethod
    def find_data(imeis):
        """Check if data already exists."""
        try:
            for imei in imeis:
                flag = db.session.execute("select device_imei.imei, c.created_at, c.tracking_id from device_imei join public.device_details as dd on device_imei.device_id = dd.id join public.case as c on dd.case_id = c.id where device_imei.imei='"+imei+"' and (c.case_status = 3 or c.case_status = 2) limit 1;")
                for row in flag:
                    return dict((col, val) for col, val in row.items())
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def create(cls, args):
        """Insert data into database."""
        try:
            trigger = 'SET ROLE case_user; COMMIT;'
            db.session.execute(trigger)
            flag = Case.find_data(args['device_details']['imeis'])
            bulk_flag = Bulk.find_bulk_data(args['device_details']['imeis'])
            if flag:
                return {"code": CODES.get('CONFLICT'), "data": flag, "reason": "LSDS"}
            elif bulk_flag:
                return {"code": CODES.get('CONFLICT'), "data": bulk_flag, "reason": "Bulk"}
            else:
                case = cls(args)
                db.session.add(case)
                db.session.flush()

                personal_details = args.get("personal_details")
                if any(item is not None for item in [personal_details.get('email'), personal_details.get('dob'),
                                                     personal_details.get('address'), personal_details.get('gin'),
                                                     personal_details.get('number')]):

                    case_incident_args = args.get("incident_details")
                    device_details = args.get("device_details")

                    DeviceDetails.add(device_details, case.id)
                    CaseIncidentDetails.add(case_incident_args, case.id)
                    CasePersonalDetails.add(personal_details, case.id)

                    db.session.commit()
                    case = Case.query.filter_by(tracking_id=case.tracking_id).first()
                    ElasticSearchResource.insert_doc(case.serialize, "LSDS")
                    return {"code": CODES.get('OK'), "data": case.tracking_id}
                else:
                    return {"code": CODES.get('BAD_REQUEST')}

        except Exception:
            db.session.rollback()
            raise Exception
        finally:
            db.session.close()

    @classmethod
    def update_case(cls, tracking_id):
        """Update DB column "updated_at" after case update."""
        try:
            case = cls.query.filter_by(tracking_id=tracking_id).first()
            case.updated_at = db.func.now()
            db.session.commit()
            ElasticSearchResource.update_doc(case.tracking_id, {"doc" : {"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def update_case_info(cls, args, case_id):
        """Update get blocked column in case model."""
        try:
            case = cls.query.filter_by(id=case_id).first()
            case.get_blocked = args["get_blocked"] if args.get("get_blocked") is not None else case.get_blocked
            db.session.add(case)
            db.session.commit()
            ElasticSearchResource.update_doc(case.tracking_id, {"doc": {"get_blocked": args.get('get_blocked')}})
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def update(cls, args, tracking_id):
        """Update personal details by tracking id."""
        try:
            trigger = 'SET ROLE case_user; COMMIT;'
            db.session.execute(trigger)
            case = cls.query.filter_by(tracking_id=tracking_id).first()
            if case:
                if case.case_status == 3:

                    personal_details = args.get("personal_details")
                    # status_args = args.get('status_args')

                    if any(item is not None for item in [personal_details.get('email'),
                                                         personal_details.get('address'), personal_details.get('gin'),
                                                         personal_details.get('number')]):

                        CasePersonalDetails.update(personal_details, case.id)

                        # CaseComments.add(status_args.get('case_comment'), case.id, status_args.get('user_id'),
                        #                status_args.get('username'))

                        Case.update_case(tracking_id)

                        db.session.commit()
                        ElasticSearchResource.update_doc(case.tracking_id, {"doc": {"personal_details": personal_details}})
                        return case.tracking_id
                    else:
                        return CODES.get('BAD_REQUEST')
                else:
                    return CODES.get('NOT_ACCEPTABLE')
            else:
                return None
        except Exception:
            db.session.rollback()
            raise Exception
        finally:
            db.session.close()

    @classmethod
    def update_blocked_info(cls, args, tracking_id):
        """Update case get blocked information by tracking id."""
        try:
            trigger = 'SET ROLE case_user; COMMIT;'
            db.session.execute(trigger)
            case = cls.query.filter_by(tracking_id=tracking_id).first()
            if case:
                if case.case_status == 3:
                    case_details = args.get("case_details")
                    status_args = args.get('status_args')

                    Case.update_case_info(case_details, case.id)

                    CaseComments.add(status_args.get('case_comment'), case.id, status_args.get('user_id'),
                                     status_args.get('username'))

                    Case.update_case(tracking_id)

                    db.session.commit()
                    ElasticSearchResource.insert_comments(comment=status_args.get('case_comment'),
                                                          userid=status_args.get('user_id'),
                                                          username=status_args.get('username'),
                                                          tracking_id=case.tracking_id)
                    return case.tracking_id
                else:
                    return CODES.get('NOT_ACCEPTABLE')
            else:
                return None
        except Exception:
            db.session.rollback()
            raise Exception
        finally:
            db.session.close()

    @classmethod
    def update_status(cls, args, tracking_id):
        """Update status."""
        try:
            if args.get('role') == "admin":
                trigger = 'SET ROLE case_user; COMMIT;'
                db.session.execute(trigger)
                case = cls.query.filter_by(tracking_id=tracking_id).first()
                if case:
                    if case.get_blocked:
                        if (case.case_status == 2 and args.get('case_status') != 3) or (case.case_status == 3):
                            if case.case_status != args.get('case_status'):
                                case.case_status = args.get('case_status')
                                CaseComments.add(args.get('case_comment'), case.id, args.get('user_id'), args.get('username'))
                                db.session.commit()
                                ElasticSearchResource.update_doc(case.tracking_id, {"doc": {"status": "Recovered"}})
                                ElasticSearchResource.insert_comments(comment=args.get('case_comment'),
                                                                      userid=args.get('user_id'),
                                                                      username=args.get('username'),
                                                                      tracking_id=case.tracking_id)
                                return case.tracking_id
                            else:
                                return CODES.get('CONFLICT')
                        else:
                            return CODES.get('NOT_ACCEPTABLE')
                    else:
                        if case.case_status == 3 and args.get('case_status') != 2:
                            if case.case_status != args.get('case_status'):
                                case.case_status = args.get('case_status')
                                CaseComments.add(args.get('case_comment'), case.id, args.get('user_id'), args.get('username'))
                                db.session.commit()
                                ElasticSearchResource.update_doc(case.tracking_id, {"doc": {
                                    "status": "Recovered" if args.get('case_status') == 1 else "Blocked" if args.get(
                                        'case_status') == 2 else "Pending"}})
                                ElasticSearchResource.insert_comments(comment=args.get('case_comment'),
                                                                      userid=args.get('user_id'),
                                                                      username=args.get('username'),
                                                                      tracking_id=case.tracking_id)
                                return case.tracking_id
                            else:
                                return CODES.get('CONFLICT')
                        else:
                            return CODES.get('NOT_ACCEPTABLE')
                else:
                    return None
            else:
                return CODES.get('UNAUTHORIZED')
        except Exception:
            db.session.rollback()
            raise Exception
        finally:
            db.session.close()
