# Bedrock Agents: Custom Control Approach Explained

This document explains the Custom Control approach for AWS Bedrock Agents, as implemented in the provided example code.

## Overview

The Custom Control approach gives the application invoking the agent the responsibility of executing the agent's defined functions (tools). When the agent decides to use a tool, it sends a `returnControl` event back to the calling application, which then executes the function locally and (optionally) returns the result to the agent to continue processing.

## Key Steps & Concepts

1.  **Define Agent:**
    *   Define instructions (prompt) for the agent.
    *   Define the function schema (tools the agent can use, e.g., `researcher_functions`, `writer_functions` in the example).

2.  **Create Agent in Bedrock:**
    *   Use `bedrock_agent_client.create_agent` to create the agent, providing the instructions and foundation model.
    *   The example's `create_agent` function includes logic to check for existing agents and potentially delete/recreate them if they are in a non-functional state.

3.  **Create Action Group (Custom Control):**
    *   Use `bedrock_agent_client.create_agent_action_group`.
    *   Crucially, set the `actionGroupExecutor` to `{"customControl": "RETURN_CONTROL"}`. This tells Bedrock to pause execution and return control to the caller when a function in this group needs to be run.
    *   Provide the `functionSchema` defined earlier.

4.  **Prepare Agent:**
    *   Use `bedrock_agent_client.prepare_agent` to make the agent ready for invocation.
    *   The `wait_for_agent_status` utility function polls until the agent reaches a `PREPARED` or `Available` state.

5.  **Create Agent Alias:**
    *   An alias (e.g., "v1") is created using `bedrock_agent_client.create_agent_alias` for invoking the agent.

6.  **Invoke Agent & Handle Return Control:**
    *   Use `bedrock_runtime_client.invoke_agent`, providing the `agentId`, `agentAliasId`, `sessionId`, and `inputText`. Set `enableTrace=True` for debugging.
    *   Process the streaming response (`response['completion']`).
    *   **Listen for `returnControl` events:** When the agent decides to use a function, the stream will contain an event with a `returnControl` key.
    *   **Parse the Invocation:** Extract the `functionInvocationInput` from the `returnControl` event to get the `actionGroup`, `function` name, and `parameters`.
    *   **Execute the Function Locally:** The example's `invoke_agent` function directly calls the corresponding Python function (e.g., `search_documents` imported from `utils`, or a simple formatting logic for `format_content`) using the extracted parameters. It has direct access to application state like the `vector_store` object.
    *   **Handle the Result:**
        *   *Note:* The provided example implementation **does not** seem to use the `ReturnControl` invocation type to send the function's result *back* to the *same* agent invocation to continue the turn.
        *   Instead, it executes the function, gets the result (e.g., `search_results`), formats it into a string, and effectively *ends* that agent invocation, returning the formatted string as the `result`.
        *   Subsequent steps (like formatting the research) involve a *new* call to `invoke_agent` for the writer agent, passing the result from the previous step as input. This differs from designs where the result is returned to the same agent turn for further reasoning.

## Pros

*   **Full Control:** The application has complete control over the execution environment and logic of the tools.
*   **Direct State Access:** Tools can directly access application memory, state, and resources (like the `vector_store` object in the example) without needing separate deployment or complex configuration passing.
*   **Simpler Local Development:** Can be easier to test and debug locally as the tool execution happens within the same process.
*   **Flexibility:** Allows integration with any library or service available to the application.

## Cons

*   **Application Burden:** The application code is responsible for implementing and executing the tool logic.
*   **Scalability:** The scalability of tool execution is tied to the scalability of the application itself.
*   **Tighter Coupling:** The agent's functionality is more tightly coupled with the application code.
*   **Interaction Model:** The specific implementation shown requires chaining separate agent invocations rather than letting the agent continue processing within a single turn after a tool is used. Implementing the latter (returning results via `ReturnControl`) adds complexity to the application's handling of the `invoke_agent` response/request cycle. 