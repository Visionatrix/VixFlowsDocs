---
title: Technical Information
---

## Bundled ComfyUI nodes

Visionatrix by default install and reinstall on `update` some nodes that are required by flows we provide as examples.

You can find file with it here: [basic_node_list.py](https://github.com/Visionatrix/Visionatrix/blob/main/visionatrix/basic_node_list.py)

!!! note

    Starting from the Visionatrix `2.0` version we had switched to the [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager).

All nodes are installed from the [Comfy-Registry](https://registry.comfy.org/) or their original repositories.

You could easily update Nodes yourself if needed or install new ones.

If after updating via ComfyUI-Manager some of the nodes stopped working, we recommend running the command:

    `python3 -m visionatrix update`

This command will perform a re-instalaltion of the nodes that are included in the Visionatrix package to the original versions that were supplied with this version of Visionatrix.

---

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

When an element in the **FLOWS_URL** ends with `/`, Visionatrix fetches an archive with flows appropriate for its version:

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

---

## Models Storage

All public models catalogs are located in the [VixFlowsDocs](https://github.com/Visionatrix/VixFlowsDocs) repository.

Similar to workflows, the repository consists of a development branch **main** and a set of branches **version-X.Y**:

-   version-0.5
-   version-0.6
-   ...
-   version-1.0
-   version-1.1
-   main

The models catalogs are available in the root of the documentation and have the following form:

-   models_catalog-0.5.json
-   models_catalog-0.6.json
-   ...
-   models_catalog-1.0.json
-   models_catalog-1.1.json
-   models_catalog.json

The development version of Visionatrix fetches the `models_catalog.json` by default.

Release versions of Visionatrix fetch the models catalog for their version.

### Configuring Models Catalog Sources

The `MODELS_CATALOG_URL` variable in Visionatrix has the default value of:

```ini
MODELS_CATALOG_URL=https://visionatrix.github.io/VixFlowsDocs/
```

**You can specify multiple URLs or paths to catalogs by separating them with semicolons `;`.**

When an element in the **MODELS_CATALOG_URL** ends with `/`, Visionatrix fetches the catalog appropriate for its version:

- For development versions, it fetches `models_catalog.json`.
- For release versions, it fetches `models_catalog-X.Y.json`, where `X.Y` matches the major and minor Visionatrix version numbers.

#### Examples

1. **Default Configuration**:

    ```ini
    MODELS_CATALOG_URL=https://visionatrix.github.io/VixFlowsDocs/
    ```

    Visionatrix will fetch the models catalog from the repository corresponding to its version.

2. **Custom Models Catalog Sources**:

    ```ini
    MODELS_CATALOG_URL=https://visionatrix.github.io/VixFlowsDocs/;https://example.com/custom_models_catalog.json;/local/path/models_catalog.json
    ```

    Visionatrix will fetch models catalogs from:

    - The official repository.
    - A custom online catalog at `https://example.com/custom_models_catalog.json`.
    - A local catalog at `/local/path/models_catalog.json`.

#### Models Merging and Versioning

- When multiple models have the same name across different sources, Visionatrix will:

    - Prefer the model from the source listed later in the `MODELS_CATALOG_URL` variable.
    - Allow custom catalogs to override or supplement default models.

#### Notes

- **Local Paths**: You can specify local paths to models catalogs, which is useful during development or when working offline.

- **URL Endings**:

    - If a URL ends with `/`, Visionatrix automatically appends the appropriate `models_catalog.json` or `models_catalog-X.Y.json` based on its version.

    - If a URL points directly to a catalog (e.g., `https://example.com/custom_models_catalog.json`), Visionatrix will use that specific file.
