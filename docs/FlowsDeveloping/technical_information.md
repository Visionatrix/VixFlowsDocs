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

## Workflows Storage

All public flows are located in the [VixFlowsDocs](https://github.com/Visionatrix/VixFlowsDocs) repository.

The repository consists of a development branch **main** and a set of branches **version-X.Y**:

-   version-0.5
-   version-0.6
-   ...
-   version-1.0
-   version-1.1
-   main

Sets of public workflows are packaged in the root of the documentation and have the following form:

-   flows-0.5.zip
-   flows-0.6.zip
-   ...
-   flows-1.0.zip
-   flows-1.1.zip
-   flows.zip

The development version of Visionatrix fetches the `flows.zip` archive by default.

Release versions of Visionatrix fetch sets of flows for their version.

### Configuring Flows Sources

The `FLOWS_URL` variable in Visionatrix has the default value of:

```ini
FLOWS_URL=https://visionatrix.github.io/VixFlowsDocs/
```

**You can specify multiple URLs or paths to flow archives by separating them with semicolons `;`.**

When element in the **FLOWS_URL** ends with `/`, Visionatrix fetches an archive with flows appropriate for its version:

- For development versions, it fetches `flows.zip`.
- For release versions, it fetches `flows-X.Y.zip`, where `X.Y` matches the major and minor Visionatrix version numbers.

#### Examples

1. **Default Configuration**:

    ```ini
    FLOWS_URL=https://visionatrix.github.io/VixFlowsDocs/
    ```

    Visionatrix will fetch flows from the official repository corresponding to its version.

2. **Custom Flow Sources**:

    ```ini
    FLOWS_URL=https://visionatrix.github.io/VixFlowsDocs/;https://example.com/custom_flows.zip;/local/path/flows.zip
    ```

    Visionatrix will fetch flows from:

    - The official repository.
    - A custom online archive at `https://example.com/custom_flows.zip`.
    - A local archive at `/local/path/flows.zip`.

#### Flow Merging and Versioning

- When multiple flows have the same name across different sources, Visionatrix will:

    - Prefer the flow with the highest version number.
    - If versions are equal, the flow from the first source in the `FLOWS_URL` list takes precedence.

- This allows you to override or supplement the default flows with custom ones.

#### Notes

- **Local Paths**: You can specify local paths to flow archives, which is useful during development or when working offline.

- **URL Endings**:

    - If a URL ends with `/`, Visionatrix automatically appends the appropriate `flows.zip` or `flows-X.Y.zip` based on its version.

    - If a URL points directly to an archive (e.g., `https://example.com/custom_flows.zip`), Visionatrix will use that specific file.
