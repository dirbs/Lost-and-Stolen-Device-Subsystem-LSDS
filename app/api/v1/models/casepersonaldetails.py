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
from flask_babel import _


class CasePersonalDetails(db.Model):
    """Database model for personal details."""
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id', ondelete='CASCADE'))
    full_name = db.Column(db.String(1000))
    address = db.Column(db.Text, server_default='N/A')
    gin = db.Column(db.String(30), server_default='N/A')
    alternate_number = db.Column(db.String(30), server_default='N/A')
    email = db.Column(db.String(65), server_default='N/A')

    def __init__(self, args, case_id):
        """Constructor"""
        self.case_id = case_id
        self.full_name = args.get("full_name").strip()
        self.address = args.get("address").strip() if args.get("address") else args.get("address")
        self.gin = args.get("gin")
        self.alternate_number = args.get("number")
        self.email = args.get("email")


    @property
    def serialize(self):
        """Serialize data."""
        return {
            'full_name': _(self.full_name),
            'address': _(self.address),
            'gin': _(self.gin),
            'number': _(self.alternate_number),
            'email': _(self.email)
        }

    @classmethod
    def add(cls, args, case_id):
        """Insert details."""
        try:
            person = cls(args, case_id)
            db.session.add(person)
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def update(cls, args, case_id):
        """Update details."""
        try:
            person = cls.query.filter_by(case_id=case_id).first()
            person.full_name = args.get('full_name').strip()
            person.address = args.get("address").strip() if args.get("address") else args.get("address")
            person.gin = args.get('gin')
            person.alternate_number = args.get('number')
            person.email = args.get('email')
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception
