from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from metaops.validators.onix_xsd import validate_xsd
from metaops.validators.onix_schematron import validate_schematron
from metaops.validators.presence import score_presence
from metaops.validators.nielsen_scoring import calculate_nielsen_score
from metaops.validators.retailer_profiles import calculate_retailer_score, calculate_multi_retailer_score, RETAILER_PROFILES
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

@app.command("nielsen-score")
def cmd_nielsen_score(
    onix: Path = typer.Option(..., exists=True, readable=True),
    out_json: Optional[Path] = typer.Option(None),
):
    score_data = calculate_nielsen_score(onix)
    console.print(f"[blue]Nielsen Score[/]: {score_data['overall_score']}%")
    console.print(f"[yellow]Sales Impact[/]: {score_data['sales_impact_estimate']}")
    if score_data.get('missing_critical'):
        console.print(f"[red]Missing Critical[/]: {', '.join(score_data['missing_critical'][:5])}")

    if out_json:
        write_json([score_data], out_json)
    else:
        console.print_json(data=score_data)

@app.command("validate-full")
def cmd_validate_full(
    onix: Path = typer.Option(..., exists=True, readable=True),
    out_json: Optional[Path] = typer.Option(None),
    out_csv: Optional[Path] = typer.Option(None),
    skip_nielsen: bool = typer.Option(False, help="Skip Nielsen completeness scoring"),
):
    """Run complete validation pipeline: XSD → Schematron → Rules → Nielsen Score"""
    all_results = []

    console.print(f"[cyan]Running full validation pipeline for[/]: {onix.name}")

    # Step 1: XSD Validation
    console.print("[1/4] XSD validation...")
    xsd_results = validate_xsd(onix)
    all_results.extend(xsd_results)
    console.print(f"  XSD: {len(xsd_results)} findings")

    # Step 2: Schematron Validation
    console.print("[2/4] Schematron validation...")
    sch_results = validate_schematron(onix)
    all_results.extend(sch_results)
    console.print(f"  Schematron: {len(sch_results)} findings")

    # Step 3: Custom Rules
    console.print("[3/4] Custom rules evaluation...")
    rules_results = eval_rules(onix)
    all_results.extend(rules_results)
    console.print(f"  Rules: {len(rules_results)} findings")

    # Step 4: Nielsen Scoring
    if not skip_nielsen:
        console.print("[4/4] Nielsen completeness scoring...")
        nielsen_data = calculate_nielsen_score(onix)
        nielsen_result = {
            "line": 1,
            "level": "INFO",
            "domain": "NIELSEN_SCORE",
            "type": "scoring",
            "message": f"Nielsen completeness score: {nielsen_data['overall_score']}%",
            "path": onix.name,
            "nielsen_data": nielsen_data
        }
        all_results.append(nielsen_result)
        console.print(f"  Nielsen Score: {nielsen_data['overall_score']}%")

    console.print(f"\n[green]Pipeline complete[/]: {len(all_results)} total findings")

    # Count by severity
    errors = len([r for r in all_results if r.get('level') == 'ERROR'])
    warnings = len([r for r in all_results if r.get('level') == 'WARNING'])
    infos = len([r for r in all_results if r.get('level') == 'INFO'])

    console.print(f"  Errors: {errors} | Warnings: {warnings} | Info: {infos}")

    if out_json:
        write_json(all_results, out_json)
    if out_csv:
        write_csv(all_results, out_csv)
    if not out_json and not out_csv:
        console.print_json(data=all_results)

