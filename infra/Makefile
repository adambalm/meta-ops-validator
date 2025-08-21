.PHONY: venv install test demo gui
venv:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
install:
	pip install -r requirements.txt
test:
	pytest -q || true
demo:
	python -m metaops.cli report --in runs --out diagnostic/report.html
gui:
	streamlit run streamlit_app.py