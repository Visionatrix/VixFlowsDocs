---
title: Gated Models
---

Sometimes, the model you want to use requires authentication to access it. These are referred to as [Gated Models](https://huggingface.co/docs/hub/models-gated).

Flows with such models are distinctly marked in the Visionatrix UI.

To install such a flow, you need to provide an `Access Token` for HuggingFace or an `API Key` for CivitAI.

### HuggingFace Token

Steps to access gated models from HuggingFace:

1. Register on [HuggingFace](https://huggingface.co) if you are not already registered.
2. Generate an access token in the settings of HuggingFace (click on your icon → Settings → Access Tokens).
3. Click `Set Permissions` for the token after generation and select `Read access to contents of all public gated repos you can access`.
4. Enter this access token in the Visionatrix settings.
5. Gain access to the model on your account by visiting its page (you can click on the model from the Visionatrix UI) and filling out the required form.

### CivitAI API Key

Steps to access gated models from CivitAI:

1. Register on [CivitAI](https://civitai.com) if you are not already registered.
2. Create an API key in the settings of CivitAI (click on your icon → Add API Key).
3. Enter this API key in the Visionatrix settings.
4. Gain access to the model on your account by visiting its page (you can click on the model from the Visionatrix UI) and filling out the required form.

#### Connecting a Worker to Process Flows with Gated Models

If you want to connect your own worker to process flows with gated models, note that user workers cannot receive global access tokens from the server to prevent leaks. You have two options:

1. Download the model yourself and place it in the folder specified in `models_catalog.json` under the `filename` or `types` keys.
2. Set the `HF_AUTH_TOKEN` environment variable with your own public access token. The worker will then be able to install flows with gated models from HuggingFace.
3. For CivitAI, set the environment variable `CA_API_KEY`.