@app.command("retailer-score")
def cmd_retailer_score(
    onix: Path = typer.Option(..., exists=True, readable=True),
    retailer: str = typer.Option(..., help="Retailer profile (amazon, ingram, apple, kobo, barnes_noble, overdrive)"),
    out_json: Optional[Path] = typer.Option(None),
):
    """Score metadata completeness for specific retailer requirements."""
    if retailer not in RETAILER_PROFILES:
        console.print(f"[red]Error[/]: Unknown retailer '{retailer}'")
        console.print(f"Available profiles: {', '.join(RETAILER_PROFILES.keys())}")
        return

    score_data = calculate_retailer_score(onix, retailer)

    if 'error' in score_data:
        console.print(f"[red]Error[/]: {score_data['error']}")
        return

    console.print(f"[blue]{score_data['retailer']} Score[/]: {score_data['overall_score']}%")
    console.print(f"[yellow]Risk Level[/]: {score_data['risk_level']}")
    console.print(f"[cyan]Compliance[/]: {score_data['compliance_status']}")

    if score_data.get('critical_missing'):
        console.print(f"[red]Critical Missing[/]: {', '.join(score_data['critical_missing'][:5])}")

    if score_data.get('recommendations'):
        console.print(f"[green]Top Recommendation[/]: {score_data['recommendations'][0]}")

    if out_json:
        write_json([score_data], out_json)
    else:
        console.print_json(data=score_data)

@app.command("multi-retailer")
def cmd_multi_retailer(
    onix: Path = typer.Option(..., exists=True, readable=True),
    retailers: str = typer.Option("amazon,ingram,apple", help="Comma-separated retailer list"),
    out_json: Optional[Path] = typer.Option(None),
):
    """Compare metadata completeness across multiple retailers."""
    retailer_list = [r.strip() for r in retailers.split(',')]

    # Validate retailer names
    invalid_retailers = [r for r in retailer_list if r not in RETAILER_PROFILES]
    if invalid_retailers:
        console.print(f"[red]Error[/]: Unknown retailers: {', '.join(invalid_retailers)}")
        console.print(f"Available profiles: {', '.join(RETAILER_PROFILES.keys())}")
        return

    comparison_data = calculate_multi_retailer_score(onix, retailer_list)

    if 'error' in comparison_data:
        console.print(f"[red]Error[/]: {comparison_data['error']}")
        return

    console.print(f"[cyan]Multi-Retailer Analysis[/]: {comparison_data['retailers_analyzed']} retailers")
    console.print(f"[blue]Average Score[/]: {comparison_data['average_score']}%")
    console.print(f"[green]Best Fit[/]: {comparison_data['best_fit_retailer']} ({comparison_data['best_fit_score']}%)")
    console.print(f"[yellow]Worst Fit[/]: {comparison_data['worst_fit_retailer']} ({comparison_data['worst_fit_score']}%)")

    if comparison_data.get('common_gaps'):
        console.print(f"[red]Common Gaps[/]: {', '.join(comparison_data['common_gaps'][:5])}")

    console.print(f"[magenta]Recommendation[/]: {comparison_data['recommendation']}")

    if out_json:
        write_json([comparison_data], out_json)
    else:
        console.print_json(data=comparison_data)

@app.command("web")
def cmd_web(
    port: int = typer.Option(8502, help="Port to run web interface on"),
):
    """Launch the web interface for interactive validation."""
    import subprocess
    import sys
    from pathlib import Path

    # Get the path to the streamlit app
    app_path = Path(__file__).parent.parent / "web" / "streamlit_app.py"

    console.print(f"[cyan]Starting web interface on port {port}...[/]")
    console.print(f"[yellow]Access at:[/] http://100.111.114.84:{port}")

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(app_path),
            "--server.port", str(port),
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        console.print("\n[yellow]Web interface stopped[/]")

@app.command("dashboard")
def cmd_dashboard(
    port: int = typer.Option(8503, help="Port to run dashboard on"),
):
    """Launch the analytics dashboard for batch processing."""
    import subprocess
    import sys
    from pathlib import Path

    # Get the path to the dashboard app
    app_path = Path(__file__).parent.parent / "web" / "dashboard.py"

    console.print(f"[cyan]Starting analytics dashboard on port {port}...[/]")
    console.print(f"[yellow]Access at:[/] http://100.111.114.84:{port}")
    console.print(f"[blue]Features:[/] Batch processing, charts, export reports")

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(app_path),
            "--server.port", str(port),
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped[/]")

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
