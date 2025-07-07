#!/usr/bin/env python3
"""
heyzine_dl - Command-line tool to download Heyzine flipbooks
Following patterns from youtube-dl and gallery-dl
"""

import re
import sys
import json
import argparse
import requests
from pathlib import Path
from urllib.parse import urlparse, unquote
import logging
from typing import Optional, Dict, List

__version__ = "1.0.0"

# Configure logging
class ColorFormatter(logging.Formatter):
    """Colored log formatter"""
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    FORMATS = {
        logging.DEBUG: grey + "%(message)s" + reset,
        logging.INFO: "%(message)s",
        logging.WARNING: yellow + "%(message)s" + reset,
        logging.ERROR: red + "%(message)s" + reset,
        logging.CRITICAL: bold_red + "%(message)s" + reset
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logging(verbosity: int = 0, quiet: bool = False):
    """Setup logging based on verbosity level"""
    if quiet:
        level = logging.ERROR
    elif verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
        
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter())
    
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers = [handler]
    
    return logger


class HeyzineDownloader:
    """Downloads Heyzine flipbooks"""
    
    def __init__(self, args):
        self.args = args
        self.logger = logging.getLogger()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'heyzine_dl/{__version__} (+https://github.com/user/heyzine_dl)'
        })
        
        if args.proxy:
            self.session.proxies = {
                'http': args.proxy,
                'https': args.proxy
            }
            
    def extract_info(self, url: str) -> Dict:
        """Extract flipbook information from URL"""
        self.logger.debug(f"Fetching: {url}")
        
        response = self.session.get(url)
        response.raise_for_status()
        
        # Look for the flipbookcfg variable
        cfg_pattern = r'var\s+flipbookcfg\s*=\s*({[\s\S]+?});[\s]*(?:/\*|var)'
        cfg_match = re.search(cfg_pattern, response.text, re.DOTALL)
        
        if not cfg_match:
            raise ValueError("Could not find flipbook configuration")
            
        # Extract PDF filename
        pdf_pattern = r'"name"\s*:\s*"([^"]+\.pdf)"'
        pdf_match = re.search(pdf_pattern, cfg_match.group(1))
        
        if not pdf_match:
            raise ValueError("Could not find PDF filename")
            
        pdf_filename = pdf_match.group(1)
        
        # Extract metadata
        info = {
            'url': url,
            'pdf_filename': pdf_filename,
            'title': None,
            'num_pages': None,
            'id': None,
            'uploader': 'heyzine',
            'extractor': 'heyzine:flipbook'
        }
        
        # Extract additional metadata
        patterns = {
            'id': r'"id"\s*:\s*"([^"]+)"',
            'num_pages': r'"num_pages"\s*:\s*(\d+)',
            'title': r'"title"\s*:\s*"([^"]*)"',
            'custom_name': r'"custom_name"\s*:\s*"([^"]+)"'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, cfg_match.group(1))
            if match:
                value = match.group(1)
                if key == 'num_pages':
                    value = int(value)
                info[key] = value
                
        # Set title from custom_name if no title
        if not info['title'] and info.get('custom_name'):
            info['title'] = Path(info['custom_name']).stem
            
        # Construct PDF URLs
        cdn_base = "https://cdnc.heyzine.com"
        info['pdf_urls'] = [
            f"{cdn_base}/flip-book/pdf/{pdf_filename}",
            f"{cdn_base}/files/uploaded/{pdf_filename}",
        ]
        
        return info
        
    def format_filename(self, template: str, info: Dict) -> str:
        """Format filename using template and info dict"""
        # Default template
        if not template:
            template = "%(title)s-%(id)s.%(ext)s"
            
        # Replace template variables
        replacements = {
            '%(title)s': info.get('title', 'flipbook'),
            '%(id)s': info.get('id', 'unknown'),
            '%(uploader)s': info.get('uploader', 'heyzine'),
            '%(ext)s': 'pdf',
            '%(pdf_filename)s': Path(info.get('pdf_filename', 'download.pdf')).stem,
        }
        
        filename = template
        for key, value in replacements.items():
            filename = filename.replace(key, str(value))
            
        # Clean filename
        if self.args.restrict_filenames:
            # Remove non-ASCII and unsafe characters
            filename = re.sub(r'[^\w\s.-]', '_', filename)
            filename = re.sub(r'\s+', '_', filename)
            
        return filename
        
    def download_pdf(self, info: Dict, output_path: str) -> bool:
        """Download PDF from URLs"""
        for pdf_url in info['pdf_urls']:
            try:
                self.logger.info(f"[download] Downloading: {pdf_url}")
                
                # Check if file exists
                if Path(output_path).exists() and self.args.no_overwrites:
                    self.logger.warning(f"[download] {output_path} already exists")
                    return True
                    
                response = self.session.get(pdf_url, stream=True)
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('Content-Type', '')
                if 'pdf' not in content_type.lower():
                    self.logger.debug(f"Not a PDF: {content_type}")
                    continue
                    
                # Download with progress
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if not self.args.quiet and total_size > 0:
                                progress = (downloaded / total_size) * 100
                                size_mb = total_size / 1024 / 1024
                                down_mb = downloaded / 1024 / 1024
                                print(f"\r[download] {progress:5.1f}% of {size_mb:.2f}MiB at {down_mb:.2f}MiB", 
                                      end='', flush=True)
                                      
                if not self.args.quiet:
                    print()  # New line after progress
                    
                self.logger.info(f"[download] Saved as: {output_path}")
                return True
                
            except requests.exceptions.RequestException as e:
                self.logger.debug(f"Failed: {e}")
                continue
                
        return False
        
    def process_url(self, url: str):
        """Process a single URL"""
        try:
            # Extract information
            if self.args.dump_json or self.args.get_url:
                info = self.extract_info(url)
                
                if self.args.dump_json:
                    print(json.dumps(info, indent=2))
                    return
                    
                if self.args.get_url:
                    for pdf_url in info['pdf_urls']:
                        print(pdf_url)
                    return
                    
            # Download
            info = self.extract_info(url)
            
            # Format output filename
            if self.args.output:
                output_path = self.args.output
            else:
                filename = self.format_filename(self.args.output_template, info)
                output_path = filename
                
            # Print info if verbose
            if self.args.verbose:
                self.logger.info(f"[info] Title: {info.get('title', 'N/A')}")
                self.logger.info(f"[info] Pages: {info.get('num_pages', 'N/A')}")
                self.logger.info(f"[info] ID: {info.get('id', 'N/A')}")
                
            # Simulate mode
            if self.args.simulate:
                self.logger.info(f"[simulate] Would download to: {output_path}")
                return
                
            # Download the PDF
            if not self.download_pdf(info, output_path):
                raise Exception("Failed to download from all URLs")
                
        except Exception as e:
            self.logger.error(f"[error] {url}: {e}")
            if self.args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
            
    def run(self):
        """Run the downloader"""
        urls = []
        
        # Get URLs from arguments or batch file
        if self.args.batch_file:
            with open(self.args.batch_file, 'r') as f:
                urls.extend(line.strip() for line in f if line.strip() and not line.startswith('#'))
        else:
            urls.append(self.args.url)
            
        # Process each URL
        for i, url in enumerate(urls, 1):
            if len(urls) > 1:
                self.logger.info(f"[{i}/{len(urls)}] Processing: {url}")
            self.process_url(url)


