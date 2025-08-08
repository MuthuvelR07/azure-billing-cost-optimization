# Retrieval Logic

## Trigger
- HTTP-triggered Azure Function called by API

## Steps
1. Get `record_id` from request
2. Try reading from Cosmos DB
   - If found → return it
3. If not found:
   a. Construct expected blob path(s)
   b. Try to fetch from Blob Storage
   c. If found → return it
4. If not found in either → return 404
