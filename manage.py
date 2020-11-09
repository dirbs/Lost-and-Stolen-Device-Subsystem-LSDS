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

"""This modules manages database migration commands."""

import sys
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# noinspection PyUnresolvedReferences
from app.api.v1.models import *
from app.api.v1.models.eshelper import ElasticSearchResource
from app.api.v1.seeders.seeder import Seeds
from app import app, db
from scripts.stolen_list import GenList
from scripts.data_migration import DataMigration

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
seed = Seeds(db)


@manager.command
def Seed():
    """Seeds cases status and incident types."""
    try:
        status = seed.seed_status()
        incident_types = seed.seed_incident_types()
        print(status, incident_types)
    except Exception as e:
        app.logger.exception(e)
        sys.exit(1)

@manager.command
def DbTrigger():
    """Create event triggers to generate case identifier."""

    sql = "CREATE OR REPLACE FUNCTION public.tracking_id_function() RETURNS trigger LANGUAGE plpgsql AS $function$ DECLARE _serial char(8); _i int; _chars char(62) = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'; done bool; BEGIN IF NEW IS NULL THEN RAISE EXCEPTION 'id cannot be null'; END IF; done = false; WHILE NOT done LOOP _serial = ''; FOR _i in 1 .. 8 LOOP _serial = _serial || substr(_chars, int4(floor(random() * length(_chars))) + 1, 1); END LOOP; done = NOT exists(SELECT 1 FROM public.case WHERE tracking_id=_serial); END LOOP; UPDATE public.case SET tracking_id=_serial WHERE id=NEW.id; RETURN new; END; $function$"
    db.engine.execute(sql)
    # trigger = "create trigger insert_tracking_id_trigger after insert on public.case referencing new table as public.case for each row execute procedure tracking_id_function()"
    check = "select 1 from pg_trigger where tgname='insert_tracking_id_trigger'"
    if db.engine.execute(check).fetchone() is None:
        trigger = 'create trigger insert_tracking_id_trigger after insert on public.case referencing new table as "case" for each row execute procedure tracking_id_function()'
        db.engine.execute(trigger)
        print("Function created successfully")
    else:
        drop_trigger = "drop trigger insert_tracking_id_trigger on public.case CASCADE;"
        db.engine.execute(drop_trigger)
        trigger = 'create trigger insert_tracking_id_trigger after insert on public.case referencing new table as "case" for each row execute procedure tracking_id_function()'
        db.engine.execute(trigger)
        print("Function created successfully")


@manager.command
def CreateRoles():
    """Create db roles and grant relevant privileges."""
    roles = ['case_user', 'search_user', 'delta_list_user']
    for role in roles:
        check = "SELECT 1 FROM pg_roles WHERE rolname='%s';" % (role)
        if db.engine.execute(check).fetchone() is None:
            trigger = "CREATE ROLE %s;" % (role)
            db.engine.execute(trigger)
            print("created successfully")
        else:
            drop_privileges = "DROP OWNED BY %s;" % role
            db.engine.execute(drop_privileges)
            drop_role = "DROP ROLE %s;" % role
            db.engine.execute(drop_role)
            trigger = "CREATE ROLE %s;" % role
            db.engine.execute(trigger)
            print("Already existed but created successfully")
    grant_access_case_user = "GRANT SELECT, UPDATE, INSERT ON public.case, public.case_comments, " \
                             "public.case_incident_details, public.case_personal_details, public.device_details, " \
                             "public.device_imei, public.device_msisdn, public.nature_of_incident, public.status, " \
                             "public.summary, public.bulk TO case_user"
    db.engine.execute(grant_access_case_user)
    grant_squences = "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO case_user"
    db.engine.execute(grant_squences)
    print("Permission granted to role case_user")
    # grant_access_search_user = "GRANT SELECT ON public.search TO search_user"
    # db.engine.execute(grant_access_search_user)
    # print("Permission granted to role search_user")
    grant_access_delta_list_user = "GRANT SELECT ON public.case, public.device_details, public.device_imei, " \
                                   "public.bulk TO delta_list_user"
    db.engine.execute(grant_access_delta_list_user)
    print("Permission granted to role delta_list_user for case model")
    grant_access_delta_list_user = "GRANT SELECT, INSERT, UPDATE ON public.delta_list TO delta_list_user"
    db.engine.execute(grant_access_delta_list_user)
    grant_squences = "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO delta_list_user"
    db.engine.execute(grant_squences)
    print("Permission granted to role delta_list_user for delta list model")

    print("Roles created successfully")


@manager.command
def genlist():
    return GenList.create_list()


@manager.command
def GenFullList():
    return GenList.get_full_list()

@manager.command
def CreateIndex():
    app.logger.info(ElasticSearchResource.create_index())


@manager.command
def MigrateDataBulk():
    app.logger.info(DataMigration.bulk_insert())

@manager.command
def MigrateData():
    app.logger.info(DataMigration.single_insert())


if __name__ == '__main__':
    manager.run()
