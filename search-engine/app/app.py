import argparse
import logging
from fastapi import FastAPI, Path as FastAPIPath, Request
import pathlib as pl
from pathlib import Path

from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
from uvicorn import run

from engine import SearchEngine


script_dir = pl.Path(__file__).resolve().parent
templates_path = script_dir / "templates"
static_path = script_dir / "static"

app = FastAPI()
engine = SearchEngine()
templates = Jinja2Templates(directory=str(templates_path))

app.mount('/static', StaticFiles(directory=str(static_path)), name='static')

def get_top_names(scores_dict: dict, n: int):
    sorted_names = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
    top_n_names = sorted_names[:n]
    top_n_dict = dict(top_n_names)

    return top_n_dict

def get_research_papers(papers_dir: str) -> list[dict]:
    papers = []
    try:
        dir_path = pl.Path(papers_dir)
        if not dir_path.exists():
            logging.warning(f"Papers directory not found: {papers_dir}")
            return papers
            
        for folder in dir_path.iterdir():
            if folder.is_dir():
                try:
                    paper = {
                        'name': folder.name,
                        'pdf': next(folder.glob('*.pdf')),
                        'summary_md': next(folder.glob('summary_*.md')),
                        'summary_pdf': next(folder.glob('summary_*.pdf'))
                    }
                    papers.append(paper)
                except StopIteration:
                    logging.warning(f"Missing files in folder: {folder}")
                except Exception as e:
                    logging.error(f"Error processing folder {folder}: {e}")
    except Exception as e:
        logging.error(f"Error accessing papers directory: {e}")
    
    return papers


@app.get('/', response_class=HTMLResponse)
async def search(request: Request):
    papers = engine.papers
    return templates.TemplateResponse(
        'search.html', {'request': request, 'papers': papers}
    )

@app.get('/results/{query}', response_class=HTMLResponse)
async def search_results(request: Request, query: str = FastAPIPath(...)):
    papers_dir = "/home/swayam/Downloads/Clean Cookstove PDFS/Processed Research Papers"
    results = engine.search(query)
    top_results = get_top_names(results, n=10)
    
    # Get all papers once and create mapping
    papers = {p['name']: p for p in get_research_papers(papers_dir)}
    
    # Enrich results using paper mapping
    enriched_results = []
    for name, score in top_results.items():
        if name in papers:
            paper = papers[name]
            enriched_results.append({
                'name': name,
                'score': score,
                'pdf': paper['pdf'],
                'summary_md': paper['summary_md'],
                'summary_pdf': paper['summary_pdf']
            })
    
    return templates.TemplateResponse(
        "results.html", {
            "request": request,
            "query": query,
            "results": enriched_results,
            "total_results": len(enriched_results)
        })

@app.get('/papers')
async def list_papers(request: Request):
    papers_dir = "/home/swayam/Downloads/Clean Cookstove PDFS/Processed Research Papers"
    papers = get_research_papers(papers_dir)
    return templates.TemplateResponse(
        "papers.html",
        {"request": request, "papers": papers}
    )


# file serving route
@app.get('/papers/{folder}/{filename}')
async def serve_paper(
    folder: str = FastAPIPath(...),
    filename: str = FastAPIPath(...)
):
    papers_dir = "/home/swayam/Downloads/Clean Cookstove PDFS/Processed Research Papers"
    file_path = pl.Path(papers_dir) / folder / filename
    if not file_path.exists():
        return {"error": "File not found"}, 404
    return FileResponse(str(file_path))


@app.get("/about")
def read_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    data = pd.read_parquet(args.data_path)
    content = list(zip(data["name"].values, data["content"].values))

    engine.bulk_index(content)

    run(app, host="127.0.0.1", port=8000)
