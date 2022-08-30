import logging
import azure.functions as func

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from main_pipeline import MainPipeline
import json
from time import perf_counter_ns


def main(req: func.HttpRequest) -> func.HttpResponse:
    start_time = perf_counter_ns()
    logging.info('Python HTTP trigger function processed a request.')

    req_body = req.get_json()
    if req_body:
        logging.debug("req_body: {}".format(req_body))
        if "azure_storage_file_name" in req_body and req_body.get("azure_storage_file_name"):
            azure_storage_file_name = req_body["azure_storage_file_name"]
        else:
            azure_storage_file_name = os.environ["MY_MAIN_PIPELINE_FILE_NAME"]
        logging.info("azure_storage_file_name: {}".format(azure_storage_file_name))
        if "azure_storage_container_name" in req_body and req_body.get("azure_storage_container_name"):
            azure_storage_container_name = req_body["azure_storage_container_name"]
        else:
            azure_storage_container_name = os.environ["MY_AZURE_STORAGE_CONTAINER_NAME"]
        logging.info("azure_storage_container_name: {}".format(azure_storage_container_name))
        if "keep_local_file" in req_body and req_body.get("keep_local_file") in [True, False]:
            keep_local_file = req_body["keep_local_file"]
        else:
            keep_local_file = eval(os.environ["MY_MAIN_PIPELINE_KEEP_LOCAL_FILE"])
        logging.info("keep_local_file: {}".format(keep_local_file))
        if "keep_blob" in req_body and req_body.get("keep_blob") in [True, False]:
            keep_blob = req_body["keep_blob"]
        else:
            keep_blob = eval(os.environ["MY_MAIN_PIPELINE_KEEP_BLOB"])
        logging.info("keep_blob: {}".format(keep_blob))

    main_pipeline = MainPipeline(
        os.environ["MY_AZURE_AI_FORMRECOGNIZER_ENDPOINT"],
        os.environ["MY_AZURE_AI_FORMRECOGNIZER_ACCESS_KEY"],
        os.environ["MY_AZURE_AI_FORMRECOGNIZER_MODEL_ID"],
        os.environ["MY_AZURE_STORAGE_ACCOUNT_NAME"],
        os.environ["MY_AZURE_STORAGE_ACCOUNT_ACCESS_KEY"],
        azure_storage_container_name,
        os.environ["MY_MONGODB_URI"],
        os.environ["MY_MONGODB_DATABASE"],
        os.environ["MY_MONGODB_COLLECTION"],
        os.environ["MY_MAIN_PIPELINE_LOCAL_FOLDER_PATH"],
        azure_storage_file_name,
        keep_local_file,
        keep_blob,
    )
    retval = main_pipeline.run()
    end_time = perf_counter_ns()

    res = {
        "elapsed_time": (end_time - start_time) / 1000000000,
        "request": {
            "method": req.method,
            "url": req.url,
            "headers": {k: v for k, v in req.headers.items()},
            "params": {k: v for k, v in req.params.items()},
            "route_params": {k: v for k, v in req.route_params.items()},
            "body": req_body
        }
    }

    if retval:
        res['document_id'] = retval
        return func.HttpResponse(json.dumps(res), status_code=201, mimetype="application/json", charset="utf-8", headers={"Content-Type": "application/json"})
    else:
        return func.HttpResponse(json.dumps(res), status_code=500, mimetype="application/json", charset="utf-8", headers={"Content-Type": "application/json"})
