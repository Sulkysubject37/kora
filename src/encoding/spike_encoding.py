import numpy as np
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)

class SpikeEncoder:
    """
    Encodes continuous gene expression data into spike trains using rate-based encoding.
    """
    
    def __init__(self, 
                 dt: float = 1.0, 
                 max_freq: float = 100.0, 
                 refractory_period: float = 0.0,
                 seed: int = 42):
        """
        Args:
            dt: Simulation time step (ms)
            max_freq: Maximum firing rate (Hz) corresponding to expression=1.0
            refractory_period: Minimum time between spikes (ms)
            seed: Random seed
        """
        self.dt = dt
        self.max_freq = max_freq
        self.refractory_period = refractory_period
        self.rng = np.random.default_rng(seed)
        
    def encode(self, expression_data: np.ndarray, duration_ms: float = 1000.0) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Encodes expression data into spikes.
        
        Args:
            expression_data: (n_genes,) or (n_timepoints, n_genes) array of expression values [0, 1].
                             If 1D, assumes constant expression over 'duration_ms'.
                             If 2D, interpolates or segments 'duration_ms' across timepoints.
            duration_ms: Total duration of the spike train in ms.
            
        Returns:
            spike_times: List of length n_genes, each containing spike times (ms).
            spike_indices: List of length n_genes, containing indices (redundant but useful for some formats).
        """
        if expression_data.ndim == 1:
            # Constant expression case
            n_genes = len(expression_data)
            n_steps = int(duration_ms / self.dt)
            rates = expression_data * self.max_freq * (self.dt / 1000.0) # probability per step
            
            spike_times = [[] for _ in range(n_genes)]
            
            for gene_idx in range(n_genes):
                rate = rates[gene_idx]
                last_spike_time = -self.refractory_period
                
                for step in range(n_steps):
                    time = step * self.dt
                    
                    if time - last_spike_time < self.refractory_period:
                        continue
                        
                    if self.rng.random() < rate:
                        spike_times[gene_idx].append(time)
                        last_spike_time = time
                        
            return spike_times
            
        elif expression_data.ndim == 2:
            # Time-varying expression case
            # We assume expression_data points are equally spaced over duration_ms
            n_timepoints, n_genes = expression_data.shape
            steps_per_point = int(duration_ms / (n_timepoints * self.dt))
            
            # This is a simplification; ideally we'd interpolate. 
            # For now, we hold the value for the duration of the timepoint segment.
            
            spike_times = [[] for _ in range(n_genes)]
            
            for t_idx in range(n_timepoints):
                current_expression = expression_data[t_idx]
                rates = current_expression * self.max_freq * (self.dt / 1000.0)
                
                start_time = t_idx * steps_per_point * self.dt
                
                for step in range(steps_per_point):
                    current_time = start_time + step * self.dt
                    
                    for gene_idx in range(n_genes):
                        # Refractory check (simplified global tracking)
                        # To do this efficiently, we'd track last_spike per gene
                        pass 
            
            # Re-implementing more efficiently
            total_steps = int(duration_ms / self.dt)
            # Interpolate expression to full resolution
            # For strict correctness with the "transcriptomic" nature, 
            # we might just want to treat each transcriptomic timepoint as a window.
            
            # Let's use a simpler approach: Process by window
            window_duration = duration_ms / n_timepoints
            current_time_offset = 0.0
            
            all_spikes = [[] for _ in range(n_genes)]
            last_spike_times = np.full(n_genes, -self.refractory_period)
            
            for t_idx in range(n_timepoints):
                rates = expression_data[t_idx] * self.max_freq * (self.dt / 1000.0)
                steps_in_window = int(window_duration / self.dt)
                
                # Vectorized probability check for this window
                # Shape: (steps_in_window, n_genes)
                rand_vals = self.rng.random((steps_in_window, n_genes))
                spikes = rand_vals < rates[None, :] # Broadcast rates
                
                # Convert to times
                # This doesn't easily handle refractory period vectorially across steps dependent on history
                # Fallback to loop for correctness with refractory
                
                for step in range(steps_in_window):
                    time = current_time_offset + step * self.dt
                    
                    # Identify potential spikes
                    potential_spikes = np.where(rand_vals[step] < rates)[0]
                    
                    for gene_idx in potential_spikes:
                        if time - last_spike_times[gene_idx] >= self.refractory_period:
                            all_spikes[gene_idx].append(time)
                            last_spike_times[gene_idx] = time
                            
                current_time_offset += window_duration
                
            return [np.array(x) for x in all_spikes]
            
        else:
            raise ValueError("expression_data must be 1D or 2D")
