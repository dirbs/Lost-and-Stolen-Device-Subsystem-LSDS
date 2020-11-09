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

import json
import magic
import pandas as pd
from flask_restful import request

from flask_babel import _
from ..assets.response import MIME_TYPES, CODES, MESSAGES
from ..assets.error_handlers import custom_response
from ..models.summary import Summary
from ..schema.case import BulkInsertSchema
from ..schema.validations import *
from ..helpers.tasks import CeleryTasks
from ..helpers.bulk_helpers import BulkCommonResources

from flask import Response, send_from_directory
from flask_apispec import use_kwargs, MethodResource, doc


class BlockCases(MethodResource):
    """Flak resource for case insertion."""

    @doc(description='Block/Unblock cases', tags=['bulk'])
    @use_kwargs(BulkInsertSchema().fields_dict, location='form')
    def post(self, **args):
        """Insert case details."""
        try:
            args['file'] = request.files.get('file')
            file = args.get('file')
            filepath = BulkCommonResources.save_file(file)
            filename = file.filename
            mimetype = magic.from_file(filepath, mime=True)
            if mimetype in app.config['system_config']['allowed_file_types'][
                'AllowedTypes'] and '.' in filename and filename.rsplit('.', 1)[1].lower() in \
                    app.config['system_config']['allowed_file_types']['AllowedExt']:  # validate file type
                bulk_file = pd.read_csv(filepath, index_col=False, dtype=str).astype(str)
                if 'alternate_number' in bulk_file.columns:
                    response = []
                    if args.get('action') == "block":
                        response = (CeleryTasks.bulk_block.s(list(bulk_file.T.to_dict().values())) |
                                    CeleryTasks.log_results.s(input="file")).apply_async()
                    if args.get('action') == "unblock":
                        response = (CeleryTasks.bulk_unblock.s(list(bulk_file.T.to_dict().values())) |
                                    CeleryTasks.log_results.s(input="file")).apply_async()
                    summary_data = {
                        "tracking_id": response.parent.id,
                        "status": response.state,
                        "input": "file"
                    }
                    Summary.create(summary_data)
                    data = {
                        "message": _("You can track your request using this id"),
                        "task_id": response.parent.id,
                        "state": response.state
                    }
                    return Response(json.dumps(data), status=CODES.get('OK'), mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                else:
                    return custom_response(_("Alternate Number column missing"), CODES.get('BAD_REQUEST'),
                                           MIME_TYPES.get('JSON'))
            else:
                return custom_response(_("System only accepts tsv/csv files."), CODES.get('BAD_REQUEST'), MIME_TYPES.get('JSON'))
        except Exception as e:
            app.logger.exception(e)
            data = {'message': _('Bulk process failed')}
            response = Response(json.dumps(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            return response


class DownloadFile(MethodResource):
    """Flask resource for downloading report."""

    @doc(description="Download IMEIs report", tags=['bulk'])
    def post(self, filename):
        """Sends downloadable report."""
        try:
            # returns file when user wants to download non compliance report
            return send_from_directory(directory=app.config['system_config']['UPLOADS']['report_dir'], filename=filename)
        except Exception as e:
            app.logger.info("Error occurred while downloading non compliant report.")
            app.logger.exception(e)
            return custom_response(_("Compliant report not found."), CODES.get('OK'), MIME_TYPES.get('JSON'))
