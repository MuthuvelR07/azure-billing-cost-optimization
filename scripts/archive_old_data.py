import datetime
import logging
import azure.functions as func
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import json

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Archival function triggered.')

    # Connect to Cosmos DB
    cosmos_client = CosmosClient("<COSMOS_ENDPOINT>", credential="<COSMOS_KEY>")
    db = cosmos_client.get_database_client("<DB_NAME>")
    container = db.get_container_client("<CONTAINER_NAME>")

    # Connect to Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string("<BLOB_CONN_STRING>")
    blob_container = blob_service_client.get_container_client("archived-billing-records")

    # Determine archival cutoff date
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=90)
    query = f"SELECT * FROM c WHERE c.timestamp < '{cutoff_date.isoformat()}'"

    for item in container.query_items(query, enable_cross_partition_query=True):
        record_id = item['id']
        billing_date = datetime.datetime.fromisoformat(item['timestamp'])

        blob_path = f"billing/{billing_date.year}/{billing_date.month:02}/{billing_date.day:02}/{record_id}.json"
        blob_data = json.dumps(item)

        # Upload to Blob
        blob_container.upload_blob(blob_path, blob_data, overwrite=True)

        # Delete from Cosmos DB
        container.delete_item(item=record_id, partition_key=item['partitionKey'])

    logging.info('Archival completed.')
