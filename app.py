import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy.fftpack import fft, fftfreq
from scipy.signal import correlate
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="WAMS Lite - Power System Oscillation Monitoring",
    page_icon="⚡",
    layout="wide"
)

# --- Helper Functions ---

def generate_synthetic_data(num_buses, sampling_rate, duration=10, forced=False):
    """
    Generates synthetic PMU frequency data with oscillations.
    
    Args:
        num_buses (int): Number of buses to simulate.
        sampling_rate (int): Samples per second (Hz).
        duration (int): Duration of the signal in seconds.
        forced (bool): If True, generates a forced oscillation.
    
    Returns:
        pd.DataFrame: Simulated PMU data.
    """
    t = np.linspace(0, duration, sampling_rate * duration)
    data_list = []
    
    # Base frequency
    base_freq = 60.0 # Hz
    
    # Oscillation Parameters
    if forced:
        # Forced: Fixed frequency, higher amplitude
        osc_freq = 2.0  # Hz
        damping = 0.0   # No damping for forced
        source_bus = np.random.randint(1, num_buses + 1)
    else:
        # Natural: Low frequency, some damping
        osc_freq = 0.8  # Hz
        damping = 0.05  # Damping ratio
        source_bus = np.random.randint(1, num_buses + 1)

    for i in range(1, num_buses + 1):
        # Noise
        noise = np.random.normal(0, 0.002, len(t))
        
        # Oscillation magnitude decays with "distance" from source_bus
        distance = abs(i - source_bus)
        amplitude = 0.05 * np.exp(-0.2 * distance)
        
        if forced:
            # Forced oscillation signal
            signal = amplitude * np.sin(2 * np.pi * osc_freq * t)
        else:
            # Natural oscillation signal (damped)
            signal = amplitude * np.exp(-damping * t) * np.sin(2 * np.pi * osc_freq * t)
            
        freq_signal = base_freq + signal + noise
        
        df_bus = pd.DataFrame({
            "Time": t,
            "Frequency": freq_signal,
            "Bus ID": f"Bus {i}"
        })
        data_list.append(df_bus)
        
    return pd.concat(data_list, ignore_index=True), source_bus

def perform_fft(signal, fs):
    """
    Performs FFT and returns frequency and magnitude.
    """
    # Remove DC component (mean)
    signal_ac = signal - np.mean(signal)
    n = len(signal_ac)
    yf = fft(signal_ac.values)
    xf = fftfreq(n, 1/fs)
    
    # Keep only positive frequencies
    pos_mask = xf > 0
    xf = xf[pos_mask]
    yf_mag = 2.0/n * np.abs(yf[pos_mask])
    
    return xf, yf_mag

def analyze_oscillations(df, fs):
    """
    Performs oscillation detection and localization.
    """
    results = {}
    buses = df["Bus ID"].unique()
    
    bus_energies = {}
    bus_ffts = {}
    
    max_amp = 0
    dominant_freq = 0
    
    for bus in buses:
        bus_data = df[df["Bus ID"] == bus]["Frequency"]
        
        # Energy calculation (Variance as a proxy for oscillation energy)
        energy = np.var(bus_data)
        bus_energies[bus] = energy
        
        # FFT
        xf, yf = perform_fft(bus_data, fs)
        bus_ffts[bus] = (xf, yf)
        
        # Find dominant frequency across all buses
        idx = np.argmax(yf)
        if yf[idx] > max_amp:
            max_amp = yf[idx]
            dominant_freq = xf[idx]

    # Detection Logic
    # Threshold for detection: if max variance > threshold
    detection_threshold = 0.0001
    max_energy = max(bus_energies.values())
    oscillation_detected = max_energy > detection_threshold
    
    # Source Localization: Bus with highest energy
    source_bus = max(bus_energies, key=bus_energies.get)
    
    # Classification (Simple Rule-Based)
    # Forced vs Natural: Natural usually < 1.0Hz, Forced can be anything but often shows less damping
    # In this lite version, we use frequency and energy distribution
    if dominant_freq > 1.2:
        osc_type = "Forced"
    else:
        osc_type = "Natural"
        
    # Severity Level
    if max_energy > 0.001:
        severity = "High"
    elif max_energy > 0.0004:
        severity = "Medium"
    else:
        severity = "Low"
        
    results = {
        "Detected": oscillation_detected,
        "Dominant Frequency": dominant_freq,
        "Type": osc_type,
        "Source Bus": source_bus,
        "Severity": severity,
        "Energies": bus_energies,
        "FFTs": bus_ffts
    }
    
    return results

# --- UI Components ---

st.title("⚡ AI-Based WAMS Lite")
st.markdown("### Power System Oscillation Detection & Localization")

# Sidebar
st.sidebar.header("User Input Configuration")
uploaded_file = st.sidebar.file_uploader("Upload PMU Data (CSV)", type=["csv"])

num_buses_input = st.sidebar.number_input("Number of Buses", min_value=2, max_value=20, value=5)
sampling_rate_input = st.sidebar.number_input("Sampling Rate (Hz)", min_value=10, max_value=100, value=30)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** If no file is uploaded, synthetic data will be generated automatically.")

