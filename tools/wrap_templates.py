import os
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / 'templates'
EXCLUDE = {'base.html', 'header.html', 'footer_fragment.html', 'footer.html', 'categories_select_box.html'}

changed = []
for p in TEMPLATES_DIR.glob('*.html'):
    name = p.name
    if name in EXCLUDE:
        continue
    text = p.read_text(encoding='utf-8')
    if "{% extends" in text:
        continue
    # Backup
    bak = p.with_suffix(p.suffix + '.bak')
    bak.write_text(text, encoding='utf-8')
    new = []
    new.append("{% extends 'base.html' %}\n")
    new.append("{% block content %}\n")
    new.append(text)
    new.append("\n{% endblock %}\n")
    p.write_text(''.join(new), encoding='utf-8')
    changed.append(name)

print('Wrapped templates:', changed)
