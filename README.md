# ghAIstwriter

<p align=center>
    <img src="https://github.com/user-attachments/assets/eba2b743-7022-4a6a-a2f8-3cc87fc96880">
</p>

LLM-powered ghostwriter for [Hypothesis](https://hypothesis.readthedocs.io/). _ghAIstwriter_ can automatically generate strategies for property-based testing using the [Hypothesis](https://hypothesis.readthedocs.io/) library, based on your function descriptions. You can describe your functions through natural language specifications, function signatures and docstrings, or simply your entire function body.

## Set Up

1. To use ghAIstwriter, you need to finetune Gemini using the [Google AI Studio](https://aistudio.google.com/) and obtain an API key. Upload `dataset/ghaiswriter.csv` to Google AI Studio for finetuning and proceed with the default hyperparameters.

2. Copy the `example.env` file provided in this repository to a new file named `.env` and fill in your model ID (`tunedModels/...`) and API key.

3. You will also have to [set up OAuth](https://ai.google.dev/gemini-api/docs/oauth) on your Google Cloud project to obtain a `client_secret.json` file to be placed in the root directory of this repository. Once you have installed the [gCloud CLI](https://cloud.google.com/sdk/docs/install), run the following command to authenticate yourself.

```bash
gcloud auth application-default login \
    # --no-browser \
    --client-id-file=client_secret.json \
    --scopes='https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/generative-language.retriever'
```

4. Install the required dependencies using `pip install -r requirements.txt`.

## Usage

```python
from ghaiswriter import generate_strategy

strategy = generate_strategy("function description")
```

This returns a tuple of Hypothesis strategies for the function described in the input string. The elements of the tuple correspond to the arguments of the function. For instance, you can fuzz test your function in the following manner.

```python
from hypothesis import given

@given(strategies.tuples(*strategy))
def fuzz_my_function(args):
    my_function(*args)
```

The `generate_strategy` function throws a `ValueError` if it is unable to generate a strategy and so it is advisable to wrap it in a `try-except` block. As such, `generate_strategy` attempts automatic repair through iterative feedback to the underlying model, with a maximum of 5 iterations by default (this can be changed by setting the optional `retry_budget` argument). It tries to fix syntax errors caused by missing closing parentheses, and checks for syntax and well-formedness of the returned strategy. 

Note that the function description may be a natural language specification, function signature and docstring, the entire function body, or any combination of these. It is recommended that the arguments of the function are clearly described.

The `generate_strategy` function also accepts an optional `return_raw` argument, which, if set to `True`, makes the function return a string representating Python code that builds up the strategy-tuple. This is available only for advanced usage and will usually not be required. This will bypass some of the checks for validity of the returned strategy and so may not always work as expected.
