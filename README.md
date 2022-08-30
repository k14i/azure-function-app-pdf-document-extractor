# Azure Function for extracting PDF documents

## Prerequisite

1. Python 3.9
2. `pip install -U pip && pip install -r requirements.txt`
3. `cp local.settings.json.example local.settings.json`
4. Edit `local.settings.json`


## Running and testing this function locally

1. `make start`
2. `make call-post`


## Running this function on Azure

1. See [Create a Python function using Visual Studio Code - Azure Functions | Microsoft Docs](https://docs.microsoft.com/azure/azure-functions/create-first-function-vs-code-python)


## HTTP Request

### Method

* POST

### Parameters

| key | description of value |
| --- | ----- |
| azure_storage_container_name | The name of Azure Blob Storage Container |
| azure_storage_file_name | The name of Blob (file) |
| keep_local_file | Whether keep local file downloaded from Blob or not (true or false) |
| keep_blob | Whether keep the Blob or not (true or false) |

#### Example

```json
{
    "azure_storage_container_name": "source-files",
    "azure_storage_file_name": "sample-layout.pdf",
    "keep_local_file": true,
    "keep_blob": false
}
```

### Request example

```bash
curl \
-X POST \
-H "Content-Type: application/json" \
-d "{\"azure_storage_container_name\":\"source-files\", \"azure_storage_file_name\":\"sample-layout.pdf\", \"keep_local_file\":false, \"keep_blob\":false}" \
"http://localhost:7071/api/HttpTrigger-pdf-document-extractor"
```

## Response

### Example

```json
{
    "elapsed_time": 6.521904611,
    "request": {
        "method": "POST",
        "url": "http://localhost:7071/api/HttpTrigger-pdf-document-extractor",
        "headers": {
            "content-type": "application/json",
            "user-agent": "curl/7.64.1",
            "accept": "*/*",
            "content-length": "138",
            "host": "localhost:7071"
        },
        "params": {},
        "route_params": {},
        "body": {
            "azure_storage_container_name": "source-files",
            "azure_storage_file_name": "sample-layout.pdf",
            "keep_local_file": false,
            "keep_blob": false
        }
    },
    "document_id": "62df3ed462e133dca11c2314"
}
```


## See also

* [Azure Functions documentation | Microsoft Docs](https://docs.microsoft.com/azure/azure-functions/)
* [Tutorial: Use an Azure Function to process stored documents - Azure Applied AI Services | Microsoft Docs](https://docs.microsoft.com/azure/applied-ai-services/form-recognizer/tutorial-azure-function)
