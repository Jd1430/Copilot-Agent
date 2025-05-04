# app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.llm.query_handler import translate_nl_to_query, explain_result_with_gemini
from app.db.mongodb_handler import run_mongo_query
import json

app = FastAPI()

# CORS (safe for dev; restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask")
async def ask_database(request: Request):
    data = await request.json()
    nl_query = data.get("query", "")

    if not nl_query:
        return JSONResponse({"error": "No query provided"}, status_code=400)

    try:
        mongo_query = translate_nl_to_query(nl_query, db_type="mongo")

        if mongo_query.startswith("```"):
            mongo_query = mongo_query.strip("`").replace("json", "").strip()

        parsed_query = json.loads(mongo_query)

        is_mutation = any(op in parsed_query for op in ["insert", "update", "delete", "operation"])

        if is_mutation:
            return JSONResponse({
                "query": mongo_query,
                "mutation": True,
                "result": "Mutation query detected. Requires confirmation."
            })

        results = run_mongo_query(mongo_query)

        explanation = explain_result_with_gemini(results) if results else "No results to explain."

        return JSONResponse({
            "query": mongo_query,
            "mutation": False,
            "results": results,
            "explanation": explanation
        })

    except json.JSONDecodeError as e:
        return JSONResponse({"error": f"Error decoding query: {e}"}, status_code=500)
