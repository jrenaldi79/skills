---
name: docx
description: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. When Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"
license: Proprietary. LICENSE.txt has complete terms
---

# DOCX creation, editing, and analysis

## Overview

A user may ask you to create, edit, or analyze the contents of a .docx file. A .docx file is essentially a ZIP archive containing XML files and other resources that you can read or edit. You have different tools and workflows available for different tasks.

## Workflow Decision Tree

### Reading/Analyzing Content
Use "Text extraction" or "Raw XML access" sections below

### Creating New Document
Use "Creating a new Word document" workflow

### Editing Existing Document
- **Your own document + simple changes**
  Use "Basic OOXML editing" workflow

- **Someone else's document**
  Use **"Redlining workflow"** (recommended default)

- **Legal, academic, business, or government docs**
  Use **"Redlining workflow"** (required)

## Reading and analyzing content

### Text extraction
If you just need to read the text contents of a document, you should convert the document to markdown using pandoc. Pandoc provides excellent support for preserving document structure and can show tracked changes:

```bash
# Convert document to markdown with tracked changes
pandoc --track-changes=all path-to-file.docx -o output.md
# Options: --track-changes=accept/reject/all
```

### Raw XML access
You need raw XML access for: comments, complex formatting, document structure, embedded media, and metadata. For any of these features, you'll need to unpack a document and read its raw XML contents.

#### Unpacking a file
`python ooxml/scripts/unpack.py <office_file> <output_directory>`

#### Key file structures
* `word/document.xml` - Main document contents
* `word/comments.xml` - Comments referenced in document.xml
* `word/media/` - Embedded images and media files
* Tracked changes use `<w:ins>` (insertions) and `<w:del>` (deletions) tags

## Creating a new Word document

When creating a new Word document from scratch, use **docx-js**, which allows you to create Word documents using JavaScript/TypeScript.

### Workflow
1. **MANDATORY - READ ENTIRE FILE**: Read [`docx-js.md`](docx-js.md) (~500 lines) completely from start to finish. **NEVER set any range limits when reading this file.** Read the full file content for detailed syntax, critical formatting rules, and best practices before proceeding with document creation.
2. Create a JavaScript/TypeScript file using Document, Paragraph, TextRun components (You can assume all dependencies are installed, but if not, refer to the dependencies section below)
3. Export as .docx using Packer.toBuffer()

## Editing an existing Word document

When editing an existing Word document, use the **Document library** (a Python library for OOXML manipulation). The library automatically handles infrastructure setup and provides methods for document manipulation. For complex scenarios, you can access the underlying DOM directly through the library.

### Workflow
1. **MANDATORY - READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~600 lines) completely from start to finish. **NEVER set any range limits when reading this file.** Read the full file content for the Document library API and XML patterns for directly editing document files.
2. Unpack the document: `python ooxml/scripts/unpack.py <office_file> <output_directory>`
3. Create and run a Python script using the Document library (see "Document Library" section in ooxml.md)
4. Pack the final document: `python ooxml/scripts/pack.py <input_directory> <office_file>`

The Document library provides both high-level methods for common operations and direct DOM access for complex scenarios.

## Redlining workflow for document review

This workflow allows you to plan comprehensive tracked changes using markdown before implementing them in OOXML. **CRITICAL**: For complete tracked changes, you must implement ALL changes systematically.

**Batching Strategy**: Group related changes into batches of 3-10 changes. This makes debugging manageable while maintaining efficiency. Test each batch before moving to the next.

**Principle: Minimal, Precise Edits**
When implementing tracked changes, only mark text that actually changes. Repeating unchanged text makes edits harder to review and appears unprofessional. Break replacements into: [unchanged text] + [deletion] + [insertion] + [unchanged text]. Preserve the original run's RSID for unchanged text by extracting the `<w:r>` element from the original and reusing it.

Example - Changing "30 days" to "60 days" in a sentence:
```python
# BAD - Replaces entire sentence
'<w:del><w:r><w:delText>The term is 30 days.</w:delText></w:r></w:del><w:ins><w:r><w:t>The term is 60 days.</w:t></w:r></w:ins>'

# GOOD - Only marks what changed, preserves original <w:r> for unchanged text
'<w:r w:rsidR="00AB12CD"><w:t>The term is </w:t></w:r><w:del><w:r><w:delText>30</w:delText></w:r></w:del><w:ins><w:r><w:t>60</w:t></w:r></w:ins><w:r w:rsidR="00AB12CD"><w:t> days.</w:t></w:r>'
```

