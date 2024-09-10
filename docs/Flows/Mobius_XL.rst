.. _Mobius_XL:

Mobius XL
=========

A fairly simple flow at the moment, simply using the latest `Mobius <https://huggingface.co/Corcelio/mobius>`_ model without any post-processing.

.. note::
    *This is a very unusual model, although it is part of the SDXL family of models - its results in some areas are simply amazing.*

It has better text drawing capabilities than other SDXL models.

Since the author of this model is constantly improving it, we will update it with new versions when they are published.

Here is a link to `civitai <https://civitai.com/models/490622/mobius>`_ to learn more about the model.

Link to the author of the model on `Twitter <https://x.com/DataPlusEngine>`_.

**Supports fast generation using the Align Steps technique**

Hardware
""""""""

- **Required memory: works on 10 GB**

Time to generate 1 image:

- AMD 7900 XTX: **15.5 sec** / **6.4 sec**
- NVIDIA RTX 3060 (12 GB): **38 sec** / **17 sec**
- Apple M2 Max: **93 sec** / **39 sec**

Examples
""""""""

.. image:: /FlowsResults/Mobius_XL_1.png

Prompt: "*emotional owl looks at the viewer in surprise, masterpiece, cinematic, best quality*"  (seed: 1368672)

.. image:: /FlowsResults/Mobius_XL_2.png

Prompt: "*very angry emotional pug, future, best quality, masterpiece, cinematic, ("VIX" text logo)*"  (seed: 1220661)

.. image:: /FlowsResults/Mobius_XL_3.png

Prompt: "*portrait of male paratrooper, explosions background, masterpiece, cinematic, best quality*"  (seed: 1368894)
