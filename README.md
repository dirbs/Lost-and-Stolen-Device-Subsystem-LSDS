### Copyright (c) 2018 Qualcomm Technologies, Inc.

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

### Lost & Stolen Device Subsystem (LSDS)
Lost & Stolen Device Subsystem (LSDS) that is part of the Device Identification,
Registration and Blocking (DIRBS) system.


##### Directory structure

This repository contains code for **LSDS** part of the **DIRBS**. It contains

* ``app/`` -- The LSDS core server app, to be used as LSDS Web Server including database models, apis and resources
* ``etc/`` -- Config files etc to be reside here
* ``mock/`` -- Sample data files etc which are used in app to be reside here
* ``tests/`` -- Unit test scripts and Data

##### Prerequisites
In order to run a development environment, [Python 3.0+](https://www.python.org/download/releases/3.0/) and 
[Postgresql10](https://www.postgresql.org/about/news/1786/) we assume that these are installed.

We also assume that this repo is cloned from Github onto the local computer, it is assumed that 
all commands mentioned in this guide are run from root directory of the project and inside
```virtual environment```

On Windows, we assume that a Bash like shell is available (i.e Bash under Cygwin), with GNU make installed.

##### Starting a dev environment
The easiest and quickest way to get started is to use local-only environment (i.e everything runs locally, including
Postgresql Server). To setup the local environment, follow the section below:

##### Setting up local dev environment
For setting up a local dev environment we assume that the ```prerequisites``` are met already. To setup a local 
environment:
* Create database using Postgresql (Name and credentials should be same as in [config](tests/testdata/config.ini))
* Create virtual environment using **virtualenv** and activate it:
```bash
virtualenv venv
source venv/bin/activate
```

* Install the project requirements
```bash
$ pip install -r requirements.txt
```
* Replace sample configuration in config.ini to configurations in (tests/testdata/config.ini)

* Start LSDS development server using:
```bash
python run.py
```

* Create migration repository 	
```bash
$ python manage.py db init
```

* Generate initial migration	
```bash
$ python manage.py db migrate
```

* Apply migrations to the database
```bash
$ python manage.py db upgrade
```

* Create function and trigger in db
```bash
$ python manage.py DbTrigger 
```

* Create view in db for search
```bash
$ python manage.py CreateView
```

* Seed data in db
```bash
$ python manage.py Seed
```

**Note:** After making changes in the schema only run step 2 and 3.

* To run unit tests, run
```bash
$ pytest -v
```
