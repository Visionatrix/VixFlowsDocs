# Prometheus (Playground 2.5)

PrometheusV is presumed to be the first full rank finetune of Playground v2.5, developed by the creator of the Proteus model. This text-to-image generation model has been specifically adapted to enhance accessibility for the open-source community.

PrometheusV1 represents a significant effort to make advanced text-to-image generation more accessible to the open-source community.
Built upon the Playground v2.5 architecture, it has undergone a full rank finetune using an extensive dataset of over 400,000 images from the Proteus collection.

A key aspect of its development was the removal of custom sampling methods through brute force techniques at scale, allowing the model to work more seamlessly with standard open-source tools and pipelines.
Additionally, PrometheusV1 has been made backwards compatible with most SDXL LoRAs and tools.

This approach aims to balance the model's performance capabilities with wider compatibility and ease of use. Users can expect outputs that reflect the model's intensive training on the large Proteus dataset while benefiting from improved interoperability with common open-source frameworks and existing SDXL ecosystem.

**Supports various aspect ratios.**

## Examples

![Image](../FlowsResults/Playground_2_5_prometheus_1.png)

    portrait of gothic girl in suite looking at viewer, darkness, high quality

---

![Image](../FlowsResults/Playground_2_5_prometheus_2.png)

    close up portrait of devil in rage, high detail, ultra quality

- steps: 40

---

![Image](../FlowsResults/Playground_2_5_prometheus_3.png)

    the kindest kitten with wings, oil painting, high detail, soft colors

- steps: 40
