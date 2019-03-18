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
"""This modules manages database migration commands."""

import sys
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# noinspection PyUnresolvedReferences
from app.api.v1.models import *
from app.api.v1.seeders.seeder import Seeds
from app import app, db
from scripts.stolen_list import GenList

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
        return status, incident_types
    except Exception as e:
        app.logger.exception(e)
        sys.exit(1)


@manager.command
def CreateView():
    """Create view for search module."""

    # Find if view exist or not & return none if not found
    sql = "select to_regclass('search')"
    data = db.engine.execute(sql)

    try:
        for row in data:
            if row[0] is None:
                sql = "create view search as SELECT public.case.get_blocked, public.case.id,public.case.tracking_id,status.description AS status, public.case.updated_at,public.case.user_id,public.case.username,nature_of_incident.name AS incident, case_incident_details.date_of_incident,case_personal_details. alternate_number,case_personal_details.dob,case_personal_details.gin,case_personal_details.email,case_personal_details.address,case_personal_details.full_name,device_details.brand,device_details.model_name as model,device_details.physical_description as description,string_agg(distinct(device_imei.imei::text), ', '::text) AS imeis, string_agg(distinct(device_msisdn.msisdn::text), ', '::text) AS msisdns FROM case_incident_details JOIN nature_of_incident ON case_incident_details.nature_of_incident = nature_of_incident.id JOIN public.case ON case_incident_details.case_id = public.case.id JOIN status ON public.case.case_status = status.id JOIN case_personal_details ON case_personal_details.case_id = public.case.id JOIN device_details ON device_details.case_id = public.case.id JOIN device_imei ON device_imei.device_id = device_details.id JOIN device_msisdn ON device_msisdn.device_id = device_details.id GROUP BY public.case.id, nature_of_incident.name, status.description, public.case.updated_at, case_incident_details.date_of_incident, case_personal_details.alternate_number, case_personal_details.dob, case_personal_details.gin, case_personal_details.email, case_personal_details.address, case_personal_details.full_name, public.case.tracking_id, device_details.brand, device_details.model_name,device_details.physical_description,public.case.user_id,public.case.username, public.case.get_blocked;"
                db.engine.execute(sql)
                return "View created successfully"
            else:
                drop_view = "drop view search"
                db.engine.execute(drop_view)
                sql = "create view search as SELECT public.case.get_blocked, public.case.id,public.case.tracking_id,status.description AS status, public.case.updated_at,public.case.user_id,public.case.username,nature_of_incident.name AS incident, case_incident_details.date_of_incident,case_personal_details. alternate_number,case_personal_details.dob,case_personal_details.gin,case_personal_details.email,case_personal_details.address,case_personal_details.full_name,device_details.brand,device_details.model_name as model,device_details.physical_description as description,string_agg(distinct(device_imei.imei::text), ', '::text) AS imeis, string_agg(distinct(device_msisdn.msisdn::text), ', '::text) AS msisdns FROM case_incident_details JOIN nature_of_incident ON case_incident_details.nature_of_incident = nature_of_incident.id JOIN public.case ON case_incident_details.case_id = public.case.id JOIN status ON public.case.case_status = status.id JOIN case_personal_details ON case_personal_details.case_id = public.case.id JOIN device_details ON device_details.case_id = public.case.id JOIN device_imei ON device_imei.device_id = device_details.id JOIN device_msisdn ON device_msisdn.device_id = device_details.id GROUP BY public.case.id, nature_of_incident.name, status.description, public.case.updated_at, case_incident_details.date_of_incident, case_personal_details.alternate_number, case_personal_details.dob, case_personal_details.gin, case_personal_details.email, case_personal_details.address, case_personal_details.full_name, public.case.tracking_id, device_details.brand, device_details.model_name,device_details.physical_description,public.case.user_id,public.case.username, public.case.get_blocked;"
                db.engine.execute(sql)
                return "View created successfullyy"
    except Exception as e:
        return app.logger.exception(e)


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
        return "Function created successfully"
    else:
        drop_trigger = "drop trigger insert_tracking_id_trigger on public.case CASCADE;"
        db.engine.execute(drop_trigger)
        trigger = 'create trigger insert_tracking_id_trigger after insert on public.case referencing new table as "case" for each row execute procedure tracking_id_function()'
        db.engine.execute(trigger)
        return "Function created successfully"


@manager.command
def genlist():
    return GenList.create_list()


if __name__ == '__main__':
    manager.run()
