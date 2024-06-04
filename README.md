# Installation

```bash
pip install -r requirements.txt --user
```
# Setup
setup .env file in the root directory with the following content
```bash
OPENAI_API_VERSION="2024-02-01"
AZURE_OPENAI_ENDPOINT="XXXX"
AZURE_OPENAI_API_KEY="XXXX"
GPT_DEPLOYMENT_NAME="XXXX"
EMBEDDING_DEPLOYMENT_NAME="XXXX"
````


# Run

```bash
py ted.py -r https://github.com/AmadeusITGroup/jetstream-mini-controller.git -f unit-tests
```