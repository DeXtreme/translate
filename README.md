# [Translate](https://dev.to/__dbrown__/project-translate-architecture-2icg)
An API that translates sentences and files to different languages.


# Requirements
- Python 3.10 or higher
- Terraform (latest stable version)

# Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/DeXtreme/translate.git
```

2. Navigate to the infrastructure directory:
```bash
cd backend/infrastructure
```

3. Initialize Terraform:
```bash
terraform init
```

4. Apply the Terraform configuration:
```bash
terraform apply
```
When prompted, review the planned changes and type `yes` to proceed.

5. Once deployment is complete, copy the output URL


# Usage

## Text Translation

Send a POST request to the API endpoint with a JSON payload:

```json
{
    "text": "Your text to translate",
    "lang": "target_language_code"
}
```

Example using cURL:
```bash
curl -X POST https://<api-url>/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "lang": "es"
  }'
```

The API will respond with:
```json
{
    "result": "Hola mundo"
}
```

## File Translation

### Supported File Types
- Plain text files (`.txt`)
- Word documents (`.docx`)

### API Request
Send a POST request with:
- File upload (for Word documents, use content-type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`)
- `lang` parameter specifying the target language

Example using cURL:
```bash
# For text files
curl -X POST https://<api-url>/translate/file \
  -F "file=@document.txt" \
  -F "lang=es"

# For Word documents
curl -X POST https://<api-url>/translate/file \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.docx;type=application/vnd.openxmlformats-officedocument.wordprocessingml.document" \
  -F "lang=es"
```

### Response
The API will return a JSON containing download URLs for the translated files:
```json
{
    "urls": [
        "https://example.com/translated-file-1",
        "https://example.com/translated-file-2"
    ]
}
```
