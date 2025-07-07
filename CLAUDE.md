# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
```bash
# Run tests (if/when tests are added)
uv run pytest

# Run tests with coverage
uv run pytest --cov
```

### Code Quality
```bash
# Format code
uv run ruff format .

# Lint code  
uv run ruff check .

# Fix linting issues
uv run ruff check . --fix
```

### Installation & Running
```bash
# Install in development mode
uv pip install -e .

# Run directly with uv
uv run heyzine_dl.py <URL>

# Run installed CLI
heyzine-dl <URL>
```

## Architecture Overview

### Single-File Design
The entire application is contained in `heyzine_dl.py` following the single-script pattern of tools like `youtube-dl`. This design choice prioritizes:
- Simplicity and ease of distribution
- Self-contained functionality
- Easy inspection and modification

### Core Architecture
```
HeyzineExtractor class (heyzine_dl.py:60-283)
├── extract_info() - Parse HTML and extract PDF metadata
├── format_filename() - Handle output template formatting  
├── download_pdf() - Download with progress tracking
├── process_url() - Main processing pipeline
└── run() - Handle batch processing and CLI flow

main() function (heyzine_dl.py:284+)
├── Argument parsing with argparse
├── Logging setup with colored output
└── HeyzineExtractor instantiation and execution
```

### Key Technical Insights

**Metadata Extraction Strategy**: Uses regex to parse JavaScript configuration objects embedded in HTML rather than browser automation:
```python
# Core metadata extraction pattern in extract_info()
cfg_pattern = r'var flipbookcfg\s*=\s*(\{[^}]+\});'
pdf_pattern = r'"name"\s*:\s*"([^"]+\.pdf)"'
```

**Fallback URL Strategy**: Tries multiple CDN endpoints since Heyzine uses different URL patterns:
```python
info['pdf_urls'] = [
    f"{cdn_base}/flip-book/pdf/{pdf_filename}",
    f"{cdn_base}/files/uploaded/{pdf_filename}",
]
```

**Template System**: Implements youtube-dl style filename templating with variables like `%(title)s`, `%(id)s`, `%(pdf_filename)s`.

## Code Conventions

- **Logging**: Uses structured logging with colored output via `ColorFormatter` class
- **Error Handling**: Comprehensive try/catch with optional verbose tracebacks  
- **HTTP Handling**: Single `requests.Session` for connection reuse and proxy support
- **CLI Patterns**: Follows youtube-dl conventions for option naming and behavior

## Dependencies & Packaging

- **Core Dependency**: Only `requests>=2.31.0` for HTTP operations
- **Development Tools**: pytest, ruff (formatter/linter), pytest-cov  
- **Package Manager**: Supports both `uv` (preferred) and traditional `pip`
- **Python Versions**: 3.8+ compatibility maintained

## Important Implementation Notes

- **No Tests Currently**: Test structure is configured in pyproject.toml but no tests exist yet
- **Single Module**: All code in one file following youtube-dl pattern
- **Progress Display**: Custom progress bars for downloads without external dependencies  
- **Filename Sanitization**: Built-in ASCII restriction and special character handling
- **Session Management**: Reuses HTTP connections and supports proxy configurationTesting private workflow
Testing private-only functionality properly!
