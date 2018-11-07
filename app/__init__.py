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
#                                                                                                                     #
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

import sys
import yaml
import configparser

import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

try:
    config = configparser.ConfigParser()
    config.read("config.ini")

    global_config = yaml.load(open("etc/config.yml"))

    db_params = {
        'Host': config['Database']['Host'],
        'Port': config['Database']['Port'],
        'Database': config['Database']['Database'],
        'User': config['Database']['UserName'],
        'Password': config['Database']['Password']
    }

    HOST = str(config['Server']['Host'])  # Host addr required as str
    PORT = int(config['Server']['Port'])  # Host port required as int
    CORE_BASE_URL = global_config['dirbs_core']['base_url']  # core api base url
    VERSION = global_config['dirbs_core']['version']  # core api version
    GLOBAL_CONF = global_config['global']  # load & export global configs
    UPLOADS = str(config['UPLOADS']['list_dir'])  # stolen list upload path
    APP_VERSION = global_config['system']['version']

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://%s:%s@%s:%s/%s' % \
                                            (db_params['User'], db_params['Password'], db_params['Host'],
                                             db_params['Port'], db_params['Database'])

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SQLALCHEMY_POOL_SIZE'] = int(config['Database']['pool_size'])
    app.config['SQLALCHEMY_POOL_RECYCLE'] = int(config['Database']['pool_recycle'])
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = int(config['Database']['overflow_size'])
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = int(config['Database']['pool_timeout'])

    db = SQLAlchemy()
    db.init_app(app)

    session = requests.Session()
    session.keep_alive = False
    retry = Retry(total=GLOBAL_CONF.get('retry'), backoff_factor=1, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    from app.api.v1.routes import *

except Exception as e:
    app.logger.critical('exception encountered while parsing the config file, see details below')
    app.logger.exception(e)
    sys.exit(1)
