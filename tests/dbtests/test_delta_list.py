"""
 Copyright (c) 2018 Qualcomm Technologies, Inc.

 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
   following disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or
   promote products derived from this software without specific prior written permission.

 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED
 BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
 SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE,
 DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from app.api.v1.models.delta_list import DeltaList


def test_delta_list_insert(session):
    """Test delta list insertion"""
    res = session.execute("SELECT * FROM public.delta_list")
    records = []
    for r in res:
        records.append(dict((col, val) for col, val in r.items()))
    assert len(records) == 28

    DeltaList.insert("12345678901234", 3)

    res = session.execute("SELECT * FROM public.delta_list")
    records = []
    for r in res:
        records.append(dict((col, val) for col, val in r.items()))
    assert len(records) == 29


def test_delta_list_update(session):
    """Test delta list update"""
    res = session.execute("SELECT * FROM public.delta_list")
    records = []
    for r in res:
        records.append(dict((col, val) for col, val in r.items()))
    assert len(records) == 29

    DeltaList.update("12345678901234", 2)

    res = session.execute("SELECT * FROM public.delta_list where imei='12345678901234'")
    records = []
    for r in res:
        records.append(dict((col, val) for col, val in r.items()))

    assert records[0]['status'] == 2
