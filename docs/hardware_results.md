# Hardware Test Results

## SDXL Lighting

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| 4_steps | 0.9 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| 4_steps | 0.9 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| 4_steps | 1.1 | i9_10900-7900XTX | 2024/09/13 11:54:14 |
| 8_steps | 1.4 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| 8_steps | 1.4 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| 8_steps | 1.7 | i9_10900-7900XTX | 2024/09/13 11:54:14 |

## Juggernaut Lite

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| default | 9.2 | i9_10900-7900XTX | 2024/09/13 11:54:14 |
| default | 10.2 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| default | 16.6 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |

## Juggernaut XL

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| default | 7.3 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| default | 10.9 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| default | 15.1 | i9_10900-7900XTX | 2024/09/13 11:54:14 |
| fast_run | 3.1 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| fast_run | 4.6 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| fast_run | 6.3 | i9_10900-7900XTX | 2024/09/13 11:54:14 |

## Colorful XL

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| fast_run_30steps | 1.5 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| fast_run_30steps | 1.7 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| fast_run_30steps | 2.0 | i9_10900-7900XTX | 2024/09/13 11:54:14 |
| fast_run_60steps | 2.7 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| fast_run_60steps | 2.8 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| fast_run_60steps | 3.5 | i9_10900-7900XTX | 2024/09/13 11:54:14 |
| usual_run_30steps | 3.8 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| usual_run_30steps | 4.0 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| usual_run_30steps | 5.0 | i9_10900-7900XTX | 2024/09/13 11:54:14 |
| usual_run_60steps | 7.0 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| usual_run_60steps | 7.2 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| usual_run_60steps | 9.6 | i9_10900-7900XTX | 2024/09/13 11:54:14 |

## Mobius XL

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| fast_run_30steps | 5.0 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| fast_run_30steps | 7.2 | i9_10900-7900XTX | 2024/09/13 11:54:14 |
| fast_run_30steps | 11.1 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| usual_run_30steps | 12.0 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| usual_run_30steps | 17.3 | i9_10900-7900XTX | 2024/09/13 11:54:14 |
| usual_run_30steps | 24.5 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |

## Aesthetic images

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| default | 7.0 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| default | 10.5 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| default | 15.1 | i9_10900-7900XTX | 2024/09/13 11:54:14 |
| fast_run | 3.7 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| fast_run | 4.4 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| fast_run | 6.2 | i9_10900-7900XTX | 2024/09/13 11:54:14 |

## Prometheus model

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| 25steps | 5.7 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| 25steps | 8.9 | i9_10900-7900XTX | 2024/09/13 11:54:14 |
| 25steps | 12.0 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |
| 50steps | 11.2 | R9_7900X-4070TiS | 2024/09/13 13:12:33 |
| 50steps | 17.4 | i9_10900-7900XTX | 2024/09/13 11:54:14 |
| 50steps | 20.5 | EPYC_75F3-4090 | 2024/09/14 12:50:03 |

## Flux (Small)

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| 20steps | 13.1 | EPYC_75F3-4090 | 2024/09/14 12:43:35 |
| 20steps | 23.9 | R9_7900X-4070TiS | 2024/09/13 14:02:12 |
| 20steps | 37.4 | i9_10900-7900XTX | 2024/09/13 14:21:16 |
| 40steps | 25.8 | EPYC_75F3-4090 | 2024/09/14 12:43:35 |
| 40steps | 46.7 | R9_7900X-4070TiS | 2024/09/13 14:02:12 |
| 40steps | 74.4 | i9_10900-7900XTX | 2024/09/13 14:21:16 |

## Flux Lighting (Small)

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| default | 2.9 | EPYC_75F3-4090 | 2024/09/14 12:43:35 |
| default | 5.5 | R9_7900X-4070TiS | 2024/09/13 14:02:12 |
| default | 7.4 | i9_10900-7900XTX | 2024/09/13 14:21:16 |

## Stable Cascade

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| one_pass | 5.8 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| one_pass | 6.3 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |
| one_pass | 7.7 | i9_10900-7900XTX | 2024/09/13 13:41:37 |
| three_pass | 26.2 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |
| three_pass | 38.4 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| three_pass | 65.4 | i9_10900-7900XTX | 2024/09/13 13:41:37 |
| two_pass | 14.5 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |
| two_pass | 18.3 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| two_pass | 27.0 | i9_10900-7900XTX | 2024/09/13 13:41:37 |

## HunyuanDiT

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| 20steps | 6.5 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |
| 20steps | 11.0 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| 20steps | 20.9 | i9_10900-7900XTX | 2024/09/13 13:41:37 |
| 40steps | 12.5 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |
| 40steps | 21.9 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| 40steps | 41.5 | i9_10900-7900XTX | 2024/09/13 13:41:37 |

## Vintage Portrait

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| default | 19.6 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| default | 25.5 | i9_10900-7900XTX | 2024/09/13 13:41:37 |
| default | 67.7 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |

## Sketch Portrait

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| default | 3.7 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| default | 4.3 | i9_10900-7900XTX | 2024/09/13 13:41:37 |
| default | 42.2 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |

## ComicU Portrait

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| default | 3.7 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| default | 4.4 | i9_10900-7900XTX | 2024/09/13 13:41:37 |
| default | 23.5 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |

## Ghibli Portrait

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| default | 3.2 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| default | 4.1 | i9_10900-7900XTX | 2024/09/13 13:41:37 |
| default | 23.6 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |

## Memoji Portrait

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| default | 3.2 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| default | 3.8 | i9_10900-7900XTX | 2024/09/13 13:41:37 |

## Photo from 1 image

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| default | 9.5 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| default | 13.1 | i9_10900-7900XTX | 2024/09/13 13:41:37 |

## Remove background (BiRefNet)

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| 1024x1024 | 0.4 | i9_10900-7900XTX | 2024/09/13 13:41:37 |
| 1024x1024 | 0.4 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |
| 1024x1024 | 0.4 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |

## Remove background

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| 1024x1024 | 0.2 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| 1024x1024 | 0.3 | i9_10900-7900XTX | 2024/09/13 13:41:37 |
| 1024x1024 | 0.3 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |

## SUPIR Upscaler

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| 1MPx1.5 | 93.3 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| 1MPx1.5 | 115.8 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |
| 1MPx1.5 | 124.5 | i9_10900-7900XTX | 2024/09/13 13:41:37 |

## Photo Stickers

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| default | 28.5 | R9_7900X-4070TiS | 2024/09/13 13:22:53 |
| default | 33.3 | i9_10900-7900XTX | 2024/09/13 13:41:37 |
| default | 150.0 | EPYC_75F3-4090 | 2024/09/14 14:03:35 |

## Flux

| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |
| ---------- | :---------------------: | -------------------- | --------- |
| 20steps | 14.8 | EPYC_75F3-4090 | 2024/09/14 12:22:38 |
| 20steps | 52.6 | i9_10900-7900XTX | 2024/09/13 14:33:49 |
| 40steps | 28.4 | EPYC_75F3-4090 | 2024/09/14 12:22:38 |
| 40steps | 103.5 | i9_10900-7900XTX | 2024/09/13 14:33:49 |
