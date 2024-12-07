---
title: Vix Workflows
---

## Introduction

ComfyUI workflows are designed for developers and those interested in
diffusion processes.

Visionatrix workflows are created on top of ComfyUI workflows for easy
deployment and straightforward use.

Currently, there are two main issues with using ComfyUI flows for the public:

1.  It's unclear where to get the model from and how to deploy/install it:

    **deployment/installation issue**

2.  Without some experience, it's unclear how to just provide inputs to simple get results:

    **usability issue**


## Automatic models mapping

To address the first issue with model mapping, Visionatrix includes a
[models_catalog.json](https://github.com/Visionatrix/VixFlows/blob/main/models_catalog.json)
file.

By default, it is taken and updated from the Visionatrix repository on
GitHub, in case you add a new flow and need to add new model mappings
you can change its path using an environment variable to a local file
path or add additional places from where to fetch it.

!!! note

    UI for easily adding models without going into too much detail, you can find it on this [documentation page](./models_catalog.md).

The file structure consists of a set of objects, each describing a
ComfyUI Node class that loads or uses a model.

``` python
"InstantID-ControlNet": {
    "regexes": [
      {
        "class_name": "ControlNetLoader",
        "input_value": "^(?=.*(?i:instantid)).*"
      }
    ],
    "url": "https://huggingface.co/InstantX/InstantID/resolve/main/ControlNetModel/diffusion_pytorch_model.safetensors",
    "homepage": "https://huggingface.co/InstantX/InstantID",
    "hash": "c8127be9f174101ebdafee9964d856b49b634435cf6daa396d3f593cf0bbbb05",
    "types": [
      "controlnet"
    ],
    "filename": "instantid-controlnet.safetensors"
  }
```

### "regexes"

Regexes are used to understand if this record related to the
specified model from the ComfyUI workflow.

`"input_name"`, `"class_name"`, and `"input_value"` are supported, both
together and separately.

!!! note

    If these conditions prove insufficient, please create an issue and we
    will find a solution together.


### "types"

This field lists one or more categories the model belongs to (e.g., `text_encoders`, `ipadapter`). It determines the folder where the model will be saved.

If `types` is empty or missing, the `filename` is assumed to be located at the root of the ComfyUI folder.

Together, `types` and `filename` should provide enough information to correctly place the model.

### "filename"

Overrides the default file name for the model.

This is particularly useful when the model has a generic name (e.g., `"model.safetensors"`) that could conflict with others.

Using a unique name avoids such conflicts.

### "url"

Indicates where to download the model from if it is not already present.

It is preferable for the model to be hosted on Hugging Face, but
`civitai.com` is also supported.

### "homepage"

An optional field with a link to the model's home page where you can
view the license.

### "hash"

The SHA256 hash of the model. Used to verify the integrity of the model
and check for download errors.

## Vix workflow overview

Starting from the Visionatrix **0.6.0**, the workflow consists of a
single file: `flow_name.json`, which is a ComfyUI workflow file adopted
to Visionatrix.

!!! note

    The main difference between Visionatrix and ComfyUI:

    **A task is created with a single request, which includes both
    incoming text parameters and input files.**


The flow metadata fields described below are filled in the `VixUi-WorkflowMetadata` node.

### "name"

The name of the workflow. It usually matches the name of the file with workflow.

### "display_name"

Used in the UI to display the name of the flow.

### "description"

A brief description of the flow for user display.

### "author"

The name of the ComfyUI flow author or the Visionatrix flow author.

### "homepage"

A link that will open when clicking on the flow author's name.

### "license"

The general license under which the flow can be used (to simplify
understanding whether it can be used behind the API service, whether it
can be used commercially, etc.)

### "documentation"

Link to additional information about the flow.

### "tags"

A list of string tags that can be used to label the categories of the flow.

### "input_params"

!!! note

    Starting with Visionatrix 0.6.0, the input params are parsed
    automatically from the adopted ComfyUI workflow. Based on the
    information from this field, the Visionatrix UI dynamically displays the
    interface.

Technically, this is a list of objects, where each object is one input
parameter, which includes:

* "name" - the key(used only when `type` is equal `"text"`)
* "display_name" - the name of the parameter displayed in the UI
* "type" - a string that can have values: `"text"` or `"image"`

    !!! note

        `"video"` and `"audio"` types will
        be added as soon as there is the first Workflow requiring it.

* "optional" - indicates whether the parameter is optional. If an
    optional field is not provided, the backend will fill it in automatically.
* "advanced" - used only in the UI, shows whether the field should
    be hidden by default (we do not want to overload the interface for regular users)
* "default" - the field value to initiate.

    !!! note

        Used for both UI and backend, but not mandatory even for
        optional fields (as in the ComfyUI flow, the Node value is still set)

* "comfy_node_id" - **a field only for the backend**, which defines what to do with this value (where to use it in the ComfyUI Flow)
