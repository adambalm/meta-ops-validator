from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from metaops.validators.onix_xsd import validate_xsd
from metaops.validators.onix_schematron import validate_schematron
from metaops.validators.presence import score_presence
from metaops.rules.engine import evaluate as eval_rules
from metaops.reporters.csv_writer import write_csv
from metaops.reporters.json_writer import write_json
from metaops.reporters.html_summary import render_summary

app = typer.Typer(add_completion=False)
console = Console()

@app.command("validate-xsd")
def cmd_validate_xsd(
    onix: Path = typer.Option(..., exists=True, readable=True),
    xsd: Path = typer.Option(..., exists=True, readable=True),
    out_json: Optional[Path] = typer.Option(None),
    out_csv: Optional[Path] = typer.Option(None),
):
    rows = validate_xsd(onix, xsd)
    console.print(f"[green]XSD checked[/]: {len(rows)} issues")
    if out_json: write_json(rows, out_json)
    if out_csv: write_csv(rows, out_csv)
    else: console.print_json(data=rows)

@app.command("validate-schematron")
def cmd_validate_schematron(
    onix: Path = typer.Option(..., exists=True, readable=True),
    sch: Path = typer.Option(..., exists=True, readable=True),
    out_json: Optional[Path] = typer.Option(None),
    out_csv: Optional[Path] = typer.Option(None),
):
    rows = validate_schematron(onix, sch)
    console.print(f"[green]Schematron checked[/]: {len(rows)} findings")
    if out_json: write_json(rows, out_json)
    if out_csv: write_csv(rows, out_csv)
    else: console.print_json(data=rows)

@app.command("run-rules")
def cmd_run_rules(
    onix: Path = typer.Option(..., exists=True, readable=True),
    rules: Path = typer.Option(..., exists=True, readable=True),
    out_json: Optional[Path] = typer.Option(None),
    out_csv: Optional[Path] = typer.Option(None),
):
    rows = eval_rules(onix, rules)
    console.print(f"[cyan]Rules evaluated:[/] {len(rows)} findings")
    if out_json: write_json(rows, out_json)
    if out_csv: write_csv(rows, out_csv)
    else: console.print_json(data=rows)

@app.command("score-presence")
def cmd_score_presence(
    inputs: Path = typer.Option(..., exists=True, readable=True),
    out_json: Optional[Path] = typer.Option(None),
    out_csv: Optional[Path] = typer.Option(None),
):
    rows = score_presence(inputs)
    console.print(f"[yellow]Presence scored[/]: {len(rows)} titles")
    if out_json: write_json(rows, out_json)
    if out_csv: write_csv(rows, out_csv)
    else: console.print_json(data=rows)

@app.command("report")
def cmd_report(
    inp: Path = typer.Option(..., exists=True, readable=True, help="Folder with *.json"),
    out: Path = typer.Option(..., help="HTML output file"),
    template: Path = typer.Option(Path("docs/templates/summary.html.j2"), exists=False),
):
    if not template.exists():
        template.parent.mkdir(parents=True, exist_ok=True)
        template.write_text(
            "<html><body><h1>MetaOps Diagnostic</h1>"
            "{% for ds in data_sets %}<h3>{{ds.name}}</h3>"
            "<pre>{{ds.rows | tojson}}</pre>{% endfor %}</body></html>",
            encoding="utf-8"
        )
    render_summary(inp, template, out)
    console.print(f"[magenta]Rendered[/] {out}")

if __name__ == "__main__":
    app()