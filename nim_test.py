from openai import OpenAI
from dotenv import load_dotenv
import os

# Load NVIDIA_API_KEY from the .env file
load_dotenv()

# Create a client that talks to NVIDIA's API instead of OpenAI's API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ["NVIDIA_API_KEY"],
)

# Send a prompt to the NVIDIA NIM model
completion = client.chat.completions.create(
    model="nvidia/llama-3.3-nemotron-super-49b-v1.5",
    messages=[
        {
            "role": "system",
            "content": "You are a concise AI assistant."
        },
        {
            "role": "user",
            "content": "Explain NVIDIA NIM in simple terms."
        }
    ],
    temperature=0.2,
    top_p=0.9,
    max_tokens=500,
    stream=False,
)

# Print only the model's answer
print(completion.choices[0].message.content)
