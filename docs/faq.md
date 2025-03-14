---
title: FAQ
---

#### Can I use ComfyUI which is included in Visionatrix?

Yes, you can install your Nodes there and run ComfyUI separately without running Visionatrix.

Also, ComfyUI is available from the Visionatrix UI or at `http://127.0.0.1:8188`.

#### Can I use my own already installed ComfyUI with Visionatrix?

By default, Visionatrix installs or expects ComfyUI to be in working directory under the `ComfyUI` folder name.

You can also tell Visionatrix to use ComfyUI installed in a different path, by setting the `COMFYUI_DIR` environment variable.

Also, you can set `comfyui_folder` database parameter(by using `set-global-setting` command) if you do not want to set the environment variable.

---

#### Can I run it on multiple GPU?

You can run one worker on one GPU and process tasks in parallel, take
a look at [Server and Worker modes](AdminManual/WorkingModes/working_modes.md#server).

---

#### Why are portrait flows on runpod.io / novita.ai slow?

Portrait flows on platforms like runpod.io or novita.ai often run slowly because these setups typically use Docker containers with restricted CPU instructions, causing the `onnxruntime` library to default to the slower `CPUExecutionProvider`.

To significantly improve performance, you can set the execution provider explicitly to use GPU acceleration with CUDA. Execute the following command:

```bash
python3 -m visionatrix set-global-setting --key="insightface_provider" --value="CUDA"
```

This overrides the default provider, allowing the flows to leverage GPU hardware and run faster.

---
