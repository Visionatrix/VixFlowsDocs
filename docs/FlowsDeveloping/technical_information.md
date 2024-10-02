---
title: Technical Information
---

## Bundled ComfyUI nodes

Visionatrix by default install and update these nodes:

> -   [comfyui-art-venture](https://github.com/Visionatrix/comfyui-art-venture)
> -   [ComfyUI-AutoCropFaces](https://github.com/Visionatrix/ComfyUI-AutoCropFaces)
> -   [ComfyUI-BRIA_AI-RMBG](https://github.com/Visionatrix/ComfyUI-BRIA_AI-RMBG)
> -   [ComfyUI-BiRefNet](https://github.com/Visionatrix/ComfyUI-BiRefNet)
> -   [ComfyUI-Custom-Scripts](https://github.com/Visionatrix/ComfyUI-Custom-Scripts)
> -   [ComfyUI-Impact-Pack](https://github.com/Visionatrix/ComfyUI-Impact-Pack)
> -   [comfyui-ollama](https://github.com/Visionatrix/comfyui-ollama)
> -   [ComfyUI-SUPIR](https://github.com/Visionatrix/ComfyUI-SUPIR)
> -   [ComfyUI-Visionatrix](https://github.com/Visionatrix/ComfyUI-Visionatrix)
> -   [ComfyUI-WD14-Tagger](https://github.com/Visionatrix/ComfyUI-WD14-Tagger)
> -   [comfyui_controlnet_aux](https://github.com/Visionatrix/comfyui_controlnet_aux)
> -   [ComfyUI_essentials](https://github.com/Visionatrix/ComfyUI_essentials)
> -   [ComfyUI_FizzNodes](https://github.com/Visionatrix/ComfyUI_FizzNodes)
> -   [ComfyUI_Gemini_Flash](https://github.com/Visionatrix/ComfyUI_Gemini_Flash)
> -   [ComfyUI_InstantID](https://github.com/Visionatrix/ComfyUI_InstantID)
> -   [ComfyUI_IPAdapter_plus](https://github.com/Visionatrix/ComfyUI_IPAdapter_plus)
> -   [ComfyUI_UltimateSDUpscale](https://github.com/Visionatrix/ComfyUI_UltimateSDUpscale)
> -   [efficiency-nodes-comfyui](https://github.com/Visionatrix/efficiency-nodes-comfyui)
> -   [PuLID_ComfyUI](https://github.com/Visionatrix/PuLID_ComfyUI)
> -   [rgthree-comfy](https://github.com/Visionatrix/rgthree-comfy)
> -   [Skimmed_CFG](https://github.com/Visionatrix/Skimmed_CFG)
> -   [style_aligned_comfy](https://github.com/Visionatrix/style_aligned_comfy)
> -   [was-node-suite-comfyui](https://github.com/Visionatrix/was-node-suite-comfyui)
> -   [ComfyUI-PhotoMaker-Plus](https://github.com/Visionatrix/ComfyUI-PhotoMaker-Plus)

We are gradually expanding the list.

The main reason many components are missing is that they are quite
difficult to install, and we believe that an easy installation process
is more important in most cases.

## Workflows storage

All public flows are located in
[VixFlowsDocs](https://github.com/Visionatrix/VixFlowsDocs) repository.

The repository consists of a development branch **main** and a set of
branches **version-X.Y**:

-   version-0.5
-   version-0.6
-   \...
-   version-1.0
-   version-1.1
-   main

Sets of public workflows are packaged in the root of the documentation
and have the following form:

-   flows-0.5.zip
-   flows-0.6.zip
-   \...
-   flows-1.0.zip
-   flows-1.1.zip
-   flows.zip

The development version of Visionatrix fetches the `flows.zip` archive
by default.

Release versions of Visionatrix fetch sets of flows for their version.

The `FLOWS_URL` variable in Visionatrix has the default value of
`https://visionatrix.github.io/VixFlowsDocs/`

When **FLOWS_URL** ends with "/", the Visionatrix fetches an archive with flows for its version.

!!! note

    You can also specify a specific path/URL to the archive file with flows,
    and only that will be used.
