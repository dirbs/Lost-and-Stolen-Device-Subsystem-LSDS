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

from app import db


class DeviceMsisdn(db.Model):
    """Database model for device MSISDN."""
    id = db.Column(db.Integer, primary_key=True)
    msisdn = db.Column(db.String(15))
    device_id = db.Column(db.Integer, db.ForeignKey('device_details.id', ondelete='CASCADE'))

    def __init__(self, device_id, msisdn):
        """Constructor."""
        self.device_id = device_id
        self.msisdn = msisdn

    def __repr__(self):
        return '%r' % self.id

    @property
    def serialize(self):
        """Serialize."""
        return self.msisdn

    @staticmethod
    def get(record_id):
        """Get data by id."""
        try:
            if record_id:
                msisdn = DeviceMsisdn.query.filter_by(id=record_id).first()
                return msisdn.serialize
            return []
        except Exception:
            raise Exception

    @classmethod
    def add(cls, device_id, msisdns):
        """Insert data."""
        try:
            for msisdn in msisdns:
                device_msisdn = cls(device_id, msisdn)
                db.session.add(device_msisdn)
        except Exception:
            db.session.rollback()
            raise Exception

