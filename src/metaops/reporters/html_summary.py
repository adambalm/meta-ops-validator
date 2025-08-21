from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json

def render_summary(runs_dir: Path, template_path: Path, out_html: Path):
    runs_dir.mkdir(parents=True, exist_ok=True)
    data_sets = []
    for p in runs_dir.glob("*.json"):
        try:
            data_sets.append({"name": p.name, "rows": json.loads(p.read_text())})
        except Exception:
            pass
    env = Environment(loader=FileSystemLoader(str(template_path.parent)),
                      autoescape=select_autoescape())
    tpl = env.get_template(template_path.name)
    html = tpl.render(data_sets=data_sets)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html, encoding="utf-8")