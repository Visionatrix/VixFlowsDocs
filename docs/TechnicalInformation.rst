Technical Information
=====================

Bundled ComfyUI nodes
---------------------

Visionatrix by default install and update these nodes:

 * `ComfyUI-Impact-Pack <https://github.com/Visionatrix/ComfyUI-Impact-Pack>`_
 * `ComfyUI_InstantID <https://github.com/Visionatrix/ComfyUI_InstantID>`_
 * `ComfyUI_IPAdapter_plus <https://github.com/Visionatrix/ComfyUI_IPAdapter_plus>`_
 * `efficiency-nodes-comfyui <https://github.com/Visionatrix/efficiency-nodes-comfyui>`_
 * `ComfyUI_UltimateSDUpscale <https://github.com/Visionatrix/ComfyUI_UltimateSDUpscale>`_
 * `ComfyUI-WD14-Tagger <https://github.com/Visionatrix/ComfyUI-WD14-Tagger>`_
 * `ComfyUI-SUPIR <https://github.com/Visionatrix/ComfyUI-SUPIR>`_
 * `ComfyUI_essentials <https://github.com/Visionatrix/ComfyUI_essentials>`_
 * `ComfyUI-Custom-Scripts <https://github.com/Visionatrix/ComfyUI-Custom-Scripts>`_
 * `rgthree-comfy <https://github.com/Visionatrix/rgthree-comfy>`_
 * `comfyui_controlnet_aux <https://github.com/Visionatrix/comfyui_controlnet_aux>`_
 * `ComfyUI-AutomaticCFG <https://github.com/Visionatrix/ComfyUI-AutomaticCFG>`_

We are gradually expanding the list.

The main reason many components are missing is that they are quite difficult to install, and we believe that an easy installation process is more important in most cases.


Workflows storage
-----------------

All public flows are located in `VixFlowsDocs <https://github.com/Visionatrix/VixFlowsDocs>`_ repository.

The repository consists of a development branch **main** and a set of branches **version-X.Y**:

* version-0.5
* version-0.6
* ...
* version-1.0
* version-1.1
* main

Sets of public workflows are packaged in the root of the documentation and have the following form:

* flows-0.5.zip
* flows-0.6.zip
* ...
* flows-1.0.zip
* flows-1.1.zip
* flows.zip

The development version of Visionatrix fetches the ``flows.zip`` archive by default.

Release versions of Visionatrix fetch sets of flows for their version.

The ``FLOWS_URL`` variable in Visionatrix has the default value of ``https://visionatrix.github.io/VixFlowsDocs/``

When **FLOWS_URL** ends with "/", the Visionatrix fetches an archive with flows for its version.

.. note::
    You can also specify a specific path/URL to the archive file with flows, and only that will be used.


Update algorithm of Visionatrix
-------------------------------

Developer versions are updated only to development versions, release versions only to release ones.

.. note::
    If you are not a developer, you are better off using the release version, as they should be more stable.

It is recommended to update Vix with the ``easy_install.py`` script.

The update scheme in `easy_install.py <https://github.com/Visionatrix/Visionatrix/blob/main/scripts/easy_install.py>`_ is quite simple; everything is done with ordinary Git commands.

* If the current version is a dev release or the current branch is ``main`` then:

    1. Check out the ``main`` branch.
    2. Pull the latest changes from the remote repository.

* If the current version is a tagged release version:

    1. Determine the latest tag for the current major version, and if a newer version tag is found, check out the latest version tag within the current major version.
    2. If no newer version is found within the current major version, check for the next major version.
    3. If a newer major version tag is found, prompt the user to update to this newer major version.

* After checking out the appropriate version, run a ``pip install`` command to update the Python packages.
* Finally, run the ``python3 -m visionatrix update`` command to ensure that any additional necessary updates are applied (ComfyUI, custom nodes, flows).
