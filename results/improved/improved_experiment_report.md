# Improved Experiment Report

Generated: 2026-06-25T09:55:16.606673+00:00
Device target: t4
Primary model: BAAI/bge-large-en-v1.5

## Summary
- Total posts: 7966
- Time span: 2017-10 to 2023-08
- Highest BITE total: reddit_qanon (0.1300)
- Lowest BITE total: qdrops (0.0184)
- Top overlap pair: parler|twitter (0.2727)

## Ablation Leader
- Best run: MiniLM-L6_mcs40
- Ablation: main
- Composite score: 0.5966
- Silhouette: 0.7948
- Coherence (c_v): 0.4784
- Mean persistence: 0.525

## Ablation Table
| run | ablation | model | mcs | topics | silhouette | coherence_cv | persistence | score |
|---|---|---|---:|---:|---:|---:|---:|---:|
| MiniLM-L6_mcs40 | main | all-MiniLM-L6-v2 | 40 | 2 | 0.7948 | 0.4784 | 0.525 | 0.5966 |
| bge-large-en.5_mcs40 | drop_admin | BAAI/bge-large-en-v1.5 | 40 | 3 | 0.6115 | 0.3 | 0.683 | 0.5850 |
| mpnet-base_mcs40 | main | all-mpnet-base-v2 | 40 | 2 | 0.8147 | 0.3238 | 0.538 | 0.5782 |
| bge-large-en.5_mcs25 | drop_admin | BAAI/bge-large-en-v1.5 | 25 | 7 | 0.1597 | 0.4406 | 0.638 | 0.4550 |
| bge-large-en.5_mcs40 | main | BAAI/bge-large-en-v1.5 | 40 | 4 | 0.237 | 0.401 | 0.467 | 0.3848 |
| bge-large-en.5_mcs25 | main | BAAI/bge-large-en-v1.5 | 25 | 18 | 0.4798 | 0.3956 | 0.3 | 0.3731 |
| mpnet-base_mcs25 | main | all-mpnet-base-v2 | 25 | 4 | 0.1937 | 0.3718 | 0.467 | 0.3660 |
| MiniLM-L6_mcs25 | main | all-MiniLM-L6-v2 | 25 | 19 | 0.4205 | 0.3798 | 0.291 | 0.3476 |
| MiniLM-L6_mcs15 | main | all-MiniLM-L6-v2 | 15 | 56 | 0.603 | 0.3969 | 0.149 | 0.3348 |
| bge-large-en.5_mcs15 | main | BAAI/bge-large-en-v1.5 | 15 | 39 | 0.5269 | 0.3948 | 0.192 | 0.3330 |
| mpnet-base_mcs15 | main | all-mpnet-base-v2 | 15 | 50 | 0.5574 | 0.4144 | 0.149 | 0.3246 |
| bge-large-en.5_mcs15 | drop_admin | BAAI/bge-large-en-v1.5 | 15 | 43 | 0.5256 | 0.4126 | 0.104 | 0.2922 |

## Artifacts
- Plots: results/improved/plots/
- Codebook: results/improved/improved_experiment_codebook.json
- Transfer bundle: /content/qanon_results_bundle_improved.zip
