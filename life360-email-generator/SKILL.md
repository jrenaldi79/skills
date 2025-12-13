---
name: life360-email-generator
description: Automatically generates on-brand HTML emails for Life360 corporate communications. Supports standard lifestyle emails and "The Loop" CEO/All Hands communications.
---

# Life360 Email Generator

This skill creates production-ready HTML emails using the "Visual Card" aesthetic defined in the brand guidelines. It supports multiple templates for different communication needs.

## Capabilities
-   **Embedded Assets:** Uses pre-verified, Base64-encoded logos and headers. No dead links.
-   **Responsive Design:** Fully tested table-based layout for Gmail and Outlook.
-   **Customizable:** Accepts headline, body text, and CTA links.
-   **Templates:**
    -   `lifestyle` (Default): Standard external/internal communications with lifestyle photography header.
    -   `the_loop`: CEO and All Hands communications with specific branding.

## Usage

To generate an email, run the python script:

```bash
python3 /Users/john_renaldi/skills/life360-email-generator/scripts/generate_email.py   --headline "Welcome to the Team"   --body "<p>We are thrilled to have you...</p>"   --cta_text "View Onboarding"   --cta_link "https://life360.com/welcome"   --output /path/to/email.html   --template lifestyle
```

### Arguments
- `--headline`: The main title of the email.
- `--body`: HTML content for the email body.
- `--cta_text`: Text for the call-to-action button.
- `--cta_link`: URL for the call-to-action button.
- `--output`: Path where the generated HTML file will be saved.
- `--template`: Choose `lifestyle` (default) or `the_loop`.

## Assets
-   **Logo:** Horizontal Wordmark (Transparent PNG)
-   **Header (Lifestyle):** "Teens Connecting" (3.3:1 Crop, Retina JPEG)
-   **Header (The Loop):** Designated CEO/All Hands graphic
