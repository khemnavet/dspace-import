## DSpace Importer

The application is used to batch add items to a collection in [DSpace](https://dspace.lyrasis.org/). The metadata for the items are entered into an Excel file. 

The application is a desktop GUI application built using [Python 3](https://www.python.org/), using [Qt for Python](https://doc.qt.io/qtforpython-6/) for the UI components. It uses the DSpace REST API to add the items to the collection. It uses the DSpace 7 REST API (it has been tested with version 7.6)

### Installation

The application requires [Python 3](https://www.python.org/). It has been tested with Python 3.11 and 3.12. The recommended way to install the application is to use a virtual machine. 

Steps:

1. Install Python 3.12

2. [Download](https://github.com/khemnavet/dspace-import/archive/refs/heads/master.zip) the application and extract the  files. 
3. Open a Terminal or Command Prompt and navigate to the directory the application files were extracted to.
4. Create the virtual environment. The following command creates a virtual environment called `env` in the application directory:  
    ```bash
    python -m venv env
    ```
    The following steps assumes the virtual environment is called `env`.
5. Activate the virtual environment. Activating the virtual environment varies by operating system:  
    Windows:
    ```bash
    .\env\Scripts\activate
    ```
    Mac/Linux:
    ```bash
    source env/Scripts/activate
    ```
6. Install the required dependencies.  
    ```bash
    ./env/Scripts/pip install -r requirements.txt
    ```
7. Application configuration.  
The configuration values are stored in the file `config.toml`. The configuration keys and values present in the file are:  

    | Key | Description |
    | --- | --- |
    | `locale` | The language the UI components are displayed in. Currently `en` is supported. | 
    | `wizardWidth` | The width of the GUI window. | 
    | `wizardHeight` | The height of the GUI window. | 
    | `dspaceRestURL` | The URL of the DSpace REST server. | 
    | `metadataNotRemoveUpdate` | A comma delimited list of metadata fields not to be changed or removed when an item is updated by the application. The following are set `dc.identifier.uri, dc.description.provenance, dc.date.available, dc.date.accessioned` |
    | `provenance.enabled` | A flag to indicate if to add provenance metadata when items are uploaded or updated. The key is set to `true` to enable or `false` for the application not to add the provenance metadata field. |
    | `provenance.metadata-field` | The metadata field that would be used to store the provenance information. This field is added to the metadata submitted to DSpace if `provenance.enabled` is set to `true`.|
    | `provenance.add` | The value of the provenance metadata field when items are added. |
    | `provenance.update` | The value of the provenance metadata field when items are uodated. |
    
    The following place holders can be used within the `provenance.add` and `provenance.update` strings:  

     - {u} - This is replaced by the email address of the user logged on to the application.
     - {t} - This is replaced by the current timestamp (UTC).

    Edit the values to match the environment.
8. Start the application.  
    The application is started using the command:
    ```bash
    ./env/Scripts/python main.py
    ```
    The application will attempt to connect to the DSpace REST URL and if successful a login screen is displayed. The login is a DSpace login.


