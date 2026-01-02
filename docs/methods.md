# Method Overview

KORA (Kinetic Ordered Regulatory Analysis) is a novel computational biology pipeline designed to infer Gene Regulatory Networks (GRNs) from transcriptomic data, specifically in the context of neurodegenerative disorders. The core methodology leverages principles from neuroscience and machine learning, combining Spiking Neural Networks (SNNs) with generalized Spike-Timing Dependent Plasticity (STDP).

## Pipeline Stages

1.  **Data Processing**: Raw transcriptomic datasets (Microarray, RNA-seq) from public repositories (e.g., GEO) are downloaded, normalized, and harmonized to a common gene identifier space (HGNC symbols). This involves handling various data formats (SOFT, supplementary files) and annotation challenges.

2.  **Spike Encoding**: The processed, normalized gene expression data for each cohort is converted into a series of spike trains. This rate-based encoding transforms static gene expression levels into a dynamic, temporal input suitable for SNNs. Each gene is represented by a neuron, and its expression level dictates its spiking frequency.

3.  **SNN Training**: For each individual cohort, a dedicated Spiking Neural Network is instantiated and trained. The synaptic weights within these networks are adjusted using a biologically plausible Generalized STDP learning rule. This rule captures the temporal correlations between pre- and post-synaptic neuron spikes, allowing the network to learn causal relationships inherent in the transcriptomic dynamics. Training is performed on CPU.

4.  **GRN Extraction**: After training, the learned synaptic weights of the SNNs are interpreted as the regulatory influences within the GRN. A thresholding mechanism is applied to these weights to identify statistically significant regulatory edges, resulting in a directed adjacency matrix and an edge list for each cohort.

5.  **CoreML Export**: For efficient inference on Apple's Neural Engine (NPU), the distilled GRN operators (representing the learned regulatory logic) are exported as inference-only CoreML models. These models are designed for deterministic forward passes, implementing the identified activating and inhibitory regulatory connections without any learning or dynamic simulation components.

6.  **Swift Inference & Benchmarking**: A native Swift application loads and executes the CoreML models. This layer performs batch inference, enabling rapid calculation of regulatory influences. Comprehensive benchmarks compare the performance (latency, throughput, memory footprint) of inference executed on the CPU versus the Apple Neural Processing Unit (NPU).

7.  **Dynamic Visualizations**: Python-based tools generate dynamic and interactive visualizations to explore the extracted GRNs, analyze weight distributions across cohorts, and illustrate benchmark performance differences.

## Key Principles

*   **Cohort Isolation**: Each disease cohort is processed, encoded, and modeled independently to preserve cohort-specific regulatory patterns and avoid data leakage.
*   **Causal Learning**: STDP-based training inherently focuses on temporal causality, enabling the inference of directed regulatory relationships.
*   **Scalability**: The modular design allows for independent processing of diverse datasets, while CoreML export facilitates high-performance inference.
*   **Interpretability**: The distilled GRN operators provide a clear, interpretable representation of gene-gene interactions.