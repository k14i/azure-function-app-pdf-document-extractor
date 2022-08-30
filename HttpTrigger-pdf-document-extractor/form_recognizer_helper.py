#!/usr/bin/env python

import os
import json
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential


class FormRecognizerHelper(object):
    def __init__(self, endpoint: str, key: str, model_id: str) -> None:
        self.model_id = model_id
        self.document_analysis_client = DocumentAnalysisClient(
            endpoint = endpoint,
            credential = AzureKeyCredential(key)
        )

    def analyze_from_url(self, formUrl: str) -> None:
        poller = self.document_analysis_client.begin_analyze_document_from_url(self.model_id, formUrl)
        result = poller.result()
        return result
    
    def analyze_from_file(self, file_name: str) -> None:
        result = None
        with open(file_name, 'rb') as f:
            poller = self.document_analysis_client.begin_analyze_document(self.model_id, f)
            result = poller.result()
        return result
    
    def get_layout_in_dict_from_url(self, formUrl: str) -> dict:
        result = self.analyze_from_url(formUrl)
        return result.to_dict()
    
    def get_layout_in_json_from_url(self, formUrl: str, ensure_ascii: bool=False, indent=None) -> str:
        result = self.get_layout_in_dict_from_url(formUrl)
        return json.dumps(result, ensure_ascii=ensure_ascii, indent=indent)
    
    def get_layout_in_dict_from_file(self, file_path: str, file_name: str) -> dict:
        result = self.analyze_from_file(os.path.join(file_path, file_name))
        return result.to_dict()
    
    def get_layout_in_json_from_file(self, file_path: str, file_name: str, ensure_ascii: bool=False, indent=None) -> str:
        result = self.get_layout_in_dict_from_file(file_path, file_name)
        return json.dumps(result, ensure_ascii=ensure_ascii, indent=indent)


if __name__ == "__main__":
    endpoint = os.environ["MY_AZURE_AI_FORMRECOGNIZER_ENDPOINT"]
    key = os.environ["MY_AZURE_AI_FORMRECOGNIZER_ACCESS_KEY"]
    model_id = os.environ["MY_AZURE_AI_FORMRECOGNIZER_MODEL_ID"]

    helper = FormRecognizerHelper(endpoint, key, model_id)

    formUrl = os.environ["MY_AZURE_AI_FORMRECOGNIZER_EXAMPLE_FORM_URL"]
    result = helper.get_layout_in_json_from_file(os.environ['MY_MAIN_PIPELINE_LOCAL_FOLDER_PATH'], os.environ['MY_MAIN_PIPELINE_FILE_NAME'], indent=4)
    print(result)