### Tracked changes workflow

1. **Get markdown representation**: Convert document to markdown with tracked changes preserved:
   ```bash
   pandoc --track-changes=all path-to-file.docx -o current.md
   ```

2. **Identify and group changes**: Review the document and identify ALL changes needed, organizing them into logical batches:

   **Location methods** (for finding changes in XML):
   - Section/heading numbers (e.g., "Section 3.2", "Article IV")
   - Paragraph identifiers if numbered
   - Grep patterns with unique surrounding text
   - Document structure (e.g., "first paragraph", "signature block")
   - **DO NOT use markdown line numbers** - they don't map to XML structure

   **Batch organization** (group 3-10 related changes per batch):
   - By section: "Batch 1: Section 2 amendments", "Batch 2: Section 5 updates"
   - By type: "Batch 1: Date corrections", "Batch 2: Party name changes"
   - By complexity: Start with simple text replacements, then tackle complex structural changes
   - Sequential: "Batch 1: Pages 1-3", "Batch 2: Pages 4-6"

3. **Read documentation and unpack**:
   - **MANDATORY - READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~600 lines) completely from start to finish. **NEVER set any range limits when reading this file.** Pay special attention to the "Document Library" and "Tracked Change Patterns" sections.
   - **Unpack the document**: `python ooxml/scripts/unpack.py <file.docx> <dir>`
   - **Note the suggested RSID**: The unpack script will suggest an RSID to use for your tracked changes. Copy this RSID for use in step 4b.

4. **Implement changes in batches**: Group changes logically (by section, by type, or by proximity) and implement them together in a single script. This approach:
   - Makes debugging easier (smaller batch = easier to isolate errors)
   - Allows incremental progress
   - Maintains efficiency (batch size of 3-10 changes works well)

   **Suggested batch groupings:**
   - By document section (e.g., "Section 3 changes", "Definitions", "Termination clause")
   - By change type (e.g., "Date changes", "Party name updates", "Legal term replacements")
   - By proximity (e.g., "Changes on pages 1-3", "Changes in first half of document")

   For each batch of related changes:

   **a. Map text to XML**: Grep for text in `word/document.xml` to verify how text is split across `<w:r>` elements.

   **b. Create and run script**: Use `get_node` to find nodes, implement changes, then `doc.save()`. See **"Document Library"** section in ooxml.md for patterns.

   **Note**: Always grep `word/document.xml` immediately before writing a script to get current line numbers and verify text content. Line numbers change after each script run.

5. **Pack the document**: After all batches are complete, convert the unpacked directory back to .docx:
   ```bash
   python ooxml/scripts/pack.py unpacked reviewed-document.docx
   ```

6. **Final verification**: Do a comprehensive check of the complete document:
   - Convert final document to markdown:
     ```bash
     pandoc --track-changes=all reviewed-document.docx -o verification.md
     ```
   - Verify ALL changes were applied correctly:
     ```bash
     grep "original phrase" verification.md  # Should NOT find it
     grep "replacement phrase" verification.md  # Should find it
     ```
   - Check that no unintended changes were introduced


## Converting Documents to Images

To visually analyze Word documents, convert them to images using a two-step process:

1. **Convert DOCX to PDF**:
   ```bash
   soffice --headless --convert-to pdf document.docx
   ```

2. **Convert PDF pages to JPEG images**:
   ```bash
   pdftoppm -jpeg -r 150 document.pdf page
   ```
   This creates files like `page-1.jpg`, `page-2.jpg`, etc.

Options:
- `-r 150`: Sets resolution to 150 DPI (adjust for quality/size balance)
- `-jpeg`: Output JPEG format (use `-png` for PNG if preferred)
- `-f N`: First page to convert (e.g., `-f 2` starts from page 2)
- `-l N`: Last page to convert (e.g., `-l 5` stops at page 5)
- `page`: Prefix for output files

Example for specific range:
```bash
pdftoppm -jpeg -r 150 -f 2 -l 5 document.pdf page  # Converts only pages 2-5
```

