import numpy as np
from typing import List, Optional
import logging
from ..stdp.generalized_stdp import CausalSTDP

logger = logging.getLogger(__name__)

class SNNNetwork:
    """
    Spiking Neural Network with STDP plasticity.
    """
    
    def __init__(self, n_neurons: int, stdp_rule: Optional[CausalSTDP] = None):
        self.n_neurons = n_neurons
        self.weights = np.zeros((n_neurons, n_neurons))
        self.stdp = stdp_rule if stdp_rule else CausalSTDP()
        
        # Neuron state
        self.v = np.zeros(n_neurons)
        self.threshold = 1.0
        self.decay = 0.1 # Membrane potential decay
        
        # Traces for STDP
        self.pre_traces = np.zeros(n_neurons)
        self.post_traces = np.zeros(n_neurons)
        self.trace_decay = 0.1 # Corresponds to tau ~ 10ms if dt=1ms
        
    def reset(self):
        self.v.fill(0)
        self.pre_traces.fill(0)
        self.post_traces.fill(0)
        # Weights persist
        
    def step(self, input_spikes: np.ndarray, dt: float = 1.0, learning: bool = True):
        """
        Single simulation step.
        
        Args:
            input_spikes: Boolean array (n_neurons,) indicating external input/clamped spikes.
                          In this framework, we assume neurons are driven by 'input_spikes' 
                          which come from the transcriptomic encoding. 
                          We learn the internal weights W.
                          
            dt: Time step ms.
        """
        # 1. Update Traces
        self.pre_traces *= (1 - self.trace_decay)
        self.post_traces *= (1 - self.trace_decay)
        
        # If a neuron spikes (externally driven), trace goes to 1 (or adds 1)
        self.pre_traces[input_spikes] += 1.0
        self.post_traces[input_spikes] += 1.0
        
        # 2. STDP Update
        if learning:
            # We treat 'input_spikes' as the activity of the network nodes.
            # The GRN nodes are the neurons. The 'input' is their expression state.
            # So pre_spikes = input_spikes, post_spikes = input_spikes.
            self.stdp.process_event(self.weights, 
                                    self.pre_traces, 
                                    self.post_traces, 
                                    input_spikes, 
                                    input_spikes)
            
            # Mask self-connections
            np.fill_diagonal(self.weights, 0.0)

class Trainer:
    """
    Manages training across cohorts.
    """
    
    def __init__(self, n_genes: int):
        self.n_genes = n_genes
        self.network = SNNNetwork(n_genes)
        
    def train_cohort(self, spike_trains: List[np.ndarray], duration_ms: float, dt: float = 1.0):
        """
        Trains on a single cohort's data.
        
        Args:
            spike_trains: List of spike times per gene.
        """
        self.network.reset()
        n_steps = int(duration_ms / dt)
        
        # Convert spike times to dense matrix for efficient stepping
        # Shape: (n_steps, n_genes) - sparse boolean
        # This might be memory intensive for long durations, but okay for batches.
        # Alternatively, iterate steps and check spikes.
        
        # Optimization: Pre-compute spike grid
        spike_grid = np.zeros((n_steps, self.n_genes), dtype=bool)
        for i, times in enumerate(spike_trains):
            indices = (np.array(times) / dt).astype(int)
            indices = indices[indices < n_steps]
            spike_grid[indices, i] = True
            
        # Simulation Loop
        for step in range(n_steps):
            current_spikes = spike_grid[step]
            self.network.step(current_spikes, dt=dt, learning=True)
            
        return self.network.weights.copy()

    def train_batch(self, 
                    cohort_spikes: List[List[np.ndarray]], 
                    duration_ms: float, 
                    dt: float = 1.0) -> np.ndarray:
        """
        Trains on multiple cohorts, averaging weights or accumulating.
        Here we accumulate updates sequentially (online learning across cohorts).
        """
        for i, spikes in enumerate(cohort_spikes):
            self.train_cohort(spikes, duration_ms, dt)
            if (i+1) % 10 == 0:
                logger.info(f"Processed {i+1} cohorts")
                
        return self.network.weights
