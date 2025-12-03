# coding: utf-8

import pandas as pd
import os

# ## Escape special characters for YAML
html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
}

def html_escape(text):
    if isinstance(text, str):
        return "".join(html_escape_table.get(c, c) for c in text)
    return "False"

# ## Create a slug from the title
def generate_slug(title):
    return title.lower().replace(" ", "-")

# ## Ensure unique filename
def get_unique_filename(base_path, base_filename):
    index = 1
    filename = base_filename
    while os.path.exists(os.path.join(base_path, filename)):
        filename = f"{base_filename}-{index}.md"
        index += 1
    return filename

# ## Creating the markdown files
output_dir = "../_talks/"
os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists

talks = pd.read_csv("talks.tsv", sep="\t", header=0)

for _, item in talks.iterrows():
    # Validate date format
    if not isinstance(item.date, str) or len(item.date) != 7 or "-" not in item.date:
        raise ValueError(f"Invalid date format '{item.date}'. Expected 'YYYY-MM'.")
    
    # Generate URL slug from title
    url_slug = generate_slug(item.title)

    # Base markdown filename
    base_md_filename = f"{item.date}-{url_slug}.md"
    md_filename = get_unique_filename(output_dir, base_md_filename)
    html_filename = md_filename.replace(".md", "")
    year = item.date[:4]

    # Start building the markdown content
    md = "---\n"
    md += f'title: "{html_escape(item.title)}"\n'
    md += "collection: talks\n"
    md += f'type: "{item.type if isinstance(item.type, str) and len(item.type) > 3 else "Talk"}"\n'
    md += f"permalink: /talks/{html_filename}\n"

    if isinstance(item.venue, str) and len(item.venue) > 3:
        md += f'venue: "{html_escape(item.venue)}"\n'

    if isinstance(item.date, str) and len(item.date) == 7:
        md += f"date: {item.date}-01\n"

    if isinstance(item.location, str) and len(item.location) > 3:
        md += f'location: "{html_escape(item.location)}"\n'

    if isinstance(item.talk_url, str) and len(item.talk_url) > 3:
        md += f'talkurl: {item.talk_url}\n'

    md += "---\n"

    if isinstance(item.description, str) and len(item.description) > 3:
        md += f"\n{html_escape(item.description)}\n"

    # Write to file
    md_filepath = os.path.join(output_dir, md_filename)
    with open(md_filepath, 'w') as f:
        f.write(md)

print("Markdown files successfully generated!")
