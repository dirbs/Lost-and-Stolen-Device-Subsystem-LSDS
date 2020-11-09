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

from app.api.v1.models import *


class Seeds:
    """Class for database seeding."""

    def __init__(self, db):
        """Constructor."""
        self.db = db

    def seed_status(self):
        """Seed case status."""
        try:
            objects = [status.Status(id=1, description='Recovered'),
                       status.Status(id=2, description='Blocked'),
                       status.Status(id=3, description='Pending')]
            sql = "select count(*) from status"
            data = self.db.engine.execute(sql).fetchone()
            if data[0] > 0:
                self.db.engine.execute("TRUNCATE table status RESTART IDENTITY CASCADE")
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Status seeding successful."
            else:
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Status seeding successful."
        except Exception as e:
            self.db.session.rollback()
            raise e
        finally:
            self.db.session.close()

    def seed_incident_types(self):
        """Seed case incident types."""
        try:
            objects = [natureofincident.NatureOfIncident(id=1, name='Stolen', description='Stolen Device'),
                       natureofincident.NatureOfIncident(id=2, name='Lost', description='Lost Device')]
            sql = "select count(*) from nature_of_incident"
            data = self.db.engine.execute(sql).fetchone()
            if data[0] > 0:
                self.db.engine.execute("TRUNCATE table nature_of_incident RESTART IDENTITY CASCADE")
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Nature of incident seeding successful."
            else:
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Nature of incident seeding successful."
        except Exception as e:
            self.db.session.rollback()
            raise e
        finally:
            self.db.session.close()