## Code Style Guidelines
**IMPORTANT**: When generating code for DOCX operations:
- Write concise code
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements

## Dependencies

Required dependencies (install if not available):

- **pandoc**: `sudo apt-get install pandoc` (for text extraction)
- **docx**: `npm install -g docx` (for creating new documents)
- **LibreOffice**: `sudo apt-get install libreoffice` (for PDF conversion)
- **Poppler**: `sudo apt-get install poppler-utils` (for pdftoppm to convert PDF to images)
- **defusedxml**: `pip install defusedxml` (for secure XML parsing)
## Converting Markdown to Branded Word Documents

When converting markdown reports to branded Word documents, use a systematic approach with quality verification to ensure completeness.

### Workflow Decision Tree

**For simple conversion (no branding):**
1. Use pandoc: `pandoc input.md -o output.docx`
2. Quick and preserves basic structure

**For branded conversion (custom colors, fonts, logos):**
1. **Small documents (<100 lines):** Use docx-js manual coding
2. **Large documents (100+ lines):** Use python-docx systematic conversion

### Complete Markdown Conversion Workflow

**CRITICAL RULE:** For documents >100 lines, NEVER manually select content. Use systematic parsing.

#### Step 1: Source Assessment
```bash
# Count lines in source markdown
wc -l source.md

# Identify structure
grep -E '^#{1,6}' source.md | wc -l  # Count headings
grep -E '^\|' source.md | wc -l     # Count table rows
```

#### Step 2: Choose Conversion Method

**For documents >100 lines, use python-docx:**

```python
# Create virtual environment
python3 -m venv /path/to/.tmp/venv
source /path/to/.tmp/venv/bin/activate
pip install python-docx pillow

# Systematic conversion script
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor

# Read entire markdown
with open('source.md', 'r') as f:
    lines = f.readlines()

# Process line by line
for i, line in enumerate(lines):
    # Handle headings, tables, bullets, etc.
    # See example below
```

#### Step 3: Quality Verification (MANDATORY)

**Completeness Checklist:**

```bash
# 1. Line count comparison
SOURCE_LINES=$(wc -l < source.md)
echo "Source has $SOURCE_LINES lines"

# 2. Heading count verification
SOURCE_H1=$(grep -c '^# ' source.md)
SOURCE_H2=$(grep -c '^## ' source.md)
echo "Source: $SOURCE_H1 H1 headings, $SOURCE_H2 H2 headings"
# Manually verify output has same counts

# 3. Table count verification
SOURCE_TABLES=$(grep -c '^|.*|.*|' source.md)
echo "Source has ~$SOURCE_TABLES table rows"

# 4. File size comparison
ls -lh source.md output.docx
# Docx should be larger due to formatting
# If docx is smaller than markdown, investigate
```

**Red Flags:**
- Word document smaller than markdown file
- Missing section headings from source
- Significant line count discrepancy
- Missing tables or code blocks

#### Step 4: Content Verification

```bash
# Convert Word back to markdown for comparison
pandoc output.docx -o verification.md

# Check for missing sections
diff <(grep '^## ' source.md) <(grep '^## ' verification.md)

# Spot check critical content
grep "important phrase" verification.md
```

### Example: Complete Python-Docx Conversion

