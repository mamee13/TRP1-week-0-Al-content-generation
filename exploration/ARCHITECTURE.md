# 🏗️ System Architecture: AI Content Generation Framework

The `ai-content` package is designed with a modular, extensible architecture that separates core orchestration from provider-specific implementation details.

## 🧩 Core Components

### 1. `ProviderRegistry` (`src/ai_content/core/registry.py`)
The heart of the framework uses a **registration pattern** to decouple the core logic from specific AI vendors.
- **Dynamic Discovery**: Providers register themselves via high-level decorators (e.g., `@ProviderRegistry.register_music("kie")`).
- **Lazy Loading**: Providers are instantiated only when requested, saving resources and avoiding unnecessary environment validation.

### 2. Standardization Protocols (`src/ai_content/core/provider.py`)
All providers must adhere to strictly defined protocols (`MusicProvider`, `VideoProvider`, `ImageProvider`). This ensures that the CLI and internal pipelines can interact with any provider using a unified interface.

### 3. Unified Result Model (`src/ai_content/core/result.py`)
The `GenerationResult` object standardizes API responses across all vendors, containing:
- `success`: Boolean status.
- `file_path`: Path to the local media asset.
- `data`: Binary content of the generated media.
- `metadata`: Provider-specific debug information (e.g., Task IDs, URLs).

## 🚀 Orchestration Layer

### Pipelines (`src/ai_content/pipelines/`)
Pipelines manage multi-step generation workflows. For example, the `FullContentPipeline` coordinates:
1. Source metadata retrieval.
2. Parallel music and image generation.
3. Video synthesis from images.
4. Media merging via FFmpeg.

### Job Tracking (`src/ai_content/core/job_tracker.py`)
A SQLite-backed persistence layer manages long-running (asynchronous) tasks.
- **MD5 De-duplication**: Prevents redundant expensive API calls by hashing prompts and presets.
- **State Synchronization**: Polling mechanisms verify task completion and trigger final downloads.

## ⚙️ Configuration & CLI

### Settings Management (`src/ai_content/config/settings.py`)
Built on **Pydantic Settings**, providing:
- Automated `.env` file loading.
- Type-safe validation for API keys and base URLs.
- Global defaults for timeouts and polling intervals.

### CLI Interface (`src/ai_content/cli/`)
Powered by **Typer**, providing a user-friendly entry point for:
- One-off generations.
- Multi-provider comparisons.
- Job status management.
- Preset listing.
