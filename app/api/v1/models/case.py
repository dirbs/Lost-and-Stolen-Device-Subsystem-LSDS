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

# noinspection PyProtectedMember
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy import or_, and_
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
from ..assets.response import CODES


class Case(db.Model):
    """Case database model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100))
    username = db.Column(db.String(1000))
    case_status = db.Column(db.Integer, db.ForeignKey('status.id'))
    tracking_id = db.Column(db.String(64))  # Generate unique case tracking id
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(),
                           onupdate=db.func.now())

    case_incident_details = db.relationship("CaseIncidentDetails", backref="case", passive_deletes=True, lazy=True)
    case_personal_details = db.relationship("CasePersonalDetails", backref="case", passive_deletes=True, lazy=True)
    device_details = db.relationship("DeviceDetails", backref="case", passive_deletes=True, lazy=True)
    case_comments = db.relationship("CaseComments", backref="case", passive_deletes=True, lazy=True)

    def __init__(self, args, case_status=3):
        """Constructor."""
        self.user_id = args.get("loggedin_user").get("user_id")
        self.username = args.get("loggedin_user").get("username")
        self.case_status = case_status

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
                flag = db.session.query(DeviceImei).join(DeviceImei.devicedetails).join(DeviceDetails.case).\
                    filter(and_(or_(Case.case_status == 3, Case.case_status == 2), DeviceImei.imei == imei)).first()
                if flag:
                    return {'flag': flag, 'imei': imei}
            return {'flag': None, 'imei': None}
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def create(cls, args):
        """Insert data into database."""
        try:
            flag = Case.find_data(args['device_details']['imeis'])
            if flag.get('flag') is not None:
                return {"code": CODES.get('CONFLICT'), "data": flag.get('imei')}
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
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def update(cls, args, tracking_id):
        """Update personal details by tracking id."""
        try:
            case = cls.query.filter_by(tracking_id=tracking_id).first()
            if case:
                if case.case_status == 3:

                    personal_details = args.get("personal_details")
                    status_args = args.get('status_args')

                    if any(item is not None for item in [personal_details.get('email'), personal_details.get('dob'),
                                                         personal_details.get('address'), personal_details.get('gin'),
                                                         personal_details.get('number')]):

                        CasePersonalDetails.update(personal_details, case.id)

                        CaseComments.add(status_args.get('case_comment'), case.id, status_args.get('user_id'),
                                         status_args.get('username'))

                        Case.update_case(tracking_id)

                        db.session.commit()
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
    def update_status(cls, args, tracking_id):
        """Update status."""
        try:
            case = cls.query.filter_by(tracking_id=tracking_id).first()
            if case:
                if (case.case_status == 2 and args.get('case_status') != 3) or (case.case_status == 3):
                    if case.case_status != args.get('case_status'):
                        case.case_status = args.get('case_status')
                        CaseComments.add(args.get('case_comment'), case.id, args.get('user_id'), args.get('username'))
                        db.session.commit()
                        return case.tracking_id
                    else:
                        return CODES.get('CONFLICT')
                else:
                    return CODES.get('NOT_ACCEPTABLE')
            else:
                return None
        except Exception:
            db.session.rollback()
            raise Exception
        finally:
            db.session.close()
