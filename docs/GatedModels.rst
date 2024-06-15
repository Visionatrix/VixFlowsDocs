Gated Models
============

It often happens that the model you are using is not available for download without authentication. These are referred to as `Gated Models <https://huggingface.co/docs/hub/models-gated>`_.

Flows with such models have a separate mark in the Visionatrix UI.

To be able to install such a flow, you need to specify an ``Access Token``

.. note::
    Currently, only HuggingFace Access Tokens are supported.

Steps to Access Gated Models:

1. Register on `HuggingFace <https://huggingface.co>`_ if you are not already registered
2. Gain access to the model on your account by going to its page (you can click on the model from Visionatrix UI) and filling out the form
3. Generate an access token in the settings of HuggingFace (click on your icon -> settings -> access tokens)
4. Click on ``Set Permissions`` of the token after generation and select ``Read access to contents of all public gated repos you can access``
5. Go to the Visionatrix settings and enter this access token

Alternatively, you can set an environment variable named ``HF_AUTH_TOKEN`` with the token value, but this requires setting up the environment variable for each worker if you have many of them.

I'm a user and want to connect my own worker to process flows with closed models.
---------------------------------------------------------------------------------

As user's workers cannot receive global access tokens from the server to avoid leaks, you have two options:

1. Download the model yourself and place it in the folder specified in ``models_catalog.json`` under the ``save_path`` key.
2. Set the ``HF_AUTH_TOKEN`` environment variable with your own public access token, and the worker will be able to install flows with gated models.