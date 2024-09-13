.. _Colorful_XL:

Colorful XL
===========

A fairly simple flow at the moment, simply using the latest **Colorful XL** model without any post-processing.

.. note:: **Not Safe for Work (NSFW) version.**

**Supports various aspect ratios.**

**Supports fast generation using the Align Steps technique**

Hardware
""""""""

- **Required memory: works on 10 GB**

Time to generate 1 image(Vibrancy=1, Steps count=45)(fast run on/off):

- AMD 7900 XTX: **2.57 sec** / **6.8 sec**
- NVIDIA RTX 3060 (12 GB): **? sec** / **? sec**
- Apple M2 Max: **? sec** / **? sec**

Examples
""""""""

.. image:: /FlowsResults/Colorful_XL_1.png

Prompt: "*portrait, half-robot woman, in the dark, contrasting light, realistic, masterpiece*"  (Seed: 101)

.. image:: /FlowsResults/Colorful_XL_2.png

Prompt: "*half-cat woman, in the forest, vivid lights, realistic, masterpiece*"  (Fast Run: true, Vibrancy: 3, Seed: 9158296)

.. image:: /FlowsResults/Colorful_XL_3.png

Prompt: "*portrait, young man, angel, sky, sun, high contrast*"  (Fast Run: true, Vibrancy: 2, Steps number to generate: 60, Seed: 9)
