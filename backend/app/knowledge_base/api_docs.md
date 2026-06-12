# API Documentation

API keys are generated in the dashboard.

## Rate Limit

100 requests per minute per API key.

## Authentication

All API requests require a Bearer token in the Authorization header:
Authorization: Bearer <your-api-key>

## Error Handling

- 400 Bad Request: Invalid payload or missing required fields
- 401 Unauthorized: Missing or invalid API key
- 404 Not Found: Resource does not exist
- 422 Unprocessable Entity: Validation error
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Server-side failure

## Outage Classification

API outage issues should be classified as technical support and routed to the engineering on-call team.
