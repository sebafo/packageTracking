# Demo Shipment Tracker API Documentation

## Overview

The Demo Shipment Tracker API allows users to access comprehensive package tracking information. Users can retrieve package details, status updates, and item-level information using a unique Tracking Number.

## Base URL

```
https://<your-demo-domain>/api/v2/package/lookup
```

## Endpoints

### 1. Get Package Details

**Endpoint:**
```http
GET /api/v2/package/lookup?trackingId=<trackingId>&fromDate=<fromDate>&toDate=<toDate>
```

**Description:**
Retrieves detailed information about a specific package using the unique tracking number.

**Parameters:**
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `trackingId` | string | Yes | The unique tracking number for the package | `PKG123456789` |
| `fromDate` | string | No | Start date for the tracking period (YYYY-MM-DD) | `2025-08-01` |
| `toDate` | string | No | End date for the tracking period (YYYY-MM-DD) | `2025-08-31` |
## Response Example

```json
{
  "packages": [
    {
      "packageKey": 987654321,
      "trackingId": "PKG123456789",
      "datePartition": 20250811,
      "serviceType": "EXPRESS",
      "customerReference": "REF20250811",
      "originCountry": "DE",
      "originCity": "Munich",
      "originFacility": "MUC1",
      "destinationCountry": "FR",
      "destinationCity": "Paris",
      "destinationFacility": "CDG2",
      "senderName": "REDACTED",
      "senderContact": "REDACTED",
      "recipientName": "REDACTED",
      "recipientContact": "REDACTED",
      "dispatchDate": "2025-08-11T09:00:00",
      "itemCount": 2,
      "packageContents": "ELECTRONICS",
      "currency": "EUR",
      "declaredValue": 199.99,
      "declaredWeight": 2.5,
      "actualWeight": 2.8,
      "items": [
        {
          "itemId": "ITM987654321",
          "itemWeightDeclared": 1.2,
          "itemWeightActual": 1.3,
          "itemDescription": "Tablet",
          "statusUpdates": [
            {
              "statusCode": "ARR",
              "statusTimestamp": "2025-08-11T10:00:00",
              "statusLocation": "MUC1",
              "statusRemarks": "Arrived at origin facility"
            }
          ]
        }
      ],
      "statusUpdates": [
        {
          "statusCode": "DEP",
          "statusTimestamp": "2025-08-11T11:00:00",
          "statusLocation": "MUC1",
          "statusRemarks": "Departed from origin facility"
        }
      ]
    }
  ]
}
```
## Field Descriptions

### Package Object

| Field | Type | Description |
|-------|------|-------------|
| `packages` | array | List of package objects |
| `packageKey` | integer | Unique identifier for the package record |
| `trackingId` | string | Unique tracking number |
| `datePartition` | integer | Date of the record in YYYYMMDD format |
| `serviceType` | string | Type of service (e.g., "EXPRESS") |
| `customerReference` | string | Reference provided by the customer |
| `originCountry` | string | Country code of origin |
| `originCity` | string | City of origin |
| `originFacility` | string | Facility code of origin |
| `destinationCountry` | string | Country code of destination |
| `destinationCity` | string | City of destination |
| `destinationFacility` | string | Facility code of destination |
| `senderName` | string | Name of sender (redacted for privacy) |
| `senderContact` | string | Contact details of sender (redacted) |
| `recipientName` | string | Name of recipient (redacted) |
| `recipientContact` | string | Contact details of recipient (redacted) |
| `dispatchDate` | string | Date and time of dispatch (ISO 8601) |
| `itemCount` | integer | Number of items in the package |
| `packageContents` | string | Description of package contents |
| `currency` | string | Currency code |
| `declaredValue` | number | Declared value of the package |
| `declaredWeight` | number | Declared weight in kilograms |
| `actualWeight` | number | Actual weight in kilograms |
| `items` | array | List of item objects within the package |
| `statusUpdates` | array | Status updates for the package |

### Item Object

| Field | Type | Description |
|-------|------|-------------|
| `itemId` | string | Unique identifier for the item |
| `itemWeightDeclared` | number | Declared weight of the item |
| `itemWeightActual` | number | Actual weight of the item |
| `itemDescription` | string | Description of the item |
| `statusUpdates` | array | Status updates for the item |

### Status Update Object

| Field | Type | Description |
|-------|------|-------------|
| `statusCode` | string | Status code (e.g., "ARR", "DEP") |
| `statusTimestamp` | string | Timestamp of the status update (ISO 8601) |
| `statusLocation` | string | Location of the status update |
| `statusRemarks` | string | Remarks for the status update |
## Error Codes

| Status Code | Description |
|-------------|-------------|
| `404 Not Found` | The tracking number does not exist |
| `400 Bad Request` | Invalid tracking number format |

## Notes

- **Privacy Protection**: Sensitive information (e.g., sender and recipient details) is redacted for privacy
- **Timestamp Format**: All timestamps are in ISO 8601 format
- **Weight Units**: All weights are specified in kilograms
- **Currency**: Values are specified in the currency indicated by the `currency` field