```python
import re
import base64
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Brand colors
COLORS = {
    'primary': RGBColor(0x86, 0x52, 0xFF),  # Purple
    'text': RGBColor(0x33, 0x33, 0x33)       # Gray
}

# Read markdown
with open('source.md', 'r') as f:
    md_content = f.read()

# Load logo if needed
with open('logo.txt', 'r') as f:
    logo_base64 = f.read().strip()
    logo_bytes = base64.b64decode(logo_base64)

# Create document
doc = Document()

# Set default font
style = doc.styles['Normal']
style.font.name = 'Arial'
style.font.size = Pt(11)
style.font.color.rgb = COLORS['text']

# Add header with logo
section = doc.sections[0]
header = section.header
header_para = header.paragraphs[0]
header_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
header_run = header_para.add_run()
header_run.add_picture(BytesIO(logo_bytes), width=Inches(2.0))

# Parse markdown systematically
lines = md_content.split('\n')
print(f"Processing {len(lines)} lines...")

i = 0
in_table = False
table_data = []

while i < len(lines):
    line = lines[i].rstrip()
    
    # Handle tables
    if line.startswith('|'):
        if not in_table:
            in_table = True
            table_data = []
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        # Skip separator rows
        if not all(c.replace('-','').strip()=='' for c in cells):
            table_data.append(cells)
        i += 1
        continue
    elif in_table:
        # Create table
        if table_data:
            table = doc.add_table(rows=len(table_data), 
                                cols=len(table_data[0]))
            table.style = 'Light Grid Accent 1'
            for r_idx, row in enumerate(table_data):
                for c_idx, cell_text in enumerate(row):
                    cell = table.rows[r_idx].cells[c_idx]
                    cell.text = cell_text
                    if r_idx == 0:  # Header row
                        cell.paragraphs[0].runs[0].font.bold = True
            doc.add_paragraph()  # Space after table
        in_table = False
        table_data = []
    
    # Handle headings
    if line.startswith('# ') and not line.startswith('## '):
        p = doc.add_heading(line[2:], level=1)
        p.runs[0].font.color.rgb = COLORS['primary']
    elif line.startswith('## '):
        p = doc.add_heading(line[3:], level=2)
        p.runs[0].font.color.rgb = COLORS['primary']
    elif line.startswith('### '):
        p = doc.add_heading(line[4:], level=3)
    
    # Handle bullets
    elif line.startswith('- '):
        doc.add_paragraph(line[2:], style='List Bullet')
    
    # Handle blockquotes
    elif line.startswith('> '):
        p = doc.add_paragraph(line[2:])
        p.paragraph_format.left_indent = Inches(0.5)
        p.runs[0].font.italic = True
    
    # Handle regular paragraphs
    elif line.strip():
        p = doc.add_paragraph()
        # Process markdown bold/italic
        parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', line)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                run = p.add_run(part[2:-2])
                run.font.bold = True
            elif part.startswith('*') and part.endswith('*'):
                run = p.add_run(part[1:-1])
                run.font.italic = True
            elif part:
                p.add_run(part)
    
    i += 1

print(f"Processed {i} lines total")

# Save
doc.save('output.docx')
print("Saved to output.docx")
```

### Quality Verification After Conversion

**MANDATORY checks before delivery:**

1. **Line Count Match:**
   - Source markdown lines = Lines processed by script
   - If mismatch, investigate what was skipped

2. **Section Completeness:**
   ```bash
   # Extract all headings from source
   grep -E '^#{1,4} ' source.md > source_headings.txt
   
   # Convert output back and extract headings
   pandoc output.docx -o temp.md
   grep -E '^#{1,4} ' temp.md > output_headings.txt
   
   # Compare
   diff source_headings.txt output_headings.txt
   ```

3. **Table Count:**
   - Count tables in source markdown
   - Verify same number in Word document

4. **File Size Sanity Check:**
   - Word document should be larger than markdown (due to formatting)
   - If Word is smaller, content is likely missing

5. **Spot Check Critical Content:**
   ```bash
   # Check for presence of key sections
   pandoc output.docx -o check.md
   grep "Executive Summary" check.md
   grep "Conclusion" check.md
   grep "References" check.md
   ```

### Common Mistakes to Avoid

1. **Manual Content Selection:** Don't cherry-pick "highlights" - convert everything
2. **Scope Underestimation:** Count lines before starting; use appropriate method
3. **No Verification:** Always verify completeness before delivery
4. **Assuming Completeness:** Just because script runs doesn't mean all content converted
5. **Ignoring File Size:** Significant size discrepancy indicates missing content

### When to Use Each Approach

| Source Size | Branding | Method | Verification |
|-------------|----------|--------|-------------|
| <50 lines | No | pandoc | Visual check |
| <50 lines | Yes | docx-js manual | Count headings |
| 50-100 lines | Yes | docx-js manual | Full checklist |
| 100+ lines | Yes | python-docx systematic | **MANDATORY full checklist** |
| 500+ lines | Yes | python-docx systematic | **MANDATORY + diff check** |

### Recovery from Incomplete Conversion

If you discover incomplete conversion:

1. **Acknowledge the gap:** Count what's missing
2. **Root cause analysis:** Why was content excluded?
3. **Use systematic approach:** Python-docx line-by-line processing
4. **Verify completeness:** Run full checklist
5. **Replace incomplete version:** Delete partial document, deliver complete one

