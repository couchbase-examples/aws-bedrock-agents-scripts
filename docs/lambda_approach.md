# Bedrock Agents: Lambda Approach Explained

This document explains the Lambda approach for AWS Bedrock Agents, as implemented in the provided example code (including the code in `awsbedrock-agents/lambda_functions`).

## Overview

The Lambda approach delegates the execution of an agent's defined functions (tools) to separate AWS Lambda functions. When the agent decides to use a tool, Bedrock directly invokes the corresponding Lambda function specified in the action group configuration, passing the required parameters. The Lambda function executes the logic and returns the result to the agent, which then continues processing within the same invocation.

## Key Steps & Concepts

1.  **Define Agent:**
    *   Define instructions (prompt) for the agent.
    *   Define the function schema (tools the agent can use, e.g., `researcher_functions_lambda`, `writer_functions_lambda` in the example). The schema defines the interface the agent expects.

2.  **Implement Lambda Handlers:**
    *   Create separate AWS Lambda functions to implement the logic for each tool defined in the schema (e.g., one Lambda for `search_documents`, another for `format_content`).
    *   These Lambda functions receive an event payload containing the API path, parameters, and other details of the agent's request.
    *   The Lambda code needs to parse this event, execute the required action (e.g., query the vector store, format text), and return a specific JSON response structure that Bedrock expects.
    *   The example includes a `deploy` script in `awsbedrock-agents/lambda_functions` to package and deploy these handlers.
    *   *Environment Configuration:* The Lambdas need access to necessary resources and configuration (e.g., Couchbase connection details, Bedrock embeddings client). The example writes a `.env` file before deployment to potentially pass this information, though the exact mechanism within the Lambda deployment/runtime isn't fully shown.

3.  **Create Agent in Bedrock:**
    *   Use `bedrock_agent_client.create_agent` similar to the Custom Control approach.

4.  **Create Action Group (Lambda):**
    *   Use `bedrock_agent_client.create_agent_action_group`.
    *   Crucially, set the `actionGroupExecutor` to `{"lambda": "arn:aws:lambda:<region>:<account_id>:function:<lambda_function_name>"}`. This points Bedrock to the specific Lambda function ARN responsible for executing the actions in this group.
    *   Provide the `functionSchema` defined earlier.

5.  **Prepare Agent:**
    *   Use `bedrock_agent_client.prepare_agent`.

6.  **Create Agent Alias:**
    *   Use `bedrock_agent_client.create_agent_alias`.

7.  **Invoke Agent:**
    *   Use `bedrock_runtime_client.invoke_agent`.
    *   Bedrock handles the invocation of the configured Lambda function when the agent decides to use a tool.
    *   The application code simply receives the final response from the agent after the tool execution (if any) is complete. It doesn't need to handle `returnControl` events for function execution.
    *   *Debugging Note:* The example's `invoke_agent` function includes extensive debugging prints and attempts to manually re-execute the logic *if* the agent's final response `result` is empty but a `returnControl` event *was* observed. This suggests potential issues or complexities in correctly receiving the final result after Lambda execution in the streaming response, leading to this fallback/debugging logic being added in the script.

## Pros

*   **Decoupling:** Tool execution logic is separate from the main application, potentially managed by different teams or deployment cycles.
*   **Scalability:** Leverages the inherent scalability and serverless nature of AWS Lambda for tool execution.
*   **Managed Execution:** AWS manages the invocation and execution environment for the Lambda functions.
*   **Simpler Application Code:** The application invoking the agent doesn't need to implement the tool logic or handle the `returnControl` event for execution.

## Cons

*   **Deployment Complexity:** Requires setting up, configuring, and deploying separate Lambda functions, including managing their dependencies and permissions.
*   **State Management:** Passing state or context between the main application and the Lambda functions can be more complex (e.g., requires passing connection details, potentially initializing clients within the Lambda).
*   **Cold Starts:** Lambda cold starts can introduce latency into the agent's response time.
*   **Debugging:** Debugging issues that span the Bedrock Agent service and the Lambda execution can be more challenging.
*   **Cost:** Incurs separate Lambda execution costs. 