# ghAIstwriter

LLM-powered ghostwriter for [Hypothesis](https://hypothesis.readthedocs.io/). _ghAIstwriter_ can automatically generate strategies for property-based testing using the [Hypothesis](https://hypothesis.readthedocs.io/) library, based on your function descriptions. You can describe your functions through natural language specifications, function signatures and docstrings, or simply your entire function body.

## Usage

1. To use ghAIstwriter, you need to finetune Gemini using the [Google AI Studio](https://aistudio.google.com/) and obtain an API key. Copy the `example.env` file provided in this repository to a new file named `.env` and fill in your model ID (`tunedModels/...`) and API key. You will also have to [set up OAuth](https://ai.google.dev/gemini-api/docs/oauth) on your Google Cloud project to obtain a `client_secret.json` file to be placed in the root directory of this repository. Once you have installed the [gCloud CLI](https://cloud.google.com/sdk/docs/install), run the following command to authenticate yourself.

```bash
gcloud auth application-default login \
    # --no-browser \
    --client-id-file=client_secret.json \
    --scopes='https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/generative-language.retriever'
```

2. Install the required dependencies using `pip install -r requirements.txt`.
