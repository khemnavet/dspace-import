��    *      l  ;   �      �     �     �  	   �      �     �     �          1     G     e     �     �     �     �     �     �        #   )     M     d      }     �  '   �     �     �     	     #     7     H     b  +   ~  #   �  (   �  &   �          8     V     l       "   �  "   �  {  �     a	     d	     h	  
   z	  	   �	  �   �	      �
  
   �
     �
  
   �
  5   �
     �
           0     E     ^  "   j  7   �  �  �     k     z     �  *   �  (   �  
   �     �  :        B     H     Q  U   c     �  ]   �  1   6  �   h     '  `   6     �     �  2   �  '   �                                "   $   (      %                                                                                  #       )             '   *              
   !       	         &                No Yes app_title collection_page_collection_label collection_page_community_label collection_page_instructions collection_page_subtitle collection_page_title excel_page_file_select_button excel_page_import_file_label excel_page_instructions excel_page_sheet_label excel_page_subtitle excel_page_title file_name_match_begins_with file_name_match_exact file_page_file_name_column_label file_page_file_name_extension_label file_page_instructions file_page_item_dir_label file_page_item_dir_select_button file_page_match_file_name_label file_page_remove_existing_for_duplicate file_page_subtitle file_page_title login_page_password_label login_page_subtitle login_page_title login_page_username_label mapping_page_column_heading mapping_page_column_schema_mapping_required mapping_page_duplicate_column_label mapping_page_duplicate_column_not_mapped mapping_page_duplicate_column_required mapping_page_instructions mapping_page_metadata_heading mapping_page_subtitle mapping_page_title mapping_page_title_column_label mapping_page_title_column_required mapping_page_update_existing_label Project-Id-Version: dspace_importer
PO-Revision-Date: 2023-10-30 16:10-0400
Last-Translator: 
Language-Team: 
Language: en
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
X-Generator: Poedit 3.4.1
X-Poedit-Basepath: ../../..
X-Poedit-SearchPath-0: main.py
X-Poedit-SearchPath-1: wizardpages.py
 No Yes UWISpace Importer Collection Community Navigate to the collection to import the data to by starting from the top communities. 
The collections in a community are shown in the collection dropdown. 

To go to the parent community, select the "Back" option under the community name. The collection to import data to Collection Browse Excel File The first row of the file must have the column names. Select the sheet to import Select the Excel file to import. Excel File to Import Begins with column value Exact Match Column with file name for the item Extension of the item files (if not in Excel worksheet) The directory where the files are stored is chosen using "Item Directory". Subdirectories can be included in the file name column of the Excel file. For example, dir1/file1.pdf will cause the application to look in the dir1 subdirectory for file1.pdf. If this is left blank, no files will be uploaded with the items. The Excel file can have rows with the file name column blank. In this case, the item metadata alone will be imported.

The "How to match item file names?" radio button indicates how the application will search for file names. If the "Exact match" option is chosen, the file name as it is entered in the Excel file is used. This will upload a single file per item. The "Begins with column value" option means that the value entered in the file name column of the Excel file is used to search for files with names starting with that value. The "Extension of the item files" textbox is required in this case. This option can be used to upload more than one file for an item. For example, if the file name column in the Excel file has item_ and the file extension is .pdf, the application will match files item_1.pdf, item_2.pdf, item_three.pdf, and upload them with the item. Item Directory Browse How to match item file names? Remove existing files for duplicate items? Select the directory with the item files Item Files Password Enter your email address and password to logon to UWISpace Login Username Excel Column Name Please select the metadata field to be used for at least one column of the Excel file Column to check for duplicates The column selected in "Column to check for duplicates" has to be mapped to a metadata field. The "Column to check for duplicates" is required. When selecting the metadata field, select the schema from the first combo box, then the metadata field from the second.

Columns that are not mapped to a metadata field will not be imported. Metadata Field Select the metadata field the data in the Excel column will be added to when importing the item. Metadata Mapping Column with title of the item The column with the title of the item is required. Update the metadata for existing items? 