.. _SD3_Medium:

StableDiffusion3-Medium
=======================

Flow using the gated model, requires a HuggingFace token to setup.

*This flow is made more for development and verification that we have successfully added the ability to use gated/closed models.*

.. note::
    In the future this Flow will either be modernized or removed when something better appears to replace it based on the feature-tuned SD3, if there are any.

**Supports various aspect ratios.**

Hardware
""""""""

- **Required memory: 12-16 GB**

Time to generate 1 image:

- AMD 7900 XTX: **20.2 sec**
- NVIDIA RTX 3060 (12 GB): **25-32 sec**
- Apple M2 Max: **97 sec**

Examples
""""""""

.. image:: /FlowsResults/SD3_Medium_1.png

Prompt: "*Black kitten with white wings sitting on a blue cloud, cinematic*" | prompt_strength: 5.1 (seed: 6814591)

.. image:: /FlowsResults/SD3_Medium_2.png

Prompt: "*poster, cyborg girl against an alien, black baground, high contrast, high details, cinematic*" | prompt_strength: 5.5 (seed: 2131028)

.. image:: /FlowsResults/SD3_Medium_3.png

Prompt: "*an oil line art painting of the angel impressive neon shadows, warm colors*" | prompt_strength: 4.1 (seed: 1167357)
