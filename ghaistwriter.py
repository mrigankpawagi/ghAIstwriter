import os
import google.generativeai as genai
from dotenv import load_dotenv
from hypothesis.strategies import SearchStrategy

load_dotenv()
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# base path of this script
base_path = os.path.dirname(os.path.realpath(__file__))

# load the distilled prompt (Hypothesis reference)
with open(os.path.join(base_path, "distilled_prompt.txt")) as f:
    reference_prompt = f.read()

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name=os.getenv("MODEL_ID"),
    generation_config=generation_config,
)

chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                reference_prompt,
            ],
        },
        {
            "role": "model",
            "parts": [
                "Thank you for providing this reference. I will keep this in mind while writing Hypothesis strategies.",
            ],
        },
    ]
)

INSTRUCTION = """Please create a Hypothesis strategy for the following function. Return only the code wrapped in python and . Make sure you create a variable called "strategy" which is a tuple containing strategies for each argument."""


def generate_strategy(
    function_description: str, retry_budget=5
) -> tuple[SearchStrategy]:
    prompt = f"{INSTRUCTION}\n{function_description}"

    try:
        response = chat_session.send_message(prompt).text
        strategy_code = response.split("```python", 1)[-1].split("```", 1)[0].strip()

        env = {}
        exec(strategy_code, env)
        strategy = env["strategy"]
    except Exception as e:
        if retry_budget > 0:
            print(f"Retrying... {retry_budget} retries left.")
            return generate_strategy(function_description, retry_budget - 1)
        else:
            raise e

    if not isinstance(strategy, tuple):
        strategy = (strategy,)
    return strategy


if __name__ == "__main__":
    function_description = """def first_nonzero(nums: list[float]) -> float:
    \"\"\" Return the first non-zero value in nums.
    
    >>> first_nonzero([0.0 , 3.7 , 0.0])
    3.7
    \"\"\""""
    strategy = generate_strategy(function_description)
    print(strategy)

    from hypothesis import given, settings

    @settings(max_examples=10)
    @given(*strategy)
    def test_first_nonzero(nums):
        print(nums)

    test_first_nonzero()
