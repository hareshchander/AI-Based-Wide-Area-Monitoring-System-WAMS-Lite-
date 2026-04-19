# AI-Based Wide Area Monitoring System (WAMS Lite)

An interactive, Streamlit-based web application for **Power System Oscillation Detection and Localization**. This tool simulates a simplified wide-area monitoring system (WAMS) capable of analyzing multi-bus PMU frequency data to detect, analyze, and locate oscillations in modern power systems.

## 🚀 Features

- **Real-Time Detection:** Uses statistical thresholds (variance/energy-based) to detect anomalies in frequency signals.
- **Frequency Analysis:** Implements Fast Fourier Transform (FFT) to identify dominant oscillation frequencies.
- **Oscillation Classification:** Rule-based classification to distinguish between **Forced** and **Natural** oscillations.
- **Source Localization:** Automatically identifies the most probable source bus using signal energy comparison and cross-correlation analysis across multiple buses.
- **Interactive Visualization:** High-quality Plotly dashboards featuring:
  - Multi-bus Time-series monitoring.
  - FFT Spectrum (Frequency vs Amplitude).
  - Oscillation Intensity (Energy) Bar Charts.
  - Inter-Bus Correlation Heatmaps.
- **AI-Based Insights:** Provides color-coded alerts (Normal/Detected), severity assessments (Low/Medium/High), and basic mitigation recommendations.

## 🛠️ Tech Stack

- **Python**
- **Streamlit** (UI Framework)
- **NumPy & SciPy** (Numerical and Signal Processing)
- **Plotly** (Interactive Visualizations)
- **Pandas** (Data Manipulation)

## 📦 Installation & Usage

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/wams-lite.git
cd wams-lite
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```

## 📊 Data Input Format

The application accepts PMU data in CSV format with the following columns:
- `Time` (s)
- `Frequency` (Hz)
- `Bus ID` (e.g., Bus 1, Bus 2, etc.)

*Note: If no file is uploaded, the system automatically generates a synthetic dataset with oscillations for demonstration.*

## 📂 Project Structure

- `app.py`: Main Streamlit application logic and dashboard.
- `requirements.txt`: Python dependencies.
- `generate_sample.py`: Utility script to generate a sample PMU dataset.
- `sample_pmu_data.csv`: Sample dataset for testing.
- `.gitignore`: Files to ignore in Git.

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
