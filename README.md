# ghAIstwriter

LLM-powered ghostwriter for [Hypothesis](https://hypothesis.readthedocs.io/). _ghAIstwriter_ can automatically generate strategies for property-based testing using the [Hypothesis](https://hypothesis.readthedocs.io/) library, based on your function descriptions. You can describe your functions through natural language specifications, function signatures and docstrings, or simply your entire function body.

## Usage

1. To use ghAIstwriter, you need to finetune Gemini using the [Google AI Studio](https://aistudio.google.com/) and obtain an API key. Copy the `example.env` file provided in this repository to a new file named `.env` and fill in your model ID (`tunedModels/...`) and API key. 

2. Install the required dependencies using `pip install -r requirements.txt`.
