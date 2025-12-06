# Building Code Deep Research Agent

An AI agent designed to research building codes and zoning requirements for specific construction tasks. It uses [apify/rag-web-browser](https://apify.com/apify/rag-web-browser) to search for relevant municipal or state codes (e.g., UpCodes, Municode, city websites) and extracts specific requirements.

## How it works

This agent leverages a **ReAct** (Reason+Act) architecture using **LangGraph**:
1.  **Search**: It starts by performing a Google Search for the specific jurisdiction and building topic (e.g., "Antioch CA single family home building requirements").
2.  **Navigate & Extract**: It navigates to the most relevant search results (official city pages, code libraries) and extracts the text.
3.  **Analyze**: It uses an LLM (via OpenRouter) to analyze the text and extract specific requirements (setbacks, height limits, parking, etc.).
4.  **Report**: It outputs a structured `BuildingCodeReport` containing the findings.

## How to use

Input a natural language query describing your construction task and location.

**Example Query:**
`"Find single house building requirements in Antioch, CA."`

The agent will output a JSON report with:
-   **Jurisdiction**: Detected location (e.g., "Antioch, CA").
-   **Code Source**: The document or website used (e.g., "Antioch Municipal Code").
-   **Requirements**: A list of specific requirements found.

For a more advanced multi-agent example, see the [Finance Monitoring Agent actor](https://github.com/apify/actor-finance-monitoring-agent) or visit the [LangGraph documentation](https://langchain-ai.github.io/langgraph/concepts/multi_agent/).

#### Pay Per Event

This template uses the [Pay Per Event (PPE)](https://docs.apify.com/platform/actors/publishing/monetize#pay-per-event-pricing-model) monetization model, which provides flexible pricing based on defined events.

To charge users, define events in JSON format and save them on the Apify platform. Here is an example schema with the `task-completed` event:

```json
[
    {
        "task-completed": {
            "eventTitle": "Task completed",
            "eventDescription": "Cost per query answered.",
            "eventPriceUsd": 0.1
        }
    }
]
```

In the Actor, trigger the event with:

```python
await Actor.charge(event_name='task-completed')
```

This approach allows you to programmatically charge users directly from your Actor, covering the costs of execution and related services, such as LLM input/output tokens.

To set up the PPE model for this Actor:

- **Configure the OpenAI API key environment variable**: provide your OpenAI API key to the `OPENAI_API_KEY` in the Actor's **Environment variables**.
- **Configure Pay Per Event**: establish the Pay Per Event pricing schema in the Actor's **Monetization settings**. First, set the **Pricing model** to `Pay per event` and add the schema. An example schema can be found in [pay_per_event.json](.actor/pay_per_event.json).

## Included features

- **[Apify SDK](https://docs.apify.com/sdk/python/)** for Python - a toolkit for building Apify [Actors](https://apify.com/actors) and scrapers in Python
- **[Input schema](https://docs.apify.com/platform/actors/development/input-schema)** - define and easily validate a schema for your Actor's input
- **[Dataset](https://docs.apify.com/sdk/python/docs/concepts/storages#working-with-datasets)** - store structured data where each object stored has the same attributes
- **[Key-value store](https://docs.apify.com/platform/storage/key-value-store)** - store any kind of data, such as JSON documents, images, or text files

## Resources

- [What are AI agents?](https://blog.apify.com/what-are-ai-agents/)
- [Python tutorials in Academy](https://docs.apify.com/academy/python)
- [Apify Python SDK documentation](https://docs.apify.com/sdk/python/)
- [LangChain documentation](https://python.langchain.com/docs/introduction/)
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- [Integration with Make, GitHub, Zapier, Google Drive, and other apps](https://apify.com/integrations)


## Getting started

For complete information [see this article](https://docs.apify.com/platform/actors/development#build-actor-locally). To run the Actor use the following command:

```bash
apify run
```

## Deploy to Apify

### Connect Git repository to Apify

If you've created a Git repository for the project, you can easily connect to Apify:

1. Go to [Actor creation page](https://console.apify.com/actors/new)
2. Click on **Link Git Repository** button

### Push project on your local machine to Apify

You can also deploy the project on your local machine to Apify without the need for the Git repository.

1. Log in to Apify. You will need to provide your [Apify API Token](https://console.apify.com/account/integrations) to complete this action.

    ```bash
    apify login
    ```

2. Deploy your Actor. This command will deploy and build the Actor on the Apify Platform. You can find your newly created Actor under [Actors -> My Actors](https://console.apify.com/actors?tab=my).

    ```bash
    apify push
    ```

## Documentation reference

To learn more about Apify and Actors, take a look at the following resources:

- [Apify SDK for JavaScript documentation](https://docs.apify.com/sdk/js)
- [Apify SDK for Python documentation](https://docs.apify.com/sdk/python)
- [Apify Platform documentation](https://docs.apify.com/platform)
- [Join our developer community on Discord](https://discord.com/invite/jyEM2PRvMU)
