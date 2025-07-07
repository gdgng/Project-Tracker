import os
import webview
from markdown import markdown

def create_html_from_readme():
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        return "<h2>README.md not found</h2>"

    with open(readme_path, encoding="utf-8") as f:
        md_content = f.read()

    # Markdown → HTML met extra ondersteuning
    html_body = markdown(md_content, extensions=["extra", "codehilite", "tables"])

    # Corrigeer afbeeldingspaden naar absolute file://-pad
    screens_abs = os.path.abspath("screens").replace("\\", "/") + "/"
    html_body = html_body.replace('src="screens/', f'src="file:///{screens_abs}')

    # Volledige HTML met kop en stijl
    css_path = os.path.abspath("style.css").replace("\\", "/")
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>README - Crypto Price Tracker V1.5</title>
        <link rel="stylesheet" href="file:///{css_path}">
    </head>
    <body>
    {html_body}
    </body>
    </html>
    """

    # Schrijf naar tijdelijk bestand
    html_path = os.path.join(os.getcwd(), "temp_readme.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    return html_path

if __name__ == "__main__":
    html_file = create_html_from_readme()
    webview.create_window("README.md Viewer", f"file:///{html_file.replace(os.sep, '/')}", width=900, height=700)
    webview.start()
