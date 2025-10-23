import os
import openai
import json
from dotenv import load_dotenv
load_dotenv()


openai.api_key=os.getenv("OPENAI_API_KEY")


def extract_features_from_text(user_text):


    prompt = f"""
    The text below contains project features, but may have no punctuation.
    Please split it into a list of distinct, clear features.
    Each feature should be a short sentence, no duplicates, and if necessary, summarize long sentences.
    Output ONLY as JSON with the key "features".

    User text:
    \"\"\"{user_text}\"\"\"
    """


    response=openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system", "content":"You are a helpful assistant that extracts project features from raw text."},
            {"role":"user", "content":prompt}
       ],
       temperature=0.2,
       max_tokens=800
    )


    text_output=response.choices[0].message.content.strip()


    try:
        features_json=json.loads(text_output)
        return features_json.get("features", [])


    except json.JSONDecodeError:
        print("Warning: LLM did not return valid JSON. Returning raw text output.")
        return [text_output]
