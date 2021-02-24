* Project license has been updated to remove the requirement for acknowledgement
---

![Image of DIRBS Logo](https://avatars0.githubusercontent.com/u/42587891?s=100&v=4)

# Lost & Stolen Device Subsystem (LSDS)
## License
Copyright (c) 2018-2021 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
* The origin of this software must not be misrepresented; you must not claim that you wrote the original software.
* Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
* This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


## Documentation
[LSDS-API-Installation-Guide-1.0.0](https://github.com/dirbs/Documentation/blob/master/Lost-and-Stolen-Device-Subsystem/LSDS-API-Installation-Guide-1.0.0.pdf)<br />
[LSDS-SPA-Installation-Guide-1.0.0.pdf](https://github.com/dirbs/Documentation/blob/master/Lost-and-Stolen-Device-Subsystem/LSDS-SPA-Installation-Guide-1.0.0.pdf) <br />
[LSDS-User-Guide-1.0.0.pdf](https://github.com/dirbs/Documentation/blob/master/Lost-and-Stolen-Device-Subsystem/LSDS-User-Guide-1.0.0.pdf)<br />

## Frontend Application Repo
https://github.com/dirbs/Lost-and-Stolen-Device-Subsystem-Frontend

## Directory structure

This repository contains code for **LSDS** part of the **DIRBS**. It contains

* ``app/`` -- The LSDS core server app, to be used as LSDS Web Server including database models, apis and resources
* ``etc/`` -- Config files etc to be reside here
* ``mock/`` -- Sample data files etc which are used in app to be reside here
* ``tests/`` -- Unit test scripts and Data

###Prerequisites
In order to run a development environment, [Python 3.0+](https://www.python.org/download/releases/3.0/) and 
[Postgresql10](https://www.postgresql.org/about/news/1786/) we assume that these are installed.

We also assume that this repo is cloned from Github onto the local computer, it is assumed that 
all commands mentioned in this guide are run from root directory of the project and inside
```virtual environment```

On Windows, we assume that a Bash like shell is available (i.e Bash under Cygwin), with GNU make installed.

### Starting a dev environment
The easiest and quickest way to get started is to use local-only environment (i.e everything runs locally, including
Postgresql Server). To setup the local environment, follow the section below:

### Setting up local dev environment
For setting up a local dev environment we assume that the ```prerequisites``` are met already. To setup a local 
environment:
* Create database using Postgresql (Name and credentials should be same as in [config](tests/testdata/config_test.ini))
* Create virtual environment using **virtualenv** and activate it:
```bash
pip3 install virtualenv 
virtualenv venv
source venv/bin/activate
```
Make sure the virtual environment is made using python3

* Create /lists folder in / directory

* Replace sample configuration in config.ini to similar configurations in (tests/testdata/config_test.ini)

* Run Database migrations using:

```bash
make install-db
```

This will automatically create and migrate database schemas and requirements.

* Compile multi language encoded files
```bash
pybabel compile -d app/translations
```

* Start LSDS development server using:

```bash
make start-dev
```

This will start a flask development environment for LSDS.

* To run tests create another user other than root user.
* To run unit tests, run:

```bash
make test
```

* To lint the code using pylint, simply run:

```bash
make lint
```

### Other useful commands

* To install a fresh database:

```bash
make install-db
```

* To Upgrade already installed database:

```bash
make upgrade-db
```

* To generate delta stolen list for DIRBS Core:

```bash
make gen-delta-list
```

* To generate stolen full list for DIRBS Core:

```bash
make gen-full-list
```

* To run unit tests:

```bash
make test
```

* To run code linting:

```bash
make lint
```
