# heyzine-dl

Command-line tool to download Heyzine flipbooks as PDF files.

## Features

- **Direct PDF download** - Extracts original PDF from Heyzine's CDN
- **Batch processing** - Download multiple URLs from a file
- **Output templates** - Customize filenames like youtube-dl
- **Progress display** - Shows download progress with file size
- **JSON metadata** - Export flipbook information
- **Proxy support** - Download through HTTP/HTTPS proxies
- **No browser required** - Simple and fast

## Installation

### Using uv (Recommended)

```bash
# Install and run directly
uv run heyzine_dl.py https://heyzine.com/flip-book/example.html

# Or install globally
uv pip install .
heyzine-dl https://heyzine.com/flip-book/example.html
```

### Using pip

```bash
# Install dependencies
pip install -r requirements.txt

# Run the script
python heyzine_dl.py https://heyzine.com/flip-book/example.html
```

### Using pipx

```bash
# Install globally in isolated environment
pipx install .
heyzine-dl https://heyzine.com/flip-book/example.html
```

## Usage

### Basic Examples

```bash
# Download with default filename
heyzine-dl https://heyzine.com/flip-book/example.html

# Specify output filename
heyzine-dl -o "My Book.pdf" https://heyzine.com/flip-book/example.html

# Use custom filename template
heyzine-dl --output-template "%(title)s.%(ext)s" https://heyzine.com/flip-book/example.html

# Get PDF URL without downloading
heyzine-dl --get-url https://heyzine.com/flip-book/example.html

# Export metadata as JSON
heyzine-dl --dump-json https://heyzine.com/flip-book/example.html

# Download multiple URLs from file
heyzine-dl -a urls.txt

# Quiet mode (errors only)
heyzine-dl -q https://heyzine.com/flip-book/example.html

# Verbose mode (debug info)
heyzine-dl -v https://heyzine.com/flip-book/example.html
```

### Advanced Options

```bash
# Use proxy
heyzine-dl --proxy http://proxy.example.com:8080 https://heyzine.com/flip-book/example.html

# Don't overwrite existing files
heyzine-dl -w https://heyzine.com/flip-book/example.html

# Restrict filenames to ASCII characters
heyzine-dl --restrict-filenames https://heyzine.com/flip-book/example.html

# Simulate (don't download)
heyzine-dl -s https://heyzine.com/flip-book/example.html
```

## Command Line Options

```
General Options:
  url                   Heyzine flipbook URL
  -h, --help            Show help message
  --version             Show version number

Download Options:
  -a, --batch-file      File containing URLs to download
  --proxy URL           Use the specified HTTP/HTTPS proxy
  -s, --simulate        Do not download the PDF
  -g, --get-url         Print URL without downloading
  -j, --dump-json       Print JSON information

Filesystem Options:
  -o, --output          Output filename
  --output-template     Output filename template (default: %(title)s-%(id)s.%(ext)s)
  --restrict-filenames  Restrict filenames to ASCII characters
  -w, --no-overwrites   Do not overwrite files

Verbosity Options:
  -q, --quiet           Activate quiet mode
  -v, --verbose         Print debugging information (-vv for more)
```

## Output Template Variables

You can use these variables in `--output-template`:

- `%(title)s` - Flipbook title
- `%(id)s` - Flipbook ID
- `%(pdf_filename)s` - Original PDF filename (without extension)
- `%(ext)s` - File extension (always 'pdf')
- `%(uploader)s` - Always 'heyzine'

Example: `--output-template "%(uploader)s-%(title)s-%(id)s.%(ext)s"`

## How It Works

1. Fetches the Heyzine flipbook page
2. Extracts metadata containing the original PDF filename
3. Constructs CDN URLs where PDFs are stored
4. Downloads the PDF directly - no browser automation needed!

## Legal Notice & Disclaimer

### Intended Use
This tool is intended for:
- Downloading your own content
- Archiving purchased materials you have legitimate access to
- Content explicitly allowed for personal use

**Please respect copyright laws and only download content you have permission to save offline.**

### Disclaimer of Warranties
This software is provided "as is" without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. The authors are not responsible for any misuse of this tool or any legal consequences that may arise from its use.

### Limitation of Liability
In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

### User Responsibility
Users are solely responsible for ensuring their use of this tool complies with applicable laws, terms of service, and copyright regulations. The authors do not endorse or encourage any violation of terms of service or copyright law.

## Development

```bash
# Clone the repository
git clone https://github.com/scgreenhalgh/heyzine-dl.git
cd heyzine-dl

# Install in development mode with uv
uv pip install -e .

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary
- ✅ **Commercial use** - You can use this software for commercial purposes
- ✅ **Modification** - You can modify the source code
- ✅ **Distribution** - You can distribute the software
- ✅ **Private use** - You can use the software privately
- ❗ **License and copyright notice** - You must include the license and copyright notice with the software

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## Support

If you encounter any issues or have questions:
1. Check the existing [GitHub Issues](https://github.com/scgreenhalgh/heyzine-dl/issues)
2. Create a new issue if your problem isn't already covered
3. Provide detailed information about your environment and the issue

## Acknowledgments

- Inspired by [youtube-dl](https://github.com/ytdl-org/youtube-dl) and [gallery-dl](https://github.com/mikf/gallery-dl)
- Built with Python and the [requests](https://docs.python-requests.org/) library