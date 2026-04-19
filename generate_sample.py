import pandas as pd
import numpy as np

def generate_sample_csv(filename="sample_pmu_data.csv", num_buses=5, sampling_rate=30, duration=10):
    t = np.linspace(0, duration, sampling_rate * duration)
    data_list = []
    base_freq = 60.0
    
    # Simulate a Natural Oscillation originating from Bus 2
    osc_freq = 0.8
    damping = 0.05
    source_bus = 2

    for i in range(1, num_buses + 1):
        noise = np.random.normal(0, 0.002, len(t))
        distance = abs(i - source_bus)
        amplitude = 0.05 * np.exp(-0.2 * distance)
        
        # Damped natural oscillation
        signal = amplitude * np.exp(-damping * t) * np.sin(2 * np.pi * osc_freq * t)
        freq_signal = base_freq + signal + noise
        
        df_bus = pd.DataFrame({
            "Time": t,
            "Frequency": freq_signal,
            "Bus ID": f"Bus {i}",
            "Voltage": 1.0 + np.random.normal(0, 0.001, len(t)), # Optional
            "Phase Angle": np.random.normal(0, 0.1, len(t))      # Optional
        })
        data_list.append(df_bus)
        
    full_df = pd.concat(data_list, ignore_index=True)
    full_df.to_csv(filename, index=False)
    print(f"Sample data saved to {filename}")

if __name__ == "__main__":
    generate_sample_csv()
