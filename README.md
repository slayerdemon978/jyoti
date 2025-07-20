# PDF Outline Extractor - Adobe India Hackathon Challenge 1A

A pure Python solution for extracting structured outlines from PDF documents without using ML models.

## Problem Statement

Extract structured outlines (Title, H1, H2, H3 headings) from PDF documents and output them in JSON format with hierarchy and page numbers.

## Solution Approach

This solution uses pure Python logic with the following strategies:

### 1. Text Extraction
- Uses `pdftotext` (from poppler-utils) to extract text with layout preservation
- Maintains page-by-page structure for accurate page number mapping

### 2. Heading Detection
- **Pattern Matching**: Identifies numbered sections (1., 1.1, 1.1.1, etc.)
- **Keyword Recognition**: Detects common heading keywords (Introduction, Conclusion, etc.)
- **Format Analysis**: Recognizes ALL CAPS and Title Case formatting
- **Context Analysis**: Uses surrounding text to improve accuracy

### 3. Heading Level Classification
- **H1**: Main sections, chapters, numbered sections (1., 2., etc.)
- **H2**: Subsections with two-level numbering (1.1, 2.1, etc.)
- **H3**: Sub-subsections with three-level numbering (1.1.1, 2.1.1, etc.)

### 4. Title Extraction
- Searches first few pages for document title
- Filters out copyright notices, headers, and metadata
- Prioritizes prominent text that appears early in the document

## Features

- ✅ **No ML Models**: Pure Python logic using text patterns and heuristics
- ✅ **Fast Processing**: Optimized for speed (< 10 seconds for 50-page PDFs)
- ✅ **Multilingual Support**: Unicode-aware text processing
- ✅ **Robust Error Handling**: Graceful failure with empty results
- ✅ **Docker Compatible**: AMD64 architecture support
- ✅ **Offline Operation**: No internet connectivity required

## Installation & Setup

### Option 1: Using Virtual Environment (Recommended for Development)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd jyoti
   git checkout solution-branch
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install system dependencies:**
   ```bash
   # On Ubuntu/Debian:
   sudo apt-get update
   sudo apt-get install poppler-utils

   # On macOS:
   brew install poppler

   # On Windows:
   # Download and install poppler from: https://poppler.freedesktop.org/
   ```

4. **Test the solution:**
   ```bash
   # Create test directories
   mkdir -p input output
   
   # Copy a test PDF to input directory
   cp "jyoti/Challenge - 1(a)/Datasets/Pdfs/E0CCG5S312.pdf" input/
   
   # Run the extractor
   python process_pdfs.py
   
   # Check the output
   cat output/E0CCG5S312.json
   ```

### Option 2: Using Docker (Production/Submission)

1. **Build the Docker image:**
   ```bash
   docker build --platform linux/amd64 -t pdf-outline-extractor:latest .
   ```

2. **Run the container:**
   ```bash
   docker run --rm \
     -v $(pwd)/input:/app/input \
     -v $(pwd)/output:/app/output \
     --network none \
     pdf-outline-extractor:latest
   ```

## Usage

### Input
- Place PDF files in the `/app/input` directory (or `input/` for local testing)
- Supports PDFs up to 50 pages
- Multiple PDFs can be processed in batch

### Output
- JSON files are generated in `/app/output` directory (or `output/` for local testing)
- Each `filename.pdf` generates a corresponding `filename.json`

### Output Format
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    },
    {
      "level": "H2", 
      "text": "Background",
      "page": 2
    },
    {
      "level": "H3",
      "text": "Historical Context",
      "page": 3
    }
  ]
}
```

## Algorithm Details

### Heading Detection Patterns

1. **Numbered Sections**: `1.`, `1.1`, `1.1.1`, etc.
2. **Chapter Keywords**: `Chapter 1`, `Section 2`, etc.
3. **Roman Numerals**: `I.`, `II.`, `III.`, etc.
4. **Alphabetic Sections**: `A.`, `B.`, `C.`, etc.
5. **Standard Headings**: Table of Contents, References, etc.
6. **Formatting Cues**: ALL CAPS, Title Case

### Level Classification Logic

```python
# H1: Main sections
- Single number (1., 2., 3.)
- Chapter/Part keywords
- Major document sections

# H2: Subsections  
- Two-level numbering (1.1, 2.1)
- Subsection keywords
- Secondary headings

# H3: Sub-subsections
- Three-level numbering (1.1.1, 2.1.1)
- Detailed subsections
- Tertiary headings
```

## Performance Characteristics

- **Speed**: < 10 seconds for 50-page PDFs
- **Memory**: Low memory footprint (< 100MB)
- **Model Size**: N/A (no models used)
- **Architecture**: AMD64 compatible
- **Dependencies**: Only poppler-utils (lightweight)

## Testing

Test with the provided sample files:

```bash
# Test with sample PDFs
cp "jyoti/Challenge - 1(a)/Datasets/Pdfs/"*.pdf input/
python process_pdfs.py

# Compare with expected outputs
diff output/E0CCG5S312.json "jyoti/Challenge - 1(a)/Datasets/Output.json/E0CCG5S312.json"
```

## Limitations & Considerations

1. **Font-based Detection**: Does not rely on font sizes (as recommended in challenge)
2. **Layout Dependent**: Works best with well-structured PDFs
3. **Language Support**: Optimized for English but supports Unicode
4. **Complex Layouts**: May struggle with highly complex multi-column layouts

## Dependencies

- **Python 3.10+**
- **poppler-utils** (for pdftotext)
- **Standard Library Only**: No external Python packages required

## File Structure

```
jyoti/
├── process_pdfs.py          # Main extraction logic
├── Dockerfile               # Container configuration
├── README.md               # This file
├── input/                  # Input PDFs (create for testing)
├── output/                 # Output JSON files (created automatically)
└── jyoti/
    └── Challenge - 1(a)/
        ├── Datasets/       # Sample data
        ├── process_pdfs.py # Original boilerplate
        └── Dockerfile      # Original dockerfile
```

## Contributing

This solution is designed for the Adobe India Hackathon Challenge 1A. The approach prioritizes:

1. **Accuracy**: High precision in heading detection
2. **Speed**: Fast processing for competition requirements  
3. **Simplicity**: Pure Python without ML complexity
4. **Robustness**: Handles various PDF formats and structures

## License

This project is created for the Adobe India Hackathon Challenge 1A.