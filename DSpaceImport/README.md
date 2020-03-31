## DSpace Importer

The application is used to batch add items to a collection in DSpace. The metadata for the items are entered into an Excel file.

The usage instructions can be found in the [user manual](UserManual.md).

#### Installation (Windows)

The application requires [Python 3](https://www.python.org/). It has been tested with Python 3.7. The recommended way to install the application is to use a virtual environment.
The virtual environment is created from the command line. First change directory to the directory to contain the application files. 
Execute the following command to create a virtual environment called `dspaceImporter`:

`py -3 -m venv dspaceImporter`

A directory called `dspaceImporter` will be created. 
Create a directory called `dspaceImporter` within this to store the application files. 
The application files are

- `config.ini`
- `DataObjects.py`
- `DSpaceImport.py`
- `dspacerequests.py`
- `requirements.txt`

The environment has to be started using the command

`dspaceImporter\Scripts\activate.bat`

Change directory to where the application files are:

`cd dspaceImporter\dspaceImporter`

Install the required libraries:

`..\Scripts\python.exe pip install -r requirements.txt`

The application can be started using

`..\Scripts\python.exe DSpaceImport.py`

The environment can be shutdown using the command

`..\Scripts\deactivate.bat`

#### Using the application

To launch the application, the environment has to be first started. The following commands can be used from the directory containing the `dspaceImporter` directory.

`dspaceImporter\Scripts\activate.bat`
`cd dspaceImporter\dspaceImporter`
`..\Scripts\python.exe DSpaceImport.py`

The logon screen should be shown. These commands can be added to a batch file and stored in the directory
containing the `dspaceImporter\dspaceImporter` directory.

When finished using the application, the environment can be shutdown using 

`..\Scripts\deactivate.bat`

