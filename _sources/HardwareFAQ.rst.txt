Hardware FAQ
============

First, you can take a look at the information in the `ComfyUI repository <https://github.com/comfyanonymous/ComfyUI/wiki/Which-GPU-should-I-buy-for-ComfyUI>`_.

.. note:: If you are using Windows and want to avoid hassles, currently, there are no alternatives to Nvidia. PyTorch is expected to release a native version for AMD for Windows soon, but until then, Nvidia is the only option.

List of GPUs by usefulness:

1. Nvidia 4090 ``24 GB``
2. AMD 7900 XTX ``24 GB``
3. Nvidia 3090 ``24 GB``
4. Nvidia 4080 Super ``16 GB``
5. Nvidia 4070 Ti Super ``16 GB``
6. AMD RX 7900 XT ``20 GB``
7. AMD RX 7900 GRE ``16 GB``
8. Nvidia 4060 Ti ``16 GB``
9. Nvidia 3060 ``12 GB``

.. note:: You can also look at any performance tests of hardware for ComfyUI as a reference.

---

Q: Why are there no AMD cards other than *AMD 7900 series* on the list?

A: *ROCM (Radeon Open Compute) "officially" supports only* `these cards <https://rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html#supported-gpus>`_.

---

Q: How much RAM is needed in the system?

A: *For normal operation, 32 GB is sufficient, but if you want to handle large resolutions with Supir Scaler Workflow, then 64 GB is recommended.*

---

Q: How to use 2 GPUs?

A: *The simplest way is to run 2 workers, each assigned to its own GPU, so they can process tasks in parallel.*
