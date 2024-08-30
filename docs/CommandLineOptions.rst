Command Line Options
====================

Most of the options supported by `ComfyUI` are supported.

They can be specified when starting manually:

.. code-block:: shell

    python3 -m visionatrix run --ui --use-split-cross-attention --disable-smart-memory

Here are the list of the supported command line options related to `Visionatrix` for **run** command:

  --backend_dir=BACKEND_DIR
                        Directory for the backend(folder with ComfyUI)
                            Default: ``vix_backend``
  --flows_dir=FLOWS_DIR
                        Directory for the flows
                            Default: ``vix_flows``
  --models_dir=MODELS_DIR
                        Directory for the models
                            Default: ```vix_models``
  --tasks_files_dir=TASKS_FILES_DIR
                        Directory for input/output files
                            Default: ``vix_task_files``
  --host=HOST           Host to be used by Visionatrix
  --port=PORT           Port to be used by Visionatrix
  --ui                  Flag to enable User interface(JS frontend).

Supported **ComfyUI** options
-----------------------------

  --cuda-device DEVICE_ID
                        Set the id of the cuda device this instance will use.
  --cuda-malloc         Enable cudaMallocAsync (enabled by default for torch
                        2.0 and up).
  --disable-cuda-malloc
                        Disable cudaMallocAsync.
  --force-fp32          Force fp32 (If this makes your GPU work better please report it).
  --force-fp16          Force fp16.
  --bf16-unet           Run the UNET in bf16. This should only be used for
                        testing stuff.
  --fp16-unet           Store unet weights in fp16.
  --fp8_e4m3fn-unet     Store unet weights in fp8_e4m3fn.
  --fp8_e5m2-unet       Store unet weights in fp8_e5m2.
  --fp16-vae            Run the VAE in fp16, might cause black images.
  --fp32-vae            Run the VAE in full precision fp32.
  --bf16-vae            Run the VAE in bf16.
  --cpu-vae             Run the VAE on the CPU.
  --fp8_e4m3fn-text-enc
                        Store text encoder weights in fp8 (e4m3fn variant).
  --fp8_e5m2-text-enc   Store text encoder weights in fp8 (e5m2 variant).
  --fp16-text-enc       Store text encoder weights in fp16.
  --fp32-text-enc       Store text encoder weights in fp32.
  --cache-classic       Use the old style (aggressive) caching. (Default)
  --cache-lru           Use LRU caching with a maximum of N node results cached. May use more RAM/VRAM.
  --disable-ipex-optimize
                        Disables ipex.optimize when loading models with Intel GPUs.
  --use-split-cross-attention
                        Use the split cross attention optimization. Ignored when xformers is used.
  --use-quad-cross-attention
                        Use the sub-quadratic cross attention optimization. Ignored when xformers is used.
  --use-pytorch-cross-attention
                        Use the new pytorch 2.0 cross attention function.
  --disable-xformers    Disable xformers.

  --force-upcast-attention
                        Force enable attention upcasting, please report if it fixes black images.
  --dont-upcast-attention
                        Disable all upcasting of attention. Should be unnecessary except for debugging.

  --gpu-only            Store and run everything (text encoders/CLIP models,
                        etc... on the GPU).
  --highvram            By default models will be unloaded to CPU memory after
                        being used. This option keeps them in GPU memory.
  --normalvram          Used to force normal vram use if lowvram gets
                        automatically enabled.
  --lowvram             Split the unet in parts to use less vram.
  --novram              When lowvram isn't enough.
  --cpu                 To use the CPU for everything (slow).
  --reserve-vram        Set the amount of VRAM in GB you want to reserve for use by your OS/other software.
  --disable-smart-memory
                        Force ComfyUI to aggressively offload to regular ram
                        instead of keeping models in vram when it can.
  --fast                Enable some untested and potentially quality deteriorating optimizations.

Additional commands
-------------------

install-flow
''''''''''''

Can be used for Workers that do not have a user interface.

.. code-block:: shell

    python3 -m visionatrix install-flow --file=path_to_json

File should contain ComfyUI workflow with the `metadata <https://visionatrix.github.io/VixFlowsDocs/VixWorkflows.html#vix-workflow-overview>`_ needed for Visionatrix.

.. code-block:: shell

  python3 -m visionatrix install-flow --name=photo_stickers

This will install flow by it's ``ID`` which is equal to it's folder name `here <https://github.com/Visionatrix/VixFlows/tree/main/flows>`_
