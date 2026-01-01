import numpy as np
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

class GeneralizedSTDP:
    """
    Implements generalized Spike-Timing Dependent Plasticity (STDP) for GRN inference.
    Supports causal updates where pre-post timing strengthens connections (LTP) 
    and post-pre timing weakens them (LTD), with optional modulation.
    """
    
    def __init__(self, 
                 learning_rate: float = 0.01,
                 tau_plus: float = 20.0,
                 tau_minus: float = 20.0,
                 A_plus: float = 1.0,
                 A_minus: float = 1.0,
                 w_max: float = 1.0,
                 w_min: float = -1.0):
        """
        Args:
            learning_rate: Global scaling factor for weight updates.
            tau_plus: Time constant for LTP (ms).
            tau_minus: Time constant for LTD (ms).
            A_plus: Amplitude of LTP update.
            A_minus: Amplitude of LTD update.
            w_max: Maximum weight bound.
            w_min: Minimum weight bound.
        """
        self.lr = learning_rate
        self.tau_plus = tau_plus
        self.tau_minus = tau_minus
        self.A_plus = A_plus
        self.A_minus = A_minus
        self.w_max = w_max
        self.w_min = w_min
        
    def update_weights(self, 
                       weights: np.ndarray, 
                       pre_spike_times: np.ndarray, 
                       post_spike_times: np.ndarray, 
                       current_time: float,
                       modulation: float = 1.0) -> np.ndarray:
        """
        Updates weights based on recent spike history.
        
        Args:
            weights: Current weight matrix (n_pre, n_post).
            pre_spike_times: Array of last spike times for pre-synaptic neurons (n_pre,). 
                             Use -inf if no spike recently.
            post_spike_times: Array of last spike times for post-synaptic neurons (n_post,).
            current_time: Current simulation time (ms).
            modulation: Scalar modulation factor (e.g., disease stage).
            
        Returns:
            Updated weight matrix.
        """
        # Calculate time differences
        # We only care about pairs where a spike *just* happened
        # Ideally, this is called when a post-synaptic neuron spikes (for LTP) 
        # or when a pre-synaptic neuron spikes (for LTD).
        # However, for batch simulation, we might process vectors.
        
        # Let's assume this is called at every time step or event. 
        # But efficiently, we usually only update rows/cols associated with active neurons.
        # For simplicity in this CPU reference impl, we'll assume we are given MASKS of who spiked.
        pass
        # Refactoring API for integration with Simulation Loop
        
        return weights

    def compute_update(self, dt: float) -> float:
        """
        Computes the STDP kernel value for a time difference dt = t_post - t_pre.
        """
        if dt > 0:
            return self.A_plus * np.exp(-dt / self.tau_plus)
        elif dt < 0:
            return -self.A_minus * np.exp(dt / self.tau_minus)
        else:
            return 0.0

class CausalSTDP(GeneralizedSTDP):
    """
    Specific implementation optimized for matrix operations in the training loop.
    """
    
    def process_event(self, 
                      weights: np.ndarray, 
                      pre_traces: np.ndarray, 
                      post_traces: np.ndarray, 
                      pre_spikes: np.ndarray, 
                      post_spikes: np.ndarray,
                      modulation: float = 1.0):
        """
        On-line STDP update using traces.
        
        Args:
            weights: (n_pre, n_post) matrix. Modified in-place.
            pre_traces: (n_pre,) exponential trace of pre-synaptic activity.
            post_traces: (n_post,) exponential trace of post-synaptic activity.
            pre_spikes: (n_pre,) boolean mask of neurons that spiked this step.
            post_spikes: (n_post,) boolean mask of neurons that spiked this step.
        """
        
        # LTP: Pre (trace) -> Post (spike)
        # If post neuron j spikes, increase weights from all pre i based on their trace.
        if np.any(post_spikes):
            # w_ij += lr * A_plus * pre_trace_i
            # We update columns j where post_spikes[j] is True
            active_post_indices = np.where(post_spikes)[0]
            
            # Outer product-like update, but we only select columns
            # delta (n_pre, n_active_post) = pre_traces[:, None] * 1
            
            # weights[:, j] += ...
            dw_ltp = self.lr * modulation * self.A_plus * pre_traces[:, None]
            weights[:, active_post_indices] += dw_ltp
            
        # LTD: Post (trace) -> Pre (spike)
        # If pre neuron i spikes, decrease weights to all post j based on their trace.
        if np.any(pre_spikes):
            active_pre_indices = np.where(pre_spikes)[0]
            
            # weights[i, :] -= ...
            dw_ltd = self.lr * modulation * self.A_minus * post_traces[None, :]
            weights[active_pre_indices, :] -= dw_ltd
            
        # Clip weights
        np.clip(weights, self.w_min, self.w_max, out=weights)
        
        return weights
