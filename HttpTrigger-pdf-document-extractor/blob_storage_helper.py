#!/usr/bin/env python

import os
from azure.storage.blob import BlobServiceClient, BlobProperties

class BlobStorageHelper(object):
    def __init__(self, storage_account_name: str, storage_account_access_key: str, container_name: str) -> None:
        self.account_name = storage_account_name
        self.access_key = storage_account_access_key
        self.container_name = container_name
        self.container_client = self.get_container_client()

    def _get_blob_service_client_with_access_key(self):
        blob_service_client = BlobServiceClient(
            account_url="https://{}.blob.core.windows.net".format(self.account_name),
            credential=self.access_key
        )
        return blob_service_client

    def _get_container_client_with_access_key(self):
        blob_service_client = self._get_blob_service_client_with_access_key()
        container_client = blob_service_client.get_container_client(self.container_name)
        return container_client

    def get_container_client(self):
        container_client = self._get_container_client_with_access_key()
        return container_client
    
    def get_blob_list(self) -> list:
        blob_list = self.container_client.list_blobs()
        return blob_list
    
    def get_blob_properties(self, blob_name) -> dict:
        blob_properties = self.container_client.get_blob_client(blob_name).get_blob_properties()
        return blob_properties

    def download_blob(self, local_folder_path: str, blob_name: str) -> None:
        blob_properties = BlobProperties(name=blob_name)
        with open(os.path.join(local_folder_path, blob_name), "wb") as f:
            f.write(self.container_client.download_blob(blob_properties).readall())
            f.close()
    
    def delete_blob(self, blob_name: str) -> None:
        self.container_client.delete_blob(blob_name, delete_snapshots="include", timeout=30)

if __name__ == "__main__":
    storage_account_name = os.environ["MY_AZURE_STORAGE_ACCOUNT_NAME"]
    storage_account_access_key = os.environ["MY_AZURE_STORAGE_ACCOUNT_ACCESS_KEY"]
    container_name = os.environ["MY_AZURE_STORAGE_CONTAINER_NAME"]

    blob_storage_helper = BlobStorageHelper(storage_account_name, storage_account_access_key, container_name)

    # result = blob_storage_helper.get_blob_list()
    # for item in result:
    #     print(item.name)
    #     print(item.size)
    #     print(item.last_modified)
    #     print(item.etag)
    #     print(item.lease)
    #     print(item.server_encrypted)
    #     print(item.content_settings)
    #     print(item.tags)
    #     print(item.metadata)
    #     print(item.blob_type)
    #     print("")

    result = blob_storage_helper.get_blob_properties("sample-layout.pdf")
    print(result)

    blob_storage_helper.download_blob("/tmp", "sample-layout.pdf")
