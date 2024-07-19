# User Manual

The application is used to batch add items to a collection in DSpace. The application can also update the metadata for existing items in a collection. The metadata for the items are read from an Excel file. The application uses DSpace's REST API and can be run from a client machine.

## The Excel File

The data can be uploaded from a single worksheet at a time. The worksheet has one item per row. The first row has the column headings. The column heading names can be repeated. The column heading names are mapped to metadata elements in DSpace. 

The Excel worksheet must have a column for the title of the item. This is required when items are being added or the metadata of existing items updated. 

If existing items are to be updated, the Excel worksheet has a column containing the UUID of the item to be updated.

### Files

Files can be optionally uploaded with the metadata for an item. The file name is entered in a column of the Excel worksheet. There are three ways to specify the file(s) to be added to the item:

1. The file name and extension of a single file. An optional description can be added after the file name. A `|` character is added between the file name and description.
2. If multiple files are to be added to the item and they are of different types, they entered in the Excel worksheet as follows:  
The file and the optional file description are entered as 1. above. A semicolon (`;`) is added between the files.  
Examples are: `file1.ext|file1 description;file2.ext;file3.ext|file3 description` or `file1.ext|file1 description;file2.ext`.
3. If multiple files are to be added to the item and they are of the same type, option 2. above can be used, or they can be entered in the Excel worksheet as follows:  
The files are named such there is a common part unique to the item the files are for. For example, the file names can be `item1_front.pdf`, `item1_back.pdf`. The common part entered in the Excel worksheet. File descriptions are not supported using this method.

The directory containing the files is entered in the application. If the files are in sub-directories of that directory, the sub-directory is prepended to the file name in the Excel worksheet with a `/` added between them. For example, if `dir1/file1.ext` is in the Excel worksheet, the application will look for a file names `file1.ext` in a sub-directory `dir1` under the directory entered in the application.

The primary bitstream can be identified in the Excel worksheet. This is optional. DSpace uses the thumbnail of the primary bitstream of the ORIGINAL bundle as the main thumbnail for the item.  
If the primary bitstream is needed, a column is added to the Excel worksheet for the primary bitstream. The file name (and extension) is added for the item. It can be identified for some items and left blank for others. The application will not set the primary bitstream flag for the items with blank values.

An example of an Excel worksheet to add items is:


| Filename | Primary | Title | Subject | Subject | 
| ---      | ---     | ---   | ---     | ---     | 
| file1.ext | file1.ext | Title One | Subject one | Subject two | 
| file2.ext &#124; Description | | Title Two | Subject three | Subject two | 
| file3.ext &#124; Description; file4.ext | file4.ext | Title Three | Subject five | Subject six | 
| file5.ext &#124; Description; file6.ext &#124; Description | file6.ext | Title Four | Subject four | Subject five | 

## Application Configuration

The configuration values are stored in the file `config.toml`. The configuration keys and values present in the file are:  

| Key | Description |
| --- | --- |
| `locale` | The language the UI components are displayed in. Currently `en` is supported. | 
| `wizardWidth` | The width of the GUI window. | 
| `wizardHeight` | The height of the GUI window. | 
| `dspaceRestURL` | The URL of the DSpace REST server. | 
| `metadataNotRemoveUpdate` | A comma delimited list of metadata fields not to be changed or removed when an item is updated by the application. The following are set `dc.identifier.uri, dc.description.provenance, dc.date.available, dc.date.accessioned` |
| `provenance.enabled` | A flag to indicate if to add provenance metadata when items are uploaded or updated. The key is set to `true` to enable. |
| `provenance.metadata-field` | The metadata field that would be used to store the provenance information |
| `provenance.add` | The value of the provenance metadata field when items are added. The following placeholders can be used: <ul><li>{u} - This is replaced by the email address of the user logged on to the application.</li><li>{t} - This is replaced by the current timestamp (UTC).</li></ul>  |

## Using the Application

The import is done by a DSpace user. The user will need at least submit access to the collection the items are uploaded to. The login form (figure 1) is displayed when the application is launched.

<figure>
<img src="images/importer-login.png" alt="Logon Screen">
<figcaption><b>Figure 1</b>: Logon Screen</figcaption>
</figure>

The `Next >` button is activated when a email address and password is entered. The application logs on to DSpace when `Next >` is clicked. If the username and password are invalid, an error message (figure 2) is displayed.

<figure>
<img src="images/importer-invalid-login.png" alt="Logon Error Message">
<figcaption><b>Figure 2</b>: Logon Error Message</figcaption>
</figure>

After successful logon, the form to select the DSpace collection is shown (figure 3).

<figure>
<img src="images/importer-collection-select.png" alt="Collection select">
<figcaption><b>Figure 3</b>: The collection to import to</figcaption>
</figure>

The `Community` select contains the communities in DSpace. It first displays the top communities. When a community is selected, the `Community` select is redrawn to display the sub-communities of that community. Any collections in that community are displayed in the `Collection` select.  
The selected community is displayed in the `Community` select. The next option is called `Back`. This option is used to display the communities previously shown. 

The `Next >` button is activated when a collection is selected. When clicked, the form to select the Excel file is displayed (figure 4).

<figure>
<img src="images/importer-excel-select.png" alt="Excel select">
<figcaption><b>Figure 4</b>: Excel file to import</figcaption>
</figure>

The Excel file is chosen from the file system using the `Browse` button. When the Excel file is chosen, the names of the worksheets in the file are shown in the `Select the sheet to import` select. The `Next >` button is activated when the worksheet is chosen. When clicked, the form to map the columns in the Excel worksheet to DSpace metadata fields is displayed (figure 5).

