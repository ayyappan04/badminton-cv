# Badminton CV (Project In Progress 🚧)

![Project Status](https://img.shields.io/badge/Status-In%20Progress-yellow)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)

A comprehensive Computer Vision and AI system for analyzing badminton matches. This project extracts player movements, shuttle trajectories, and generating professional coaching reports using LLMs (Google Gemini).

## 🚀 Features

*   **Video Ingestion**: Efficiently processes match videos in chunks.
*   **Court Calibration**: Automatically detects court lines and maps pixels to real-world meters.
*   **Object Detection**: Uses **YOLOv8** to detect players and (experimentally) shuttlecocks.
*   **Motion Tracking**: Implements **BoT-SORT** for persistent player tracking.
*   **Pose Estimation**: Analyzes player biomechanics using **YOLOv8-pose** (17 keypoints).
*   **Event Detection**: Automatically identifies rallies, shots (Smashes, Clears), and points.
*   **Analytics**: Computes speed (km/h), distance covered, and court coverage.
*   **AI Coach**: Uses **RAG (Retrieval Augmented Generation)** and **Google Gemini 2.5** to generate personalized coaching advice based on match data.
*   **Web Dashboard**: A modern Dark/Neon UI (React + FastAPI) to upload videos and view results.

## 🛠️ Stack

*   **Core**: Python 3.9+, OpenCV, PyTorch, NumPy
*   **AI/ML**: Ultralytics YOLOv8, SentenceTransformers
*   **LLM**: Google Gemini API (via `google-generativeai`)
*   **Backend**: FastAPI, Uvicorn
*   **Frontend**: React, Vite, TailwindCSS, Lucide Icons

## 📦 Installation

### Prerequisites
*   Python 3.9 or higher
*   Node.js & npm
*   Google Gemini API Key

### 1. Clone Repository
```bash
git clone https://github.com/ayyappan04/badminton-cv.git
cd badminton-cv
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### 3. Frontend Setup
```bash
cd web-ui
npm install
cd ..
```

## 🖥️ Usage

### Running the Web App (Recommended)
You need two terminal windows:

**Terminal 1 (Backend)**:
```bash
# Starts API server on http://localhost:8000
PYTHONPATH=. python src/web/app.py
```

**Terminal 2 (Frontend)**:
```bash
# Starts UI on http://localhost:3000 (typ.)
cd web-ui
npm run dev
```

Visit the URL shown in Terminal 2 to use the app.

### Running CLI Analysis
To analyze a video file directly from the terminal:
```bash
PYTHONPATH=. python src/main.py analyze data/test/my_match.mp4
```

## 🏗️ Project Status (In Progress)
- [x] Core Pipeline (Ingest, Detect, Track, Pose)
- [x] Basic Event Detection (Heuristic)
- [x] AI Report Generation
- [x] Web Interface
- [ ] **Advanced Shuttlecock Detection**: Training a custom YOLO model (Phase 10).
- [ ] **Shot Classification Model**: Upgrading from heuristics to LSTM/Transformers.
- [ ] **3D Trajectory Reconstruction**.

## 🤝 Contributing
This project is currently under active development. Feel free to open issues or submit PRs!

## 📄 License
MIT License
