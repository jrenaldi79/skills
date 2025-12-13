# Skills for Claude

A collection of skills that extend Claude's capabilities with specialized knowledge, workflows, and tool integrations.

## What are Skills?

Skills are modular, self-contained packages that transform Claude from a general-purpose assistant into a specialized agent equipped with:

- **Specialized workflows** - Multi-step procedures for specific domains
- **Tool integrations** - Instructions for working with file formats, APIs, and systems
- **Domain expertise** - Company-specific knowledge, schemas, and business logic
- **Bundled resources** - Scripts, references, and assets for complex tasks

## Repository Structure

```
skills/
├── README.md
├── LICENSE
├── skill-creator/          # Skill development toolkit
├── windows-onboarding/     # Windows setup automation
├── docx/                   # Word document processing
├── pptx/                   # PowerPoint creation
├── deep-research/          # Research report generation
├── life360-brand/          # Life360 brand guidelines
├── life360-email-generator/# Life360 email templates
└── web-sentiment-monitor/  # Sentiment analysis
```

Each skill directory contains:
- `SKILL.md` - Main skill documentation with YAML frontmatter
- `scripts/` - Executable Python/bash scripts (optional)
- `references/` - Reference documentation (optional)
- `assets/` - Templates, images, fonts (optional)

## Available Skills

### Core Skills

#### skill-creator
Guide for creating effective skills. Use when you want to create a new skill or update an existing one to extend Claude's capabilities.

**Use for:** Skill development, skill packaging, skill validation

#### windows-onboarding
Onboards new Windows users by adapting the system prompt to their machine. Collects user information and generates personalized system prompts with correct Windows paths. Includes automated Google Drive setup.

**Use for:** Setting up new Windows users, migrating skills to new machines

### Document Processing

#### docx
Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction.

**Use for:** Creating/editing Word documents, working with tracked changes, adding comments

#### pptx
PowerPoint creation and editing capabilities including slides, shapes, charts, tables, and HTML to PowerPoint conversion.

**Use for:** Creating presentations, editing slides, converting HTML to PowerPoint

### Specialized Skills

#### deep-research
Conduct comprehensive, evidence-based research reports following a rigorous multi-step process. Leverages parallel web searching and deep content extraction.

**Use for:** In-depth research, thorough analysis of complex topics, investigative reports

#### life360-brand
Official brand guidelines for Life360, including color palettes, typography, logo assets, UI layout principles, and photography style.

**Use for:** Designing Life360 emails, creating branded content, ensuring brand compliance

#### life360-email-generator
Automatically generates on-brand HTML emails for Life360 corporate communications with embedded brand assets.

**Use for:** Creating Life360 marketing emails, corporate announcements

#### web-sentiment-monitor
Monitors web sentiment and media coverage for brands, products, or topics. Tracks mentions, sentiment trends, and media analysis.

**Use for:** Brand monitoring, sentiment analysis, media tracking

## Installation

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jrenaldi79/skills.git ~/skills
   ```

2. **Or download specific skills:**
   ```bash
   mkdir -p ~/skills
   cd ~/skills
   # Download individual skill directories you need
   git clone --depth 1 --filter=blob:none --sparse https://github.com/jrenaldi79/skills.git temp
   cd temp
   git sparse-checkout set skill-creator docx
   cp -r skill-creator docx ../
   cd .. && rm -rf temp
   ```

3. **Use the skills:**
   - Skills are now available in your skills directory
   - Claude will automatically discover and use them when appropriate

### Setting Up Skills Directory

**macOS/Linux:**
```bash
mkdir -p ~/skills
mkdir -p ~/skills/.tmp
mkdir -p ~/skills/deliverables
```

**Windows:**
```powershell
mkdir C:\Users\{YourUsername}\skills
mkdir C:\Users\{YourUsername}\skills\.tmp
mkdir C:\Users\{YourUsername}\skills\deliverables
```

## Usage

Once skills are installed, Claude automatically:

1. **Discovers skills** - Reads skill metadata to understand capabilities
2. **Matches requests** - Maps your requests to appropriate skills
3. **Loads skills** - Loads skill instructions when needed
4. **Executes workflows** - Follows skill procedures and uses bundled resources

### Example Interactions

**Using docx skill:**
```
"Create a professional document with tracked changes enabled"
```

**Using deep-research skill:**
```
"Research the latest developments in quantum computing and write a comprehensive report"
```

**Using skill-creator:**
```
"Create a new skill for analyzing financial data"
```

## Creating Your Own Skills

Use the `skill-creator` skill to build new skills:

1. **Initialize a skill:**
   ```bash
   python scripts/init_skill.py my-skill-name --path ~/skills
   ```

2. **Edit the skill:**
   - Update `SKILL.md` with instructions
   - Add scripts, references, or assets as needed

3. **Package the skill:**
   ```bash
   python scripts/package_skill.py ~/skills/my-skill-name
   ```

See the `skill-creator` skill for detailed guidance.

## Skill Anatomy

Each skill contains:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/          - Executable code
    ├── references/       - Documentation
    └── assets/           - Templates, images, etc.
```

## System Requirements

- **Python 3.7+** (for script-based skills)
- **MCP-compatible Claude interface** (Claude Desktop, API, etc.)
- **Operating System:** Windows 10+, macOS 10.15+, or Linux

## Contributing

Contributions welcome! To contribute a skill:

1. Fork this repository
2. Create your skill using `skill-creator`
3. Test thoroughly
4. Submit a pull request with:
   - The packaged `.skill` file
   - Brief description of what it does
   - Example use cases

## License

Individual skills may have their own licenses. Check each skill's LICENSE.txt file for details.

## Support

For issues or questions:
- Open an issue in this repository
- Check individual skill documentation in `SKILL.md` files

## Skill Registry

When using Claude with these skills, add them to your system prompt's Skills Registry:

```markdown
### skill-name
- **name:** skill-name
- **description:** [from skill's YAML frontmatter]
```

The `windows-onboarding` skill can automate this process for new setups.
