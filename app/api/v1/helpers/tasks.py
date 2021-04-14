"""
Copyright (c) 2018-2020 Qualcomm Technologies, Inc.
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

import os
from time import sleep, time
from celery.signals import task_postrun

from app import celery, app, db
from celery.result import AsyncResult
from ..helpers.bulk_helpers import BulkCommonResources
from ..models.summary import Summary


class CeleryTasks:

    @staticmethod
    @celery.task()
    def log_results(response, input):
        try:
            status = AsyncResult(response['task_id'])
            while not status.ready():
                sleep(5)
            if response['response']:
                Summary.update(input=input, status=status.state, response=response)
            else:
                Summary.update(input=input, status='FAILURE', response=response)
            return True
        except Exception:
            Summary.update(input=input, status='FAILURE', response=response)
            return True

    @staticmethod
    @celery.task()
    def bulk_block(file):
        clean_data, invalid_data = BulkCommonResources.clean_data(file)
        failed_list, success_list = BulkCommonResources.block(clean_data)
        report = BulkCommonResources.generate_report(failed_list, invalid_data, "bulk_block_failed")
        return {
            "response": {
                "success": len(success_list),
                "failed": len(failed_list+invalid_data),
                "report_name": report
            },
            "task_id": celery.current_task.request.id
        }

    @staticmethod
    @celery.task()
    def bulk_unblock(file):
        clean_data, invalid_data = BulkCommonResources.clean_data(file)
        failed_list, success_list = BulkCommonResources.unblock(clean_data)
        report = BulkCommonResources.generate_report(failed_list, invalid_data, "bulk_unblock_failed")
        return {
            "response": {
                "success": len(success_list),
                "failed": len(failed_list+invalid_data),
                "report_name": report
            },
            "task_id": celery.current_task.request.id
        }

    @staticmethod
    @celery.task
    def delete_files():
        """Deletes reports from system after a specific time."""
        try:
            current_time = time()  # get current time
            for f in os.listdir(app.config['system_config']['UPLOADS']['report_dir']):  # list files in specific directory
                creation_time = os.path.getctime(
                    os.path.join(app.config['system_config']['UPLOADS']['report_dir'], f))  # get creation time of each file
                if current_time - creation_time >= app.config['system_config']['global']['ReportDeletionTime']*3600:  # compare creation time is greater than 24 hrs
                    os.remove(os.path.join(app.config['system_config']['UPLOADS']['report_dir'],
                                           f))  # if yes, delete file from directory
        except Exception as e:
            app.logger.exception(e)
            raise e

    @task_postrun.connect
    def close_session(*args, **kwargs):
        # Flask SQLAlchemy will automatically create new sessions for you from
        # a scoped session factory, given that we are maintaining the same app
        # context, this ensures tasks have a fresh session (e.g. session errors
        # won't propagate across tasks)
        db.session.remove()

