# AWS Bedrock Agents Framework

This repository contains a framework for creating and managing agents using AWS Bedrock, implementing two different execution approaches: Lambda-based execution and Custom Control execution.

## Overview

This framework provides a complete solution for:

1. Setting up Couchbase as a vector database
2. Creating and populating vector embeddings using AWS Bedrock
3. Creating specialized AI agents with different function capabilities
4. Implementing and comparing two execution models:
   - Lambda-based function execution
   - Custom Control (RETURN_CONTROL) based execution

## Prerequisites

- AWS Account with Bedrock access enabled
- Couchbase Server cluster (either self-hosted or on cloud)
- Python 3.9+
- AWS CLI configured with appropriate permissions

## Environment Setup

Create a `.env` file in the root directory with the following variables:

```
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_ACCOUNT_ID=your_account_id

# Couchbase Configuration
CB_HOST=couchbase://localhost
CB_USERNAME=Administrator
CB_PASSWORD=password
CB_BUCKET_NAME=vector-search-testing
SCOPE_NAME=shared
COLLECTION_NAME=bedrock
INDEX_NAME=vector_search_bedrock

# Execution Approach (custom_control or lambda)
APPROACH=custom_control
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aws-bedrock-agents-scripts.git
cd aws-bedrock-agents-scripts
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Project Structure

```
.
├── main.py                     # Main script with setup and execution logic
├── utils.py                    # Shared utility functions
├── age_lambda.py               # Lambda-based agent execution
├── age_custom_control.py       # Custom Control based agent execution
├── lambda_functions/           # Lambda function code
│   ├── bedrock_agent_researcher.py # Researcher agent Lambda
│   ├── bedrock_agent_writer.py     # Writer agent Lambda
│   ├── deploy.py               # Script to deploy Lambda functions
│   └── requirements.txt        # Lambda function dependencies
├── lambda_demo/                # Demo code for testing Lambda deployments
├── documents.json              # Sample documents for agent knowledge
└── aws_index.json              # Couchbase vector search index definition
```

## Core Components

### 1. Vector Store Setup

The framework sets up Couchbase as a vector store:
- Creates/verifies Couchbase bucket, scope, and collection
- Sets up search indexes for vector similarity search
- Loads documents from `documents.json` and embeds them using Bedrock's embedding model

### 2. Agent Implementation

Two specialized agents are implemented:

**Researcher Agent**:
- Searches through documents using semantic similarity
- Provides relevant document excerpts
- Answers questions based on document content

**Writer Agent**:
- Formats research findings in a user-friendly way
- Creates clear summaries
- Organizes information logically
- Highlights key insights

### 3. Execution Approaches

**Lambda Approach**:
- Creates Lambda functions for each agent's capabilities
- Sets up Lambda execution permissions
- Delegates function execution to AWS Lambda functions

**Custom Control Approach**:
- Uses the RETURN_CONTROL mechanism to handle function execution locally
- Processes agent responses and function calls within the application

## Usage

Run the main script to set up and test both agents:

```bash
python main.py
```

To specify which approach to use, set the `APPROACH` environment variable:

```bash
# For Lambda approach
export APPROACH=lambda
python main.py

# For Custom Control approach
export APPROACH=custom_control
python main.py
```

## Lambda Functions

The Lambda functions implement:

1. **Researcher Lambda (`bedrock_agent_researcher.py`)**:
   - Connects to Couchbase
   - Performs similarity searches using vector embeddings
   - Returns relevant document excerpts

2. **Writer Lambda (`bedrock_agent_writer.py`)**:
   - Takes content and formatting instructions
   - Uses Bedrock models to format content
   - Returns formatted content

### Deploying Lambda Functions

Lambda functions are automatically deployed when using the Lambda approach:

```bash
python lambda_functions/deploy.py
```

## Advanced Configuration

### Modifying Agent Instructions

Agent instructions and function definitions can be modified in `main.py`:

```python
researcher_instructions = """
You are a Research Assistant that helps users find relevant information in documents.
...
"""

researcher_functions = [{
    "name": "search_documents",
    "description": "Search for relevant documents using semantic similarity",
    ...
}]
```

### Adding New Documents

Add new documents to the `documents.json` file:

```json
{
  "documents": [
    {
      "text": "Your document content here",
      "metadata_field1": "value1",
      "metadata_field2": "value2"
    }
  ]
}
```

## Best Practices

1. **Error Handling**: Both approaches implement robust error handling and retries for AWS service calls
2. **Debugging**: Enable trace for better visibility into agent execution flow
3. **Performance Optimization**: Lambda functions include optimization techniques for deployment size and execution speed
4. **Security**: IAM roles are configured with minimum required permissions

## Troubleshooting

### Common Issues

1. **Lambda Deployment Failures**:
   - Ensure AWS credentials have appropriate permissions
   - Check Lambda limits in your AWS account
   - Verify network connectivity to AWS services

2. **Vector Search Issues**:
   - Verify Couchbase Search service is enabled
   - Check index definition in `aws_index.json`
   - Ensure documents have been properly embedded

3. **Agent Execution Errors**:
   - Examine logs for specific error messages
   - Verify agent instructions and function schemas match
   - Check agent preparation status using AWS console

## License

MIT License
