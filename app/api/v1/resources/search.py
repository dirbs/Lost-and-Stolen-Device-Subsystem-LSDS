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

from app import app, db
import json
from datetime import datetime, timedelta
from flask import Response
from flask_babel import _
from flask_apispec import use_kwargs, MethodResource, doc
from ..assets.response import MIME_TYPES, CODES
from ..assets.pagination import Pagination
from ..schema.case import SearchSchema, SearchResponseSchema, SearchResponseSchemaES
from ..models.eshelper import ElasticSearchResource


class Search(MethodResource):
    """Flask resource for search module."""

    @staticmethod
    def get_results(kwargs, data):
        """paginate retrieved search data."""
        cases = []
        for row in data:
            cases.append(dict((col, val) for col, val in row.items()))
        if cases:  # if reported cases are resent in database
            paginated_data = Pagination.get_paginated_list(cases, '/search', start=kwargs.get('start', 1),
                                                           limit=kwargs.get('limit', 3))

            paginated_data['cases'] = SearchResponseSchema(many=True).dump(paginated_data['cases']).data
            response = Response(json.dumps(paginated_data, default=str), status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        else:  # if database has no reported cases
            data = {
                "start": kwargs.get('start', 1),
                "previous": "",
                "next": "",
                "cases": cases,
                "count": 0,
                "limit": kwargs.get('limit', 2)
            }
            response = Response(json.dumps(data, default=str), status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        return response

    @staticmethod
    def build_query(sql, x, request_data, param=''):
        """Build query from search criteria given by user to search from database search view."""

        if x == "updated_at" or x == "date_of_incident":
            date = request_data.get(x).split(",")
            sql = sql + " {col} between '{min}' AND '{max}' {param}".format(
                col=x,
                min=date[0],
                max=datetime.strptime(date[1], "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59),
                param=param
            )
        elif x == "imeis" or x == "msisdns":
            record_len = len(request_data.get(x))
            if record_len == 1:
                sql = sql + " {col} like '%%{val}%%' {param}".format(
                    col=x,
                    val=request_data.get(x)[0],
                    param=param
                )
            if record_len > 1:
                sql = sql + "("
                for val in request_data.get(x):
                    record_len = record_len - 1
                    if record_len == 0:
                        sql = sql + " {col} like '%%{val}%%') {param}".format(
                            col=x,
                            val=val,
                            param=param
                        )
                    else:
                        sql = sql + " {col} like '%%{val}%%' OR".format(
                            col=x,
                            val=val
                        )
        else:
            sql = sql + " {col} ilike '%%{val}%%' {param}".format(
                col=x,
                val=str(request_data.get(x).replace("'", "''")),
                param=param
            )
        return sql

    @doc(description='Search cases', tags=['Search'])
    @use_kwargs(SearchSchema().fields_dict, locations=['json'])
    def post(self, **kwargs):
        """Return search results."""
        trigger = 'SET ROLE search_user; COMMIT;'
        db.session.execute(trigger)
        request_data = kwargs.get("search_args")
        count = len(request_data)
        sql = "select * from search"
        try:
            if count == 0:  # return all cases if no search criteria
                data = db.engine.execute(sql+" order by updated_at desc")
                response = Search.get_results(kwargs, data)
                return response
            else:  # if there is a search criteria
                sql = "select * from search where"
                for x in request_data:
                    count = count - 1
                    if count == 0:  # if there is single parameter in search query
                        sql = Search.build_query(sql, x, request_data)
                    else:  # if there are multiple parameter in search query
                        sql = Search.build_query(sql, x, request_data, 'AND')
                sql = sql + ' order by updated_at desc'
                data = db.engine.execute(sql)
                response = Search.get_results(kwargs, data)
                return response
        except Exception as e:
            app.logger.exception(e)
            data = {
                        "start": kwargs.get('start', 1),
                        "previous": "",
                        "next": "",
                        "cases": [],
                        "count": 0,
                        "limit": kwargs.get('limit', 2),
                        "message": _("service unavailable")
                    }
            response = Response(json.dumps(data), status=CODES.get("SERVICE_UNAVAILABLE"),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            return response
        finally:
            db.session.close()


class ES_Search(MethodResource):

    @doc(description='Search cases', tags=['Search'])
    @use_kwargs(SearchSchema().fields_dict, location='json')
    def post(self, **kwargs):
        """Return search results."""
        request_data = kwargs.get("search_args")
        limit = kwargs.get('limit')
        start = kwargs.get('start')
        try:
            result = ElasticSearchResource.search_doc(request_data, limit, start)
            response = ES_Search.get_es_results(kwargs, result)
            return response
        except Exception as e:
            app.logger.exception(e)
            data = {
                "start": kwargs.get('start', 1),
                "previous": "",
                "next": "",
                "cases": [],
                "count": 0,
                "limit": kwargs.get('limit', 2),
                "message": _("service unavailable")
            }
            response = Response(json.dumps(data), status=CODES.get("SERVICE_UNAVAILABLE"),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            return response


    @staticmethod
    def get_es_results(kwargs, data):
        """paginate retrieved search data."""
        if data['hits']['hits']:  # if reported cases are resent in database
            paginated_data = Pagination.get_paginated_list(data['hits']['hits'], '/search', start=kwargs.get('start', 1),
                                                           limit=kwargs.get('limit', 3))
            paginated_data['cases'] = SearchResponseSchemaES(many=True).dump(paginated_data['cases']).data
            response = Response(json.dumps(paginated_data, default=str), status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        else:  # if database has no reported cases
            data = {
                "start": kwargs.get('start', 1),
                "previous": "",
                "next": "",
                "cases": [],
                "count": 0,
                "limit": kwargs.get('limit', 2)
            }
            response = Response(json.dumps(data, default=str), status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        return response
