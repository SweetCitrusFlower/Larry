import markdown
from fpdf import FPDF
import os
import urllib.request

def test_pdf():
    text = """
# Titlu Principal
Acesta este un text cu **bold** și *italic*.
- Punctul 1
- Punctul 2

```python
print("Salut")
```
"""
    html = markdown.markdown(text, extensions=['fenced_code'])
    
    pdf = FPDF()
    pdf.add_page()
    
    # Fonts
    base_url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/"
    fonts = {
        '': 'Roboto-Regular.ttf',
        'B': 'Roboto-Bold.ttf',
        'I': 'Roboto-Italic.ttf'
    }
    for style, fname in fonts.items():
        if not os.path.exists(fname):
            urllib.request.urlretrieve(base_url + fname, fname)
        pdf.add_font("Roboto", style=style, fname=fname)
        
    pdf.set_font("Roboto", size=12)
    pdf.write_html(html)
    pdf.output("test.pdf")
    print("Succes")

if __name__ == "__main__":
    test_pdf()
