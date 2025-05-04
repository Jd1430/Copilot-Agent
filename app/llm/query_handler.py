import google.generativeai as genai
from app.config import get_secret
import json

genai.configure(api_key=get_secret("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def translate_nl_to_query(nl_query, db_type):
    prompt = (
        f"You are a helpful assistant. Convert the following natural language question into a valid "
        f"{'MongoDB' if db_type == 'mongo' else 'PostgreSQL'} command. "
        f"If it is a read operation (find), return a JSON query. If it's a write operation "
        f"(insert, update, delete), return a JSON object with this format:\n\n"
        f"{{\n  \"operation\": \"insert|update|delete\",\n  \"query\": {{ ... }}\n}}\n\n"
        f"Only return JSON, no explanation.\n"
        f"Natural Language: {nl_query}\n"
        f"JSON:"
    )

    try:
        response = model.generate_content(prompt)
        query_text = response.text.strip()

        # Clean markdown formatting
        if query_text.startswith("```"):
            query_text = query_text.strip("`").replace("json", "").strip()

        return query_text
    except Exception as e:
        return f"Error generating query: {e}"
    
def explain_result_with_gemini(query_result):
    if not query_result:
        return "No results to explain."

    # Convert to plain text for Gemini
    result_str = json.dumps(query_result[:5], indent=2)  # Limit for brevity

    prompt = (
        "You are a helpful assistant. Here's a query result from MongoDB:\n\n"
        f"{result_str}\n\n"
        "Provide a brief summary or insight into the data shown above."
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating explanation: {e}"



