.. _PhotoStickers2:

Photo Stickers 2
================

.. note:: This feature requires vision capabilities. You must either have the **Ollama** server running with the ``llava:7b-v1.6-vicuna-q8_0 model``, or provide a ``Gemini API key`` in the settings.

Turns a photo into 4 stickers using different prompts.

Part of the flow runs on the CPU, part on the GPU, the flow is quite fast and convenient for everyday use.

Original flow/idea examples: `StickerYou - 1 photo for stickers！ <https://openart.ai/workflows/rui400/stickeryou---1-photo-for-stickers/e8TPNxcEGKdNJ40bQXlU>`_

Hardware
""""""""

- **Required memory: 16-24? GB**

.. note:: this workflow creates 4 images in batch, I only tested on a 24GB graphics card (perhaps some node(or ComfyUI?) has a memory freeing issue as there was a huge swap usage on a 32GB MacBook when testing).

Time to process 1 image:

- AMD 7900 XTX/Intel 10900: **63 sec**

Examples
""""""""

.. note:: As a input file, the photo of `Bruce Lee` was taken from the Internet and used with default prompts.

.. image:: /FlowsResults/PhotoStickers2_1.png

.. image:: /FlowsResults/PhotoStickers2_2.png

.. image:: /FlowsResults/PhotoStickers2_3.png

.. image:: /FlowsResults/PhotoStickers2_4.png
