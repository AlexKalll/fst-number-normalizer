# FST Text Normalizer

Text Normalization Challenge - English cardinal numbers (0–1000).

FST-based text normalization system for English cardinal numbers with Python fallback.

## What This Project Does

Normalizes cardinal numbers (0-1000) in English text:
- "I have 3 dogs and 21 cats" -> "I have three dogs and twenty-one cats"
- "She is 45 years old." -> "She is forty-five years old."

## File Structure

```
fst-number-normalizer/
├── src/
│   ├── normalize.py          # Main normalizer (FST + fallback)
│   ├── grammar.pynini         # FST grammar source
│   └── grammar.far            # Compiled FAR file (generated)
├── scripts/
│   └── compile_grammar.py     # Compile grammar to FAR
├── tests/
│   └── test_basic.py          # Unit tests
├── report/
│   └── report.md              # Methodology report
├── requirements.txt
└── README.md
```

## Quick Start

### Clone the repository
```bash
git clone https://github.com/AlexKalll/fst-number-normalizer.git
cd fst-number-normalizer
```

### Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate # for Linux
# or for Windows
# python -m venv venv
# venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Normalizer

Works without Pynini (uses Python fallback):

```bash
python src/normalize.py "I have 21 cats and 3 dogs."
# Output: I have twenty-one cats and three dogs.
```

### Compile Grammar 

```bash
python scripts/compile_grammar.py
```

Generates `src/grammar.far` for FST-based normalization. Compilation time: < 1 second.

### Run Tests

```bash
pytest tests -v # or python -m pytest
# -v is better to see results in detail.
```

## Usage

**Command Line:**
```bash
python src/normalize.py "She is 45 years old."
# Output: She is forty-five years old.
```

**Python API:**
```python
from src.normalize import normalize_text
result = normalize_text("The number is 999.")
print(result)  # "The number is nine hundred ninety-nine."
```

## Features

- Supports numbers 0-1000
- Correct hyphenation (twenty-one, forty-five)
- Proper spacing for hundreds (one hundred one)
- Preserves text structure
- FST-based (when Pynini available) or Python fallback
- Comprehensive unit tests

## Grammar Design

Handles: units (0-9), teens (10-19), tens (20-90), two-digit with hyphenation (21-99), hundreds (100-999), and special case 1000. See `report/report.md` for details.

## Requirements

- Python 3.8+
- pytest (for testing)
- pynini ( for FST normalization)