def main():
    parser = argparse.ArgumentParser(
        prog='heyzine_dl',
        description='Download Heyzine flipbooks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s https://heyzine.com/flip-book/example.html
  %(prog)s -o mybook.pdf https://heyzine.com/flip-book/example.html
  %(prog)s --get-url https://heyzine.com/flip-book/example.html
  %(prog)s -a urls.txt
'''
    )
    
    # General options
    general = parser.add_argument_group('General Options')
    general.add_argument('url', nargs='?', help='Heyzine flipbook URL')
    general.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    # Download options
    download = parser.add_argument_group('Download Options')
    download.add_argument('-a', '--batch-file', metavar='FILE',
                         help='File containing URLs to download ("-" for stdin)')
    download.add_argument('--proxy', metavar='URL',
                         help='Use the specified HTTP/HTTPS proxy')
    download.add_argument('-s', '--simulate', action='store_true',
                         help='Do not download the PDF')
    download.add_argument('-g', '--get-url', action='store_true',
                         help='Simulate, quiet but print URL')
    download.add_argument('-j', '--dump-json', action='store_true',
                         help='Simulate, quiet but print JSON information')
                         
    # Filesystem options
    filesystem = parser.add_argument_group('Filesystem Options')
    filesystem.add_argument('-o', '--output', metavar='FILE',
                           help='Output filename')
    filesystem.add_argument('--output-template', metavar='TEMPLATE',
                           default='%(title)s-%(id)s.%(ext)s',
                           help='Output filename template (default: %%(title)s-%%(id)s.%%(ext)s)')
    filesystem.add_argument('--restrict-filenames', action='store_true',
                           help='Restrict filenames to only ASCII characters')
    filesystem.add_argument('-w', '--no-overwrites', action='store_true',
                           help='Do not overwrite files')
                           
    # Verbosity options
    verbosity = parser.add_argument_group('Verbosity Options')
    verbosity.add_argument('-q', '--quiet', action='store_true',
                          help='Activate quiet mode')
    verbosity.add_argument('-v', '--verbose', action='count', default=0,
                          help='Print various debugging information')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.url and not args.batch_file:
        parser.error('You must provide either URL or --batch-file')
        
    if args.url and 'heyzine.com' not in args.url:
        parser.error('URL must be from heyzine.com')
        
    # Setup logging
    setup_logging(args.verbose, args.quiet)
    
    # Run downloader
    downloader = HeyzineDownloader(args)
    downloader.run()


if __name__ == '__main__':
    main()