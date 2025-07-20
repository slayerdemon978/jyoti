#!/usr/bin/env python3
"""
Debug script to find the missing heading
"""

import subprocess
import re

def debug_pdf():
    # Extract text with page breaks
    result = subprocess.run(
        ['pdftotext', '-layout', '-f', '1', 'input/E0CCG5S312.pdf', '-'],
        capture_output=True,
        text=True,
        check=True
    )
    
    text = result.stdout
    pages = text.split('\f')  # Form feed character separates pages
    
    for page_num, page_content in enumerate(pages):
        if page_content.strip():
            lines = [line.rstrip() for line in page_content.split('\n')]
            
            for line in lines:
                if "1. Introduction to the Foundation Level Extensions" in line:
                    print(f"Found on page {page_num}: '{line.strip()}'")
                    print(f"Context (5 lines before and after):")
                    line_idx = lines.index(line)
                    for i in range(max(0, line_idx-5), min(len(lines), line_idx+6)):
                        marker = ">>>" if i == line_idx else "   "
                        print(f"{marker} {i:2d}: '{lines[i]}'")
                    return

if __name__ == "__main__":
    debug_pdf()