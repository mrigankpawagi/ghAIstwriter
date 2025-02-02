import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv
from hypothesis.strategies import SearchStrategy, tuples
from hypothesis import given, settings
import warnings

warnings.filterwarnings("ignore")

load_dotenv()
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# base path of this script
base_path = os.path.dirname(os.path.realpath(__file__))

sys.path.append(base_path)
from utils import close_parenthesis

# load the distilled prompt (Hypothesis reference)
with open(os.path.join(base_path, "distilled_prompt.txt")) as f:
    reference_prompt = f.read()

# Create the model
generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name=os.getenv("MODEL_ID"),
    generation_config=generation_config,
)

fresh_history = [
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

INSTRUCTION = """Please create a Hypothesis strategy for the following function. Return only the code wrapped in ```python and ```.  Do not put constraints on the domain of the input unless specified in the function description. Always end with ```strategy = (<strategy for arg 0>, <strategy for arg 1>, ...)```."""


def generate_strategy(
    function_description: str,
    return_raw: bool = False,
    retry_budget=5,
    chat_session_obj=None,
    prompt=None,
) -> tuple[SearchStrategy] | str:
    """
    Generate a Hypothesis strategy for the given function description.

    Args:
        function_description (str): Description of the function for which to generate the strategy. May be natural language, signature and docstring, complete function definition, etc.
        return_raw (bool): If True, return the raw strategy code instead of the strategy object. The strategies are available in the tuple "strategy" (a check may be needed to convert it to a singleton tuple if needed).
        retry_budget (int): Internal parameter to control the number of retries in case of failure.
    """
    if chat_session_obj is None or prompt is None:
        # this is a fresh chat session
        chat_session_obj = model.start_chat(history=fresh_history)
        prompt = f"{INSTRUCTION}\n{function_description}"

    try:
        response = chat_session_obj.send_message(prompt).text
        strategy_code = response.split("```python", 1)[-1].split("```", 1)[0].strip()

        # Gemini often forgets the last few closing parenthesis so try to fix that
        strategy_code = close_parenthesis(strategy_code)

        if return_raw:
            return strategy_code

        env = {}
        exec(strategy_code, env)
        strategy = env["strategy"]

        # strategy should be a tuple
        if not isinstance(strategy, tuple):
            strategy = (strategy,)

        # check that the strategy is well-formed
        @settings(max_examples=1)
        @given(tuples(*strategy))
        def test(args):
            pass

        test()
    except Exception as e:
        if retry_budget > 0:
            return generate_strategy(
                function_description,
                retry_budget=retry_budget - 1,
                chat_session_obj=chat_session_obj,
                prompt=str(e)
                + "\nI got the above error from your previous response. Please fix it by providing a fresh response and explain how you fixed it.",
            )
        else:
            raise ValueError(f"Failed to generate strategy.")

    return strategy
