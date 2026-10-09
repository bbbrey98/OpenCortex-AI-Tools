# OpenCortex AI Tools 🧬

Welcome to the **OpenCortex AI Tools** repository. This collection of tools represents a breakthrough in Sovereign AI architecture, bridging the gap between local generative models, autonomous data generation, and physical robotics (3D Printing / CNC).

## 🚀 Included Tools

### 1. Massive Scientific Dataset Generator (`generate_dataset_100k.py`)
Data is the lifeblood of AI. This algorithmic generator bypasses the need for manual data scraping by synthetically generating **100,000+ flawless scientific examples** (Differential Equations, RLC Circuits, Quantum Physics, dynamic SEIR systems). 
- Generates data dynamically using math engines (SymPy/SciPy).
- Pre-formatted for LLM Fine-Tuning (JSONL format).
- Automatically pushes the generated 100k dataset to Hugging Face.

### 2. Cortex G-Code Generator (`cortex_gcode_generator.py`)
A highly advanced, deterministic parametric 3D CAD engine and slicing bridge.
- **Parametric Generation:** Interprets plain text (e.g., "70mm phone stand") and generates OpenSCAD models dynamically.
- **Spectral Mesh Analysis:** Analyzes the 3D Laplacians of the generated STL to ensure structural coherence.
- **Sovereign Slicing:** Hooks directly into PrusaSlicer via CLI, or falls back to an internal deterministic cross-hatch G-Code generator if offline.

### 3. Sovereign 3D Printer Bridge (`imprimante_bridge.py`)
A robust Marlin V4 bridge designed to control a 3D printer (e.g., Ender 3) locally without cloud dependencies.
- **Direct Serial Streaming:** Sends G-Code line-by-line while parsing temperature telemetry in real-time.
- **Safety First:** Built-in emergency stop capabilities (M112) and temperature fault detection.
- **HTTP API:** Exposes a clean REST API (running on port `7981`) for a web interface to inject speed overrides, temperature changes, or XYZ movements mid-print.

## 🛠️ Usage

### Generate 100k Dataset
```bash
export HF_TOKEN="your_hugging_face_token"
export HF_USERNAME="your_hf_username"
python3 generate_dataset_100k.py
```

### Start the Printer Bridge
```bash
python3 imprimante_bridge.py
```

## 📜 Philosophy
Built for the maker community and AI researchers. 100% Sovereign. 100% Offline capable. No telemetry, no external dependencies required for the core physics engines.
