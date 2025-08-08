# Archival Logic

## Trigger
- Runs daily (timer-triggered Azure Function)

## Steps
1. Connect to Cosmos DB
2. Query all billing records older than 90 days
3. For each record:
   a. Convert to JSON
   b. Store in Azure Blob Storage (organized by date path)
   c. Delete from Cosmos DB
4. Log any failures for retry
