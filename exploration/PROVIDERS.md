# 🔌 AI Providers: Detailed Analysis

The framework supports a diverse set of AI vendors, each catering to specific modalities and quality requirements.

## 🎵 Music & Audio

### 1. Google Lyria
- **Modality**: Instrumental music generation.
- **Key Feature**: High-fidelity 16-bit PCM 44.1kHz Stereo output.
- **Challenge**: Streams raw binary data without RIFF headers.
- **Our Solution**: Automated WAV header injection in the post-processing layer.

### 2. AIMLAPI (MiniMax 2.0)
- **Modality**: Complete songs with vocals.
- **Key Feature**: Integration with lyrics text files and complex structure tags (e.g., `[Intro]`, `[Chorus]`).
- **Limitation**: High latency (5-10 minutes per generation), managed via our background `JobTracker`.

## 🎬 Video Generation

### 1. Google Veo
- **Capability**: Cinematic high-resolution video snippets.
- **Protocol**: Leverages the latest `google-genai` SDK.
- **Refinement**: Patched SDK method name changes (`generate_videos` vs legacy `generate_video`).

### 2. Kling AI
- **Capability**: State-of-the-art motion consistency and physics.
- **Architecture**: Deep polling system with periodic status synchronization.
- **Security**: Complex dual-key (API Key + Secret) signature requirements.

### 3. Kie AI (New Integration)
- **Capability**: Unified API for cutting-edge models (Veo 3.1, Runway Gen-3).
- **Benefit**: Simplifies the video stack into a single interface.
- **Implementation**: Robust null-safe result parsing and automatic quality parameter injection.

## 🖼️ Image Generation

### 1. Google Imagen 3
- **Focus**: High-fidelity photorealistic and artistic images.
- **Integration**: Native base for the framework's image-to-video pipelines.

## 🔑 Authentication & Secrets
The system uses a centralized `Settings` class to securely map environment variables from `.env` to provider instances:
- `GEMINI_API_KEY` → Google GenAI
- `KIEAI_API_KEY` → Kie AI
- `AIMLAPI_KEY` → AIMLAPI (MiniMax)
- `KLINGAI_API_KEY`/`SECRET` → Kling AI
