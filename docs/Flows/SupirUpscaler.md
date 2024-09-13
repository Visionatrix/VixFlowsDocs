# SUPIR Upscaler

*This workflow is added mostly for research purposes, it is still in development.*

**Memory requirements(both VRAM and RAM) are directly related to the input image resolution.**

> Currently, for **macOS runners** `Diffusion type` must be set to **fp32**.

- `Low memory mode`: reduces the size of processed tiles to **256**.

!!! note

    If you have a very small input image and the result is **less than 1024** (512 for low memory mode) pixels in width **or** height, **tiles should be disabled**.

From [ComfyUI-SUPIR repo](https://github.com/kijai/ComfyUI-SUPIR):

    Memory requirements are directly related to the input image resolution.
    In my testing I was able to run 512x512 to 1024x1024 with a 10GB 3080 GPU,
    and other tests on 24GB GPU to up 3072x3072.

    System RAM requirements are also hefty, don't know numbers
    but I would guess under 32GB is going to have issues, tested with 64GB.

## Examples

*This Upscaler is still in development stage, results may be get better.*

> We specifically place one portrait example where results is not perfect.

But for many tests we performed - portrait scaling is shiny compared to older scaling methods.

---

Image of a classic car:

![Image](../FlowsResults/SupirUpscaler-classic-car-1024x683.jpg)

![Image](../FlowsResults/SupirUpscaler-classic-car-result.png)

---

Jackie Chan portrait:

![Image](../FlowsResults/SupirUpscaler-jackie-chan-787x761.jpg)

![Image](../FlowsResults/SupirUpscaler-jackie-chan-result.png)

---

Shakira:

![Image](../FlowsResults/SupirUpscaler-shakira-711x474.jpeg)

![Image](../FlowsResults/SupirUpscaler-shakira-result.png)