# Simulation Options (only if no file)
if not uploaded_file:
    sim_type = st.sidebar.selectbox("Synthetic Data Type", ["Natural Oscillation", "Forced Oscillation"])
    run_analysis = st.sidebar.button("Run Analysis", use_container_width=True)
else:
    run_analysis = st.sidebar.button("Run Analysis", use_container_width=True)

# Main Dashboard
if run_analysis:
    with st.spinner("Analyzing PMU Data..."):
        # 1. Data Loading
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            # Basic validation
            required_cols = ["Time", "Frequency", "Bus ID"]
            if not all(col in df.columns for col in required_cols):
                st.error(f"CSV must contain: {', '.join(required_cols)}")
                st.stop()
        else:
            is_forced = (sim_type == "Forced Oscillation")
            df, actual_source = generate_synthetic_data(num_buses_input, sampling_rate_input, forced=is_forced)

        # 2. Processing
        results = analyze_oscillations(df, sampling_rate_input)
        
        # 3. Key Metrics Display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if results["Detected"]:
                st.error("🚨 Oscillation Detected")
            else:
                st.success("✅ Normal Operation")
        
        with col2:
            st.metric("Dominant Frequency", f"{results['Dominant Frequency']:.2f} Hz")
            
        with col3:
            st.metric("Oscillation Type", results["Type"])
            
        with col4:
            severity_color = {"High": "red", "Medium": "orange", "Low": "green"}[results["Severity"]]
            st.markdown(f"**Severity:** :{severity_color}[{results['Severity']}]")

        st.markdown("---")
        
        # 4. Detailed Insights
        c1, c2 = st.columns([1, 1])
        with c1:
            st.info(f"📍 **Estimated Source:** {results['Source Bus']}")
        with c2:
            st.warning(f"⚠️ **Insight:** Oscillation likely originating from {results['Source Bus']} due to highest relative signal energy.")

        # 5. Visualizations
        
        # Time Series Plot
        st.subheader("Time-Series Frequency Monitoring")
        fig_ts = px.line(df, x="Time", y="Frequency", color="Bus ID", 
                         title="Bus Frequency Deviations (Hz)",
                         labels={"Frequency": "Frequency (Hz)", "Time": "Time (s)"},
                         template="plotly_dark")
        st.plotly_chart(fig_ts, use_container_width=True)
        
        v1, v2 = st.columns(2)
        
        with v1:
            # FFT Plot
            st.subheader("Frequency Domain Analysis (FFT)")
            fig_fft = go.Figure()
            for bus, (xf, yf) in results["FFTs"].items():
                fig_fft.add_trace(go.Scatter(x=xf, y=yf, name=bus, mode='lines'))
            fig_fft.update_layout(title="FFT Spectrum (Frequency vs Amplitude)",
                                  xaxis_title="Frequency (Hz)",
                                  yaxis_title="Amplitude",
                                  template="plotly_dark",
                                  xaxis_range=[0, 5]) # Focus on low frequency range
            st.plotly_chart(fig_fft, use_container_width=True)
            
        with v2:
            # Energy Bar Chart
            st.subheader("Oscillation Intensity per Bus")
            energy_df = pd.DataFrame(list(results["Energies"].items()), columns=["Bus ID", "Energy"])
            fig_bar = px.bar(energy_df, x="Bus ID", y="Energy", color="Energy",
                             title="Signal Energy (Variance)",
                             color_continuous_scale='Viridis',
                             template="plotly_dark")
            st.plotly_chart(fig_bar, use_container_width=True)

        # Correlation Heatmap
        st.subheader("Inter-Bus Correlation Analysis")
        # Pivot data for correlation
        pivot_df = df.pivot(index='Time', columns='Bus ID', values='Frequency')
        corr_matrix = pivot_df.corr()
        fig_heat = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                             title="Frequency Correlation Matrix",
                             color_continuous_scale='RdBu_r',
                             template="plotly_dark")
        st.plotly_chart(fig_heat, use_container_width=True)

        # Recommendations
        st.markdown("---")
        st.subheader("🔍 Expert Recommendations")
        if results["Detected"]:
            st.write(f"- **Immediate Action:** Monitor {results['Source Bus']} for potential governor or exciter malfunction.")
            if results["Type"] == "Forced":
                st.write("- **Mitigation:** Identify periodic load or generator pulsing near the dominant frequency.")
            else:
                st.write("- **Mitigation:** Check PSS (Power System Stabilizer) settings for poorly damped modes.")
        else:
            st.write("- **Status:** System stability margins are within nominal limits.")
            st.write("- **Maintenance:** Routine PMU calibration recommended.")

else:
    # Landing State
    st.info("Welcome to the WAMS Lite Dashboard. Configure the inputs on the sidebar and click 'Run Analysis' to begin.")
    
    # Show a static preview or sample data instructions
    st.markdown("""
    ### System Overview
    - **Detection Logic:** Uses statistical variance and FFT peak detection to identify anomalous frequency oscillations.
    - **Classification:** Differentiates between 'Natural' (damped inter-area/local modes) and 'Forced' (sustained external drive) oscillations.
    - **Localization:** Employs energy-based source identification, highlighting the bus with the highest disturbance magnitude.
    """)

# Footer
st.markdown("---")
st.caption("WAMS Lite v1.0 | Built with Streamlit, SciPy, and Plotly for Power System Research.")
