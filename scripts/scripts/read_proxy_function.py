import logging
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions
from azure.storage.blob import BlobServiceClient
import json
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    record_id = req.route_params.get('record_id')
    if not record_id:
        return func.HttpResponse("Missing record ID", status_code=400)

    # Cosmos DB connection
    cosmos_client = CosmosClient("<COSMOS_ENDPOINT>", credential="<COSMOS_KEY>")
    container = cosmos_client.get_database_client("<DB>").get_container_client("<CONTAINER>")

    try:
        record = container.read_item(item=record_id, partition_key=record_id)
        return func.HttpResponse(json.dumps(record), status_code=200, mimetype="application/json")
    except exceptions.CosmosResourceNotFoundError:
        logging.info(f"Record {record_id} not found in Cosmos DB. Trying Blob Storage...")

        # Blob Storage fallback
        blob_service_client = BlobServiceClient.from_connection_string("<BLOB_CONN>")
        blob_container = blob_service_client.get_container_client("archived-billing-records")

        # Try to locate the blob file. Here we assume we can calculate or look up the path.
        # For this example, a simple lookup pattern is used (you may want to index paths).
        for year in range(2020, datetime.utcnow().year + 1):
            for month in range(1, 13):
                for day in range(1, 32):
                    blob_path = f"billing/{year}/{month:02}/{day:02}/{record_id}.json"
                    try:
                        blob = blob_container.get_blob_client(blob_path)
                        data = blob.download_blob().readall()
                        return func.HttpResponse(data, status_code=200, mimetype="application/json")
                    except Exception:
                        continue  # Try next date folder

        return func.HttpResponse("Record not found in any storage layer", status_code=404)
