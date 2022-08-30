#!/usr/bin/env python

import logging
import os
import sys
from hashlib import sha256
from blob_storage_helper import BlobStorageHelper
from form_recognizer_helper import FormRecognizerHelper
from mongodb_helper import MongoDBHelper

class MainPipeline(object):
    def __init__(self, form_recognizer_endpoint: str, form_recognizer_access_key: str, form_recognizer_model_id: str,
            storage_account_name: str, storage_account_access_key: str, container_name: str,
            mongodb_uri: str, mongodb_database: str, mongodb_collection: str,
            local_folder_path: str, file_name: str, keep_local_file: bool=True, keep_blob: bool=True) -> None:
        self.form_recognizer_helper = FormRecognizerHelper(form_recognizer_endpoint, form_recognizer_access_key, form_recognizer_model_id)
        self.blob_storage_helper = BlobStorageHelper(storage_account_name, storage_account_access_key, container_name)
        self.mongodb_helper = MongoDBHelper(mongodb_uri, mongodb_database, mongodb_collection)
        self.local_folder_path = local_folder_path
        self.file_name = file_name
        self.is_local_file_to_be_kept = keep_local_file
        self.is_blob_to_be_kept = keep_blob

        if os.environ['MY_LOGGING_BASIC_CONFIG_STREAM']:
            logging.basicConfig(
                stream = eval(os.environ['MY_LOGGING_BASIC_CONFIG_STREAM']),
            )
        elif os.environ['MY_LOGGING_BASIC_CONFIG_FILENAME']:
            logging.basicConfig(
                filename = os.environ['MY_LOGGING_BASIC_CONFIG_FILENAME'],
                filemode = "w"
            )
        else:
            pass
        if os.environ['MY_LOGGING_BASIC_CONFIG_FORMAT'] and os.environ['MY_LOGGING_BASIC_CONFIG_LEVEL']:
            logging.basicConfig(
                format = os.environ['MY_LOGGING_BASIC_CONFIG_FORMAT'],
                level = eval(os.environ['MY_LOGGING_BASIC_CONFIG_LEVEL'])
            )
        self.logger = logging.getLogger(__name__)

    def get_blob(self) -> None:
        self.logger.info("=" * 120)
        self.logger.info("MainPipeline.get_blob")
        self.logger.info("self.local_folder_path: {}".format(self.local_folder_path))
        self.logger.info("self.file_name: {}".format(self.file_name))
        self.blob_storage_helper.download_blob(self.local_folder_path, self.file_name)

    def get_file_hash(self) -> str:
        self.logger.info("=" * 120)
        self.logger.info("MainPipeline.get_file_hash")
        self.logger.info("self.local_folder_path: {}".format(self.local_folder_path))
        self.logger.info("self.file_name: {}".format(self.file_name))
        with open(os.path.join(self.local_folder_path, self.file_name), "rb") as f:
            return sha256(f.read()).hexdigest()

    def extract_content(self) -> dict:
        self.logger.info("=" * 120)
        self.logger.info("MainPipeline.extract_content")
        self.logger.info("self.local_folder_path: {}".format(self.local_folder_path))
        self.logger.info("self.file_name: {}".format(self.file_name))
        return self.form_recognizer_helper.get_layout_in_dict_from_file(self.local_folder_path, self.file_name)

    def merge_attributes(self, attr: dict, document: dict) -> dict:
        self.logger.info("=" * 120)
        self.logger.info("MainPipeline.merge_attributes")
        self.logger.info("attr: {} ...".format(str(attr)[:100]))
        self.logger.info("document: {} ...".format(str(document)[:100]))
        return {"attributes": {**attr}, **document}

    def upsert_to_mongodb(self, document: str) -> str:
        self.logger.info("=" * 120)
        self.logger.info("MainPipeline.upsert_to_mongodb")
        self.logger.info("result: {} ...".format(str(document)[:100]))
        result = self.mongodb_helper.upsert_one(document)
        # result = self.mongodb_helper.insert_one(result)
        self.mongodb_helper.close()
        return result.upserted_id

    def delete_local_file(self) -> None:
        self.logger.info("=" * 120)
        self.logger.info("MainPipeline.delete_local_file")
        self.logger.info("self.local_folder_path: {}".format(self.local_folder_path))
        self.logger.info("self.file_name: {}".format(self.file_name))
        os.remove(os.path.join(self.local_folder_path, self.file_name))

    def delete_blob(self) -> None:
        self.logger.info("=" * 120)
        self.logger.info("MainPipeline.delete_blob")
        self.logger.info("self.file_name: {}".format(self.file_name))
        self.blob_storage_helper.delete_blob(self.file_name)

    def run(self) -> str:
        self.logger.info("=" * 120)
        self.logger.info("MainPipeline.run")
        document_id = None
        try:
            self.get_blob()
            document = self.extract_content()
            blob_properties = self.blob_storage_helper.get_blob_properties(self.file_name)
            attributes = {
                "sha256_file_hash": self.get_file_hash(),
                "file_name": self.file_name,
                "container_name": self.blob_storage_helper.container_name,
                "storage_account_name": self.blob_storage_helper.account_name,
                "blob_properties": {
                    "name": blob_properties.name,
                    "container": blob_properties.container,
                    "snapshot": blob_properties.snapshot,
                    "metadata": blob_properties.metadata,
                    "last_modified": blob_properties.last_modified,
                    "etag": blob_properties.etag,
                    "size": blob_properties.size,
                    "content_range": blob_properties.content_range,
                    "creattion_time": blob_properties.creation_time,
                },
            }
            document = self.merge_attributes(attributes, document)
            object_id = self.upsert_to_mongodb(document)
            if not self.is_local_file_to_be_kept:
                self.delete_local_file()
            if not self.is_blob_to_be_kept:
                self.delete_blob()
            document_id = str(object_id)
        except Exception as e:
            self.logger.error("Exception: {}".format(e))
        return document_id

if __name__ == "__main__":
    main_pipeline = MainPipeline(
        os.environ["MY_AZURE_AI_FORMRECOGNIZER_ENDPOINT"],
        os.environ["MY_AZURE_AI_FORMRECOGNIZER_ACCESS_KEY"],
        os.environ["MY_AZURE_AI_FORMRECOGNIZER_MODEL_ID"],
        os.environ["MY_AZURE_STORAGE_ACCOUNT_NAME"],
        os.environ["MY_AZURE_STORAGE_ACCOUNT_ACCESS_KEY"],
        os.environ["MY_AZURE_STORAGE_CONTAINER_NAME"],
        os.environ["MY_MONGODB_URI"],
        os.environ["MY_MONGODB_DATABASE"],
        os.environ["MY_MONGODB_COLLECTION"],
        os.environ["MY_MAIN_PIPELINE_LOCAL_FOLDER_PATH"],
        os.environ["MY_MAIN_PIPELINE_FILE_NAME"],
        eval(os.environ["MY_MAIN_PIPELINE_KEEP_LOCAL_FILE"]),
        eval(os.environ["MY_MAIN_PIPELINE_KEEP_BLOB"])
    )
    retval = main_pipeline.run()
    main_pipeline.logger.info("retval: {}".format(retval))
