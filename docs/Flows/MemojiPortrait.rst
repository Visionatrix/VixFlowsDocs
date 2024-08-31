.. _MemojiPortrait:

Memoji Portrait
===============

Create cute Memoji from a photo of a person.

**Prompt** is required, simplest examples is: `girl, portrait, close up`

    .. note:: To make it look more like Memoji you can add ``sico style`` words: `sico style, girl, portrait, close up`

**Person's face pose** is optional.

Part of the flow runs on the CPU, part on the GPU, the flow is quite fast and convenient for everyday use.

Hardware
""""""""

- **Required memory: 10-16 GB**

Time to process 1 image:

- AMD 7900 XTX/Intel 10900: **5.6 sec**
- NVIDIA RTX 3060 (12 GB)/AMD 7900X: **8.6 sec**

Examples
""""""""

.. note:: As a input files, the photos of `Bruce Lee` and `Einstein` were taken from the Internet and used.

.. image:: /FlowsResults/MemojiPortrait_1.png

.. image:: /FlowsResults/MemojiPortrait_2.png

.. image:: /FlowsResults/MemojiPortrait_3.png

.. image:: /FlowsResults/MemojiPortrait_4.png
