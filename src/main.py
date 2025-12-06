"""Module defines the main entry point for the Apify Actor.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

from __future__ import annotations

import logging

from apify import Actor
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.models import BCARequirementReport
from src.tools import tool_research_bca
from src.utils import log_state

import os


async def main() -> None:
    """Define a main entry point for the Apify Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with Apify platform, and it also enhances performance in
    the field of web scraping significantly.

    Raises:
        ValueError: If the input is missing required attributes.
    """
    async with Actor:
        # Charge for Actor start
        await Actor.charge('actor-start')

        # Handle input
        actor_input = await Actor.get_input() or {}

        query = actor_input.get('query')
        model_name = actor_input.get('modelName', 'gpt-4o-mini')
        
        if actor_input.get('debug', False):
            Actor.log.setLevel(logging.DEBUG)
        
        if not query:
            # Fallback for testing/debugging
            Actor.log.warning('Missing "query" attribute in input. Using default test query.')
            query = "Find stair and balustrade requirements for a new Class 1 dwelling in NCC 2022 Volume Two."
        
        llm = ChatOpenAI(
            model=model_name,
            base_url="https://openrouter.apify.actor/api/v1",
            api_key="no-key-required-but-must-not-be-empty",
            default_headers={"Authorization": f"Bearer {os.getenv('APIFY_TOKEN')}"}
        )

        # Create the ReAct agent graph
        # see https://langchain-ai.github.io/langgraph/reference/prebuilt/?h=react#langgraph.prebuilt.chat_agent_executor.create_react_agent
        tools = [tool_research_bca]
        
        # We might want to use a more generic output format or just the report directly.
        # For now, let's keep it simple. The agent will use the tool and return the result.
        # Since the tool returns a complex object (BCARequirementReport), we need to ensure the agent can handle it.
        # Ideally, the agent should just return the result of the tool call if it answers the query.
        
        graph = create_react_agent(llm, tools)

        inputs: dict = {'messages': [('user', query)]}
        response_messages = []
        
        async for state in graph.astream(inputs, stream_mode='values'):
            log_state(state)
            response_messages = state['messages']

        last_message = response_messages[-1]
        
        if not last_message or not last_message.content:
            Actor.log.error('Failed to get a response from the ReAct agent!')
            await Actor.fail(status_message='Failed to get a response from the ReAct agent!')
            return

        # Charge for task completion
        await Actor.charge('task-completed')

        # Push results to the key-value store and dataset
        store = await Actor.open_key_value_store()
        
        # Try to find the actual tool output if possible, otherwise use the final message
        final_answer = last_message.content
        
        await store.set_value('response.txt', str(final_answer))
        Actor.log.info('Saved the "response.txt" file into the key-value store!')

        await Actor.push_data(
            {
                'response': str(final_answer),
                'query': query,
            }
        )
        Actor.log.info('Pushed the data into the dataset!')
