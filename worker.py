import sys, traceback

from PySide6.QtCore import QObject, Signal

from config import ImporterConfig
from dataobjects import ImporterData, AuthData, Bundle, BundleType, Item
from excelfileservice import ExcelFileService
from itemservice import ItemService, ItemException
from bundleservice import BundleService, BundleException
from bitstreamservice import BitstreamService, BitstreamException
from fileservice import ItemFileService
from metadataservice import MetadataService


class ImportWorker(QObject):
    finished = Signal(str, name="finished")
    progress = Signal(str, name="progress")

    def __init__(self, shared_data: ImporterData, config: ImporterConfig, auth_data: AuthData) -> None:

        self.shared_data = shared_data
        self.excel_service = ExcelFileService()
        self.item_service = ItemService(config,auth_data)
        self.bundle_service = BundleService(config, auth_data)
        self.bitstream_service = BitstreamService(config, auth_data)
        self.file_service = ItemFileService()
        self.metadata_service = MetadataService(config, auth_data)
        self.exclude_metadata = config.exclude_metadata()
        super().__init__()

    def __remove_primary_bitstream(self, bundle: Bundle):
        if self.bundle_service.bundle_has_primary_bitstream(bundle):
            self.bundle_service.remove_primary_bitstream(bundle)
    
    def __remove_bundle_bitstreams(self, bundle):
        if bundle is not None:
            self.__remove_primary_bitstream(bundle)
            bitstreams = self.bundle_service.bundle_bitstreams(bundle)
            for bitstream in bitstreams:
                self.bitstream_service.remove_bitstream(bitstream)

    def run(self):
        for row_index, file_name, item_uuid, item_title in self.excel_service.file_itemuuiud_title(self.shared_data.file_name_column, self.shared_data.item_uuid_column, self.shared_data.title_column):
            print(f"processing row {row_index}, title {item_title}, item uuid {item_uuid}")
            try:
                if item_uuid is not None:
                    item = self.item_service.get_item(item_uuid)
                    if self.shared_data.remove_existing_files:
                        original, thumbnail = self.item_service.bundle(item, [BundleType.ORIGINAL, BundleType.THUMBNAIL])
                        self.__remove_bundle_bitstreams(original)
                        self.__remove_bundle_bitstreams(thumbnail)
                    else:
                        original = self.item_service.bundle(item, [BundleType.ORIGINAL])[0]
                    
                    if self.shared_data.update_existing:
                        item.metadata = self.metadata_service.item_metadata(self.excel_service.get_row(row_index), self.shared_data.column_mapping)
                        item.name = item_title
                        print(f"updating item {item_title}")
                        item.patch_operations = self.metadata_service.item_patch_operations(item, self.shared_data.remove_extra_metadata, self.shared_data.metadata_to_match, self.exclude_metadata)
                        self.item_service.update_item(item)
                else: 
                    print(f"adding item {item_title}")
                    item = self.item_service.create_item(Item(name=item_title, metadata=self.metadata_service.item_metadata_with_provenance(self.excel_service.get_row(row_index), self.shared_data.column_mapping)), self.shared_data.selected_collection)
                    original = None
                
                if len(self.shared_data.primary_bitstream_column) > 0:
                    primary_file = self.excel_service.primary_bitstream_value(row_index, self.shared_data.primary_bitstream_column)
                else:
                    primary_file = None

                if file_name is not None and len(self.shared_data.item_directory) > 0:
                    if original is None:
                        original = self.bundle_service.create_bundle(Bundle(bundle_type=BundleType.ORIGINAL), item)
                    # bitstreams
                    for file in self.file_service.item_files(file_name, self.shared_data.file_name_matching, self.shared_data.file_extension, self.shared_data.item_directory):
                        # file is a list of dict("file", "description")
                        bitstream = self.bitstream_service.create_bitstream(original, file["file"], self.metadata_service.file_metadata(file["file"].name, file["description"]))
                        if primary_file is not None and file["file"].name == primary_file+self.shared_data.file_extension:
                            self.__remove_primary_bitstream(original)
                            self.bundle_service.bundle_add_primary_bitstream(original, bitstream)
                self.progress.emit(f"Imported row {row_index} (title {item_title}) successfully.")

            except ItemException as err:
                traceback.print_exc(file=sys.stdout)
                self.progress.emit(f"Error processing row {row_index} (title {item_title}). (Item Exception) {err}")
            except BundleException as err1:
                traceback.print_exc(file=sys.stdout)
                self.progress.emit(f"Error processing bundles for row {row_index} (title {item_title}). (Bundle Exception) {err1}")
            except BitstreamException as err2:
                traceback.print_exc(file=sys.stdout)
                self.progress.emit(f"Error processing bitstreams for row {row_index} (title {item_title}). (Bitstream Exception) {err2}")
            except Exception as err3:
                traceback.print_exc(file=sys.stdout)
                self.progress.emit(f"Error processing row {row_index} (title {item_title}). (Other Exception) {str(err3)}")
        
        print("finished")
        self.progress.emit("Finished import")
        self.finished.emit("Finished import")