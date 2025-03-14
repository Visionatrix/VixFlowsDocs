---
title: ComfyUI to Visionatrix migration
---

If you want to adopt your ComfyUI workflow to use in Visionatrix, you
can use this guide to help you do so. There are a few steps you need to
follow.

---

## 1. Install ComfyUI-Visionatrix custom nodes

First, it is recommended to install our custom
[ComfyUI-Visionatrix](https://github.com/Visionatrix/ComfyUI-Visionatrix)
nodes. Otherwise, you will have to use custom nodes titles which will be parsed by Visionatrix.

``` bash
git clone https://github.com/Visionatrix/ComfyUI-Visionatrix.git
```

!!! note

    You can do the required migration via nodes titles, which is less
    convenient. The node title must be like this:
    `input;Display Name;optional;advanced;order=1;custom_id=custom_name`.

---

## 2. Define the input params

Visionatrix UI aims simplicity and clarity. Define the most important
input params of your ComfyUI workflow to extract them to the Visionatrix
UI as inputs, for example:

-   prompt (textarea)
-   negative prompt (textarea)
-   prompt strength (range)
-   some logic toggles (checkbox)
-   input files (file)

For that you will need to attach our custom nodes as adapters to your
nodes receiving these inputs that will be filled by the user from
the Visionatrix UI.

As example, you can have a look at our [list of worklows](https://github.com/Visionatrix/VixFlowsDocs/tree/main/flows)
adopted to the new format.

!!! note

    The list of available nodes can be found in the readme of the
    [ComfyUI-Visionatrix](https://github.com/Visionatrix/ComfyUI-Visionatrix)
    repository.

---

### 2.1 Node to Input mapping via title string

Alternatively, Visionatrix supports other Nodes mapping as an input
param via node title string separated by semicolon.

> The nodes titles starting with `input;` keyword are considered input parameters to Visionatrix.

The parameters list:

-   `input` - keyword to define the input param
-   `Display Name` - positional parameter, the name of the input field
    displayed in the UI
-   `optional` - if present, the optional field is set to True
-   `advanced` - if present, the advanced field is set to True
-   `order=1` - the order of the input param in the UI
-   `custom_id=custom_name` - the custom id of the input param

---

### 2.2 Defining file inputs

-   `LoadImage` - default ComfyUI image loader node as image file input
    field. As required title: `input;Input image;order=1`, or optional
    advanced: `input;Optional helper image;optional;advanced;order=20`;

    !!! note

        We recommend to always define `custom_id` value as it greatly helps to have a constant name for input parameter for API.
        Like: `input;Person's face;order=1;custom_id=person_face`

-   You can make a mask from `LoadImage` using `mask` word. When you do so you need to specify `source_input_name` which point to `custom_id` of input for which this mask belongs.

    Full input for inpainting and mask definition will be:

        `input;Image to redraw;order=1;custom_id=source_image;`
        `input;Mask to redraw;order=2;custom_id=mask_redraw;mask;source_input_name=source_image`

---

## 3. Map the models for automatic download

Visionatrix simplifies and automates the process of downloading the models.

You need to ensure that models used in workflow are known to Visionatrix, see [models catalog](./models_catalog.md)

---

## 4. Build the list of available flows

The last step is to build the list of available flows in the Visionatrix
UI. Follow the steps described in
[options.py](https://github.com/Visionatrix/Visionatrix/blob/c93e8153bfe3e1bf55dddca65ee899edb7319cc7/visionatrix/options.py#L51-L67)
file for `FLOWS_URL` and `MODELS_CATALOG_URL` to enable Visionatrix
local workflows development mode:

Create a zip with adjusted/new flows:

``` bash
cd ../VixFlowsDocs && zip -r ../Visionatrix/flows.zip flows && cd ../Visionatrix
```

And uncomment appropriate code lines in [options.py file](https://github.com/Visionatrix/Visionatrix/blob/main/visionatrix/options.py)
to use local versions of the flows.

---

## 5. Verify and test the workflow

Last step is to run Visionatrix and set up your workflow to verify that
everything works as expected.
