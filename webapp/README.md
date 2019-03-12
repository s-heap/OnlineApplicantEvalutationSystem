# Installation Guide
## Requirements
The system can be tested on any computer which supports the technologies mentioned in this document. The ones which require installation are python2, python3, MongoDB and Flask. Included in the code is a file called ’setup’, this will install MongoDB, Flask and all of the python libraries required.
## Setup File
The ’setup’ file in the app directory is for installing the python requirements, MongoDB, python virtual environment and Flask on OSX. This file assumes that the system is already installed with python2, python3 and the installers pip/pip3 and brew. The setup file can be run by typing:
> ./setup
## Python Requirements
Lists all of the python libraries required for the backend are stored within the python requirements files; these have been generated using:
> pip(3) freeze pythonrequirements.txt
 
Run using the command:
>pip(3)install−rpythonrequirements.txt
## Running The System:
The submitted code contains a file called ’run’, this file contains all of the commands required to run the system locally. These commands include those required to run Flask and the Mongo Database.

## Inserting test data
To setup the database please make use of these two scripts. Please Note: Execute them from within the DB directory
> python3 insertDummyData.py 

> python3 applyToJobs.py