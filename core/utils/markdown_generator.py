import os
import json
import openai
from dotenv import load_dotenv
load_dotenv()

openai.api_key=os.getenv("OPENAI_API_KEY")

def generate_markdown(features, project_name="My Project", constraints=None, priority_hint="balanced"):
	features_text = "\n".join([ f"- {f}" for f in features])

	prompt = f"""
	You are a senior software architect and product planner.
	Project Name: {project_name}
	Constraints: {constraints}
	Priority hint: {priority_hint}

	Features list:
	{features_text}

	Your task:
	1. Group features into Epics or Feature Groups.
	2. For each feature, include:
	- Short description (1 sentence)
	- Priority (High/Medium/Low)
	- Complexity (Small/Medium/Large)
	- Acceptance Criteria (3 bullets)
	- Suggested Milestone (MVP / Iteration 2 / Later)
	3. Create a well-formatted Markdown document that includes:
	- **Title + TL;DR summary**
	- **Assumptions & Constraints**
	- **Grouped Features**
	- **Prioritized Roadmap**
	- **Suggested API / Data Models (optional)**
	- **Next Steps & Owners**
	4. At the end of the Markdown, append:
	- A **recommended project folder tree structure**, suitable for the tech stack you infer from the features.
	- A **recommended tools and libraries list** (e.g., frameworks, databases, auth systems, APIs, DevOps tools, etc.)
	5. Finally, include a JSON block summarizing all features with fields:
	`feature, group, priority, complexity, milestone, acceptance_criteria`.

	IMPORTANT:
	- Detect the language of the input Features list automatically.
	- Generate all Markdown content in the **same language** as the Features list input.
	- If input is Persian, output Markdown must be fully Persian; if English, output fully English.

	Output ONLY Markdown with the JSON block and project tree at the end.
	"""


	response=openai.ChatCompletion.create(
		model="gpt-4o-mini",
		messages=[
			{"role":"system", "content":"You are a concise product architect assistant."},
			{"role":"user", "content":prompt}
		],
		temperature=0.2,
		max_tokens=1500
	)
	md_text = response.choices[0].message.content.strip()
	return md_text
