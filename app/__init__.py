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

import sys
import yaml
import configparser

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_babel import Babel

from celery import Celery
from celery.schedules import crontab

app = Flask(__name__)
CORS(app)

try:
    config = configparser.ConfigParser()
    config.read("config.ini")
    app.config['dev_config'] = config

    global_config = yaml.safe_load(open("etc/config.yml"))
    app.config['system_config'] = global_config

    CeleryConf = app.config['system_config']['celery']
    db_params = {
        'Host': app.config['system_config']['Database']['Host'],
        'Port': app.config['system_config']['Database']['Port'],
        'Database': app.config['system_config']['Database']['Database'],
        'User': app.config['system_config']['Database']['UserName'],
        'Password': app.config['system_config']['Database']['Password']
    }

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://%s:%s@%s:%s/%s' % \
                                            (db_params['User'], db_params['Password'], db_params['Host'],
                                             db_params['Port'], db_params['Database'])

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['pool_size'] = int(app.config['system_config']['Database']['pool_size'])
    app.config['pool_recycle'] = int(app.config['system_config']['Database']['pool_recycle'])
    app.config['max_overflow'] = int(app.config['system_config']['Database']['overflow_size'])
    app.config['pool_timeout'] = int(app.config['system_config']['Database']['pool_timeout'])

    db = SQLAlchemy()
    db.init_app(app)

    # celery configurations
    app.config['CELERY_BROKER_URL'] = CeleryConf['RabbitmqUrl']
    app.config['result_backend'] = 'db+' + app.config['SQLALCHEMY_DATABASE_URI']  # CeleryConf['RabbitmqBackend']
    app.config['broker_pool_limit'] = None

    # register tasks
    app.config['imports'] = CeleryConf['CeleryTasks']

    # initialize celery
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

    # schedule task
    celery.conf.beat_schedule = {
        'delete-every-hour': {
            'task': 'app.api.v1.helpers.tasks.CeleryTasks.delete_files',
            'schedule': crontab(minute=0, hour='*/1')
        },
    }

    # update configurations
    celery.conf.update(app.config)
    TaskBase = celery.Task


    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)


    celery.Task = ContextTask

    app.config['BABEL_DEFAULT_LOCALE'] = global_config['language_support']['default']
    app.config['LANGUAGES'] = global_config['language_support']['languages']
    babel = Babel(app)


    @babel.localeselector
    def get_locale():
        return app.config['BABEL_DEFAULT_LOCALE']

    from app.api.v1.routes import *

except Exception as e:
    app.logger.critical('exception encountered while parsing the config file, see details below')
    app.logger.exception(e)
    sys.exit(1)
