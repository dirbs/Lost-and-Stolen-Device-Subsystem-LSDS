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
from elasticsearch import Elasticsearch
from app import app
from datetime import datetime, timedelta

es = Elasticsearch([{'host': app.config['system_config']['ELASTIC_SEARCH']['Host'],
                   'port': app.config['system_config']['ELASTIC_SEARCH']['Port']}])


class ElasticSearchResource:

    @staticmethod
    def create_index():
        mapping = '''{
            "mappings": {
            "numeric_detection": false,
            "properties": {
              "updated_at": {
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss" 
              },
              "created_at": {
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss" 
              }
            }
            }
            }'''
        return es.indices.create(index=app.config['system_config']['Database']['Database'], body=mapping)

    @staticmethod
    def insert_doc(document, source):
        try:
            new_doc = {
                "device_details": document['device_details'],
                "incident_details": document['incident_details'],
                "get_blocked": document['get_blocked'],
                "updated_at": document['updated_at'],
                "created_at": document['created_at'],
                "personal_details": document['personal_details'],
                "tracking_id": document['tracking_id'],
                "creator": document['creator'],
                "status": document['status'],
                "comments": document['comments'],
                "source": source
            }
            es.index(index=app.config['system_config']['Database']['Database'], id=document['tracking_id'], body=new_doc)
            return None
        except Exception as e:
            raise e

    @staticmethod
    def insert_comments(comment, userid, username, tracking_id):
        doc = {
            "script" : {
                "source": "ctx._source.comments.add(params.comments)",
                "lang": "painless",
                "params" : {
                    "comments": {
                        "user_id": userid,
                        "username": username.strip(),
                        "comment": comment.strip(),
                        "created_at": datetime.now()
                    }
                }
            }
        }
        es.update(index=app.config['system_config']['Database']['Database'], id=tracking_id, doc_type="_doc", body=doc)
        return None

    @staticmethod
    def get_doc(tracking_id):
        res = es.get(index=app.config['system_config']['Database']['Database'], id=tracking_id)
        return res

    @staticmethod
    def update_doc(tracking_id, doc_to_update):
        es.update(index=app.config['system_config']['Database']['Database'], id=tracking_id, doc_type="_doc", body=doc_to_update)
        return None

    @staticmethod
    def search_doc(doc_to_search, limit, start):
        query = {"size": 10000, "query": {"bool": {"must": []}}}
        for field in doc_to_search:
            if field == "updated_at":
                date = doc_to_search.get(field).split(",")
                query['query']['bool']['must'].append({"range": {field: {"gte": date[0] + " 00:00:00",
                                                                         "lte": date[1] + " 23:59:59"}}})
            elif field == "date_of_incident":
                date = doc_to_search.get(field).split(",")
                query['query']['bool']['must'].append({"range": {"incident_details.incident_date": {"gte": date[0], "lte": date[1]}}})
            elif field == "imeis" or field == "msisdns":
                query['query']['bool']['must'].append({"terms": {"device_details."+field: doc_to_search[field]}})
            else:
                if field in ["father_name", "mother_name", "full_name", "address", "dob", "gin", "alternate_number",
                             "email", "landline_number", "district"]:
                    query['query']['bool']['must'].append({"match": {"personal_details."+field: doc_to_search[field]}})
                elif field in ["brand", "model_name", "description"]:
                    query['query']['bool']['must'].append({"match": {"device_details."+field: doc_to_search[field]}})
                elif field in ["incident_nature"]:
                    query['query']['bool']['must'].append({"match": {"incident_details."+field: doc_to_search[field]}})
                else:
                    query['query']['bool']['must'].append({"match": {field: doc_to_search[field]}})
        resp = es.search(index=app.config['system_config']['Database']['Database'], body=query)
        return resp