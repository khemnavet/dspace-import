��    8      �  O   �      �     �     �  	   �      �          +     H     a     w     �     �     �     �     �          "      8  #   Y     }     �      �     �  '   �          )     9     S     m     �     �     �     �  +   �  -        9  #   S  &   w     �  $   �  1   �     	     )	     <	  "   \	  "   	     �	  #   �	     �	     �	     
  "   7
     Z
     m
     �
     �
  {  �
     8     ;     ?  
   Q  	   \  �   f      W  
   x     �  
   �  5   �     �      �               5  "   A  7   d  �  �     B     Q     X      v  (   �  
   �     �     �     �  :   �     1     7     @  U   R  /   �  �  �      �  1   �       3   ,  2   `  `   �     �       2   #  '   V     ~     �  $   �     �  /   �  2   	     <     D  '   Q     y        0         1       %   $   2   8              6          (                              !           )   "                 3   	   +           
   #          4       -      ,                    .       *       '                 7   5                              /         &          No Yes app_title collection_page_collection_label collection_page_community_label collection_page_instructions collection_page_subtitle collection_page_title excel_page_file_select_button excel_page_import_file_label excel_page_instructions excel_page_sheet_label excel_page_subtitle excel_page_title file_name_match_begins_with file_name_match_exact file_page_file_name_column_label file_page_file_name_extension_label file_page_instructions file_page_item_dir_label file_page_item_dir_select_button file_page_match_file_name_label file_page_remove_existing_for_duplicate file_page_subtitle file_page_title import_results_page_title login_page_password_label login_page_service_url login_page_subtitle login_page_title login_page_username_label mapping_page_column_heading mapping_page_column_schema_mapping_required mapping_page_existing_metadata_to_match_label mapping_page_instructions mapping_page_item_uuid_column_label mapping_page_item_uuid_column_required mapping_page_metadata_heading mapping_page_primary_bitstream_label mapping_page_remove_extra_existing_metadata_label mapping_page_subtitle mapping_page_title mapping_page_title_column_label mapping_page_title_column_required mapping_page_update_existing_label summary_page_file_sheet summary_page_import_into_collection summary_page_item_directory summary_page_item_uuid_column summary_page_metadata_to_match summary_page_remove_extra_metadata summary_page_title summary_page_title_column summary_page_update_existing summary_page_using_file Project-Id-Version: dspace_importer
PO-Revision-Date: 2024-01-26 14:02-0400
Last-Translator: 
Language-Team: 
Language: en
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
X-Generator: Poedit 3.4.2
X-Poedit-Basepath: ../../..
X-Poedit-SearchPath-0: main.py
X-Poedit-SearchPath-1: wizardpages.py
 No Yes UWISpace Importer Collection Community Navigate to the collection to import the data to by starting from the top communities. 
The collections in a community are shown in the collection dropdown. 

To go to the parent community, select the "Back" option under the community name. The collection to import data to Collection Browse Excel File The first row of the file must have the column names. Select the sheet to import Select the Excel file to import. Excel File to Import Begins with column value Exact Match Column with file name for the item Extension of the item files (if not in Excel worksheet) The directory where the files are stored is chosen using "Item Directory". Subdirectories can be included in the file name column of the Excel file. For example, dir1/file1.pdf will cause the application to look in the dir1 subdirectory for file1.pdf. If this is left blank, no files will be uploaded with the items. The Excel file can have rows with the file name column blank. In this case, the item metadata alone will be imported.

The "How to match item file names?" radio button indicates how the application will search for file names. If the "Exact match" option is chosen, the file name as it is entered in the Excel file is used. This will upload a single file per item. The "Begins with column value" option means that the value entered in the file name column of the Excel file is used to search for files with names starting with that value. The "Extension of the item files" textbox is required in this case. This option can be used to upload more than one file for an item. For example, if the file name column in the Excel file has item_ and the file extension is .pdf, the application will match files item_1.pdf, item_2.pdf, item_three.pdf, and upload them with the item. Item Directory Browse How to match item file names? Remove files for existing items? Select the directory with the item files Item Files Import Results Password DSpace server url: Enter your email address and password to logon to UWISpace Login Username Excel Column Name Please select the metadata field to be used for at least one column of the Excel file Update metadata of item to match data in Excel? When selecting the metadata field, select the schema from the first combo box, then the metadata field from the second.

Columns that are not mapped to a metadata field will not be imported.

"Column with the UUID of the item" specifies the column containing the UUID of the item to be updated with the metadata contained in the row.

"Column with the file name for the primary bitstream" specifies the column with the file name to be used as the primary bit stream for the item. This is optional. Column with the UUID of the item The column with the UUID of the item is required. Metadata Field Column with the file name for the primary bitstream Remove metadata of item that is not in Excel file? Select the metadata field the data in the Excel column will be added to when importing the item. Metadata Mapping Column with title of the item The column with the title of the item is required. Update the metadata for existing items? Sheet  Importing items to collection Directory containing files for items Item UUID column Update metadata of item to match data in Excel? Remove metadata of item that is not in Excel file? Summary Title column Update the metadata for existing items? Excel file with items 