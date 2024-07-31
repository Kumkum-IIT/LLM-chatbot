from typing import List, Optional
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler
import os

from .env import load_dotenv

load_dotenv()

ASSISTANT_ID = os.environ.get("ASSISTANT_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Access the environment variable containing your OpenAI API key
openai_api_key = OPENAI_API_KEY

ASSISTANT_ID = ASSISTANT_ID

# Create an instance of the OpenAI client with your API key
client = OpenAI(api_key=openai_api_key)

# EventHandler class to handle the events in the response stream.
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

thread_data = {}
all_chat = []

def submit_message(assistant_id, thread_id, user_message):
    thread_id_str = str(thread_id)
    client.beta.threads.messages.create(
        thread_id=thread_id_str, role="user", content=user_message
    )

def create_thread_and_run(user_input):
    THREAD_ID = ""
    # if not thread_data:
    #     thread = client.beta.threads.create()
    #     thread_data[0] = thread
    # else:
    #     thread = client.beta.threads.create()
    #     max_key = max(thread_data.keys())
    #     next_key = max_key + 1
    #     if next_key not in thread_data:
    #         thread_data[next_key] = thread

    # if not THREAD_ID:
    #     THREAD_ID = thread_data[0]

    if THREAD_ID is None:
        thread = client.beta.threads.create()
        THREAD_ID = thread
    else:
        try:
            thread = client.beta.threads.retrieve(thread_id=THREAD_ID.id)
        except Exception as e:
            try:
                thread = client.beta.threads.create()
                THREAD_ID = thread
            except Exception as e:
                print(f'Error occurring in create_thread_and_run: {e}')

    submit_message(ASSISTANT_ID, thread.id, user_input)
    return thread

def pretty_print(messages):
    assistant_responses = []
    for m in messages:
        if m.role == "assistant":
            assistant_responses.append(m.content[0].text.value)
    return assistant_responses[-1]

def call_gpt_model(query):
    thread = create_thread_and_run(query)
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done() # waiting for the stream to finish because twilio was not able to handle the stream
    response = client.beta.threads.messages.list(thread_id=str(thread.id), order="asc")
    gptresponse = pretty_print(response)
    return gptresponse

call_gpt_model("Hello! I need a vacation.")
