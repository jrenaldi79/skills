import argparse
from pathlib import Path

# Configuration - environment agnostic via relative paths
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_ROOT / 'assets'
TEMPLATES_DIR = SKILL_ROOT / 'templates'

def load_asset(filename):
    with open(ASSETS_DIR / filename, 'r') as f:
        return f.read().strip()

def generate_email(headline, body, cta_text, cta_link, output_file, template_name='lifestyle'):
    # Determine configuration based on template name
    if template_name == 'the_loop':
        header_filename = 'header_the_loop.txt'
        template_filename = 'the_loop.html'
    else:
        header_filename = 'header_lifestyle.txt'
        template_filename = 'visual_card.html'

    # Load Base64 Assets
    try:
        logo_b64 = load_asset('logo_transparent.txt')
        header_b64 = load_asset(header_filename)
    except FileNotFoundError:
        print(f"Error: Assets not found. Please ensure logo_transparent.txt and {header_filename} exist in assets/ folder.")
        return

    # Load Template
    try:
        with open(TEMPLATES_DIR / template_filename, 'r') as f:
            template = f.read()
    except FileNotFoundError:
        print(f"Error: Template {template_filename} not found.")
        return

    # Replace Placeholders
    html = template.replace('{{ LOGO_B64 }}', logo_b64)
    html = html.replace('{{ HEADER_B64 }}', header_b64)
    html = html.replace('{{ HEADLINE }}', headline)
    html = html.replace('{{ BODY_CONTENT }}', body)
    html = html.replace('{{ TITLE }}', headline)
    html = html.replace('{{ CTA_TEXT }}', cta_text)
    html = html.replace('{{ CTA_LINK }}', cta_link)

    # Write Output
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Email generated successfully using '{template_name}' template: {output_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a Life360 HTML Email')
    parser.add_argument('--headline', required=True, help='Main header text')
    parser.add_argument('--body', required=True, help='HTML body content (paragraphs)')
    parser.add_argument('--cta_text', default='Learn More', help='Button text')
    parser.add_argument('--cta_link', default='#', help='Button URL')
    parser.add_argument('--output', required=True, help='Output HTML file path')
    parser.add_argument('--template', choices=['lifestyle', 'the_loop'], default='lifestyle', help='Email template style')

    args = parser.parse_args()
    generate_email(args.headline, args.body, args.cta_text, args.cta_link, args.output, args.template)
