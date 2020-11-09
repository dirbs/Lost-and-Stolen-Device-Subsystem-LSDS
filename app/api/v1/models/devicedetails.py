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

from app import db
# noinspection PyUnresolvedReferences
from ..models.deviceimei import DeviceImei
# noinspection PyUnresolvedReferences
from ..models.devicemsisdn import DeviceMsisdn


class DeviceDetails(db.Model):
    """Database model for device details."""
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id', ondelete='CASCADE'))
    brand = db.Column(db.String(1000))
    model_name = db.Column(db.String(1000))
    physical_description = db.Column(db.String(1000))
    device_imeis = db.relationship("DeviceImei", backref="devicedetails", passive_deletes=True, lazy=True)
    device_msisdns = db.relationship("DeviceMsisdn", backref="devicedetails", passive_deletes=True, lazy=True)

    def __init__(self, case_id, brand, model_name, description):
        """Constructor."""
        self.case_id = case_id
        self.brand = brand
        self.model_name = model_name
        self.physical_description = description

    @property
    def serialize(self):
        """Serialize data."""
        return {
            'brand': self.brand,
            'model_name': self.model_name,
            'description': self.physical_description,
            'imeis': [imei.serialize for imei in self.device_imeis],
            'msisdns': [msisdn.serialize for msisdn in self.device_msisdns]
        }

    @classmethod
    def add(cls, args, case_id):
        """Insert details."""
        try:
            device = cls(case_id, args.get("brand").strip(), args.get("model_name").strip(),
                         args.get("description").strip())

            db.session.add(device)
            db.session.flush()

            DeviceImei.add(device.id, args.get("imeis"))

            DeviceMsisdn.add(device.id, args.get("msisdns"))

            return device.__repr__()
        except Exception:
            db.session.rollback()
            raise Exception
