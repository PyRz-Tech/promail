```markdown
# Django + OpenAI Project: Feature Extractor & Markdown Emailer  
**Full Documentation – Real Talk, No AI Voice, Just How It Is**

One page. User types project name, dumps a messy description, adds email, hits send.  
We:  
- Read it  
- Pull out clean features  
- Cut the crap  
- Build a full Markdown spec  
- Email it  

No login. No accounts. No meetings. Done.

---

## What’s this thing for?

> **"Take a brain dump and turn it into a real spec — instantly."**

You’ve got an idea. You can’t write it down properly.  
This does what a senior dev or PM would do — but without the 3-hour call.

---

## Tech We Actually Used

| Part | Tool |
|------|------|
| Backend | Django (fast, simple, gets the job done) |
| Frontend | Tailwind + Django templates (no React, no overhead) |
| AI | OpenAI `gpt-4o-mini` (cheap, fast, perfect for this) |
| Email | Gmail API (free, secure, no SMTP mess) |
| Secrets | `.env` (keys stay hidden) |
| DB | SQLite locally, PostgreSQL in prod |
| Deploy | Render, Railway, or any Python host |

---

## Folder Layout (What You See)

```
myproject/
├── core/                     # All the real work
│   ├── models.py             # Saves the submission
│   ├── forms.py              # Form with clean styling
│   ├── views.py              # The engine — runs everything
│   ├── urls.py               # One route: homepage
│   └── utils/                # Helper tools
│       ├── feature_extractor.py   # Reads mess → clean features
│       ├── clean_features.py       # Drops duplicates & junk
│       ├── markdown_generator.py   # Builds the final spec
│       └── email_utils.py          # Sends the email
│       └── token.json            # Gmail token goes **right here**
├── templates/
│   └── index.html            # Only page — clean, responsive
├── config/
│   ├── settings.py           # Django setup
│   └── urls.py               # Points `/` to core
├── .env                      # OpenAI key
├── token.json                # (Optional: can be here too, but **better in core/utils/**)
└── manage.py
```

---

## Config Files

### `.env`  
**Hide your keys here**  
Just one line. No key = app dies.

```env
OPENAI_API_KEY=sk-your-real-key-here
```

---

### `config/settings.py`  
**Tell Django where stuff is**  
Says: use `core` app and look in `templates/` for HTML.

```python
INSTALLED_APPS = [
    ...
    'core'
]

TEMPLATES = [
    {
        ...,
        'DIRS': [BASE_DIR / 'templates'],
        ...,
    }
]
```

---

### `config/urls.py`  
**Root goes to core**  
Whole site = one page. This sends `/` to `core.urls`.

```python
from django.urls import path, include

urlpatterns = [
    ...,
    path('', include('core.urls')),
]
```

---

## Core App – The Engine (`core/`)

---

### `models.py`  
**Stashes the user input**  
Name, description, email, timestamp. That’s all.

```python
from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=250)
    features = models.TextField(max_length=1000)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.email}"
```

---

### `urls.py`  
**One route: the main page**  
`/` → main view. Nothing else.

```python
from django.urls import path
from .views import PromailListView

app_name = 'core'

urlpatterns = [
    path("", PromailListView.as_view(), name='main')
]
```

---

### `forms.py`  
**Clean form with Tailwind**  
User fills name, ideas, email. Looks good on phone and desktop.

```python
from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "features", "email"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 text-black",
                "placeholder": "Project name (e.g., Task Manager)"
            }),
            "features": forms.Textarea(attrs={
                "class": "w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 text-black",
                "placeholder": "Describe what you want. No format needed. Just write.",
                "rows": "6"
            }),
            "email": forms.TextInput(attrs={
                "class": "w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 text-black",
                "placeholder": "Your email — we'll send the spec here",
                "autocomplete": "off",
            })
        }
```

---

### `views.py` – The Engine  
**Where it all happens**  
Form → save → AI extract → clean → generate → email → success.

```python
from django.views.generic import CreateView
from django.contrib import messages
from .models import Project
from .forms import ProjectForm
from core.utils.feature_extractor import extract_features_from_text
from core.utils.clean_features import clean_features
from core.utils.markdown_generator import generate_markdown
from core.utils.email_utils import send_markdown_email

class PromailListView(CreateView):
    form_class = ProjectForm
    model = Project
    template_name = "index.html"
    success_url = "/"

    def form_valid(self, form):
        response = super().form_valid(form)
        
        project_name = form.cleaned_data['name']
        raw_text = form.cleaned_data['features']
        email = form.cleaned_data['email']

        # 1. Extract
        features = extract_features_from_text(raw_text)
        
        # 2. Clean
        clean_features_list = clean_features(features)
        
        # 3. Generate
        markdown_content = generate_markdown(
            features=clean_features_list,
            project_name=project_name
        )
        
        # 4. Send
        send_markdown_email(email, project_name, markdown_content)

        messages.success(self.request, "Done! Check your email — your spec is on the way.")
        return response
```

---

## Utils – The AI Pipeline (`core/utils/`)

---

### `feature_extractor.py`  
**Reads messy text, returns clean features**  
Like someone reading a rant and making a bullet list. Output: JSON only.

```python
import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_features_from_text(user_text):
    prompt = f"""
    This is a raw project description. It might be messy, missing punctuation, or all over the place.
    Your job: pull out clear, distinct features as short sentences.
    No duplicates. Summarize long ones if needed.
    Return ONLY valid JSON: {{"features": ["feature one", "feature two", ...]}}

    Text:
    \"\"\"{user_text}\"\"\"
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a no-nonsense feature extractor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=800
    )

    output = response.choices[0].message.content.strip()
    try:
        return json.loads(output).get("features", [])
    except json.JSONDecodeError:
        print("Warning: OpenAI didn't return clean JSON. Using raw lines.")
        return [line.strip() for line in output.splitlines() if line.strip()]
```

---

### `clean_features.py`  
**Cleans up the AI output**  
Drops duplicates, tiny junk, and garbage. Keeps the good stuff.

```python
def clean_features(features_list, min_length=5):
    if not features_list:
        return []

    seen = set()
    result = []

    for feature in features_list:
        clean = feature.strip()
        if len(clean) < min_length:
            continue
        if clean.lower() in seen:
            continue
        result.append(clean)
        seen.add(clean.lower())

    return result
```

---

### `markdown_generator.py`  
**Builds the full spec**  
Asks OpenAI to group, prioritize, add roadmap, folder structure, tools — everything.

```python
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_markdown(features, project_name="Untitled Project", constraints=None, priority_hint="balanced"):
    features_text = "\n".join([f"- {f}" for f in features]) if features else "- No features found."

    prompt = f"""
    You are a senior software architect and product planner.
    
    Project: {project_name}
    Constraints: {constraints or "None"}
    Priority Focus: {priority_hint}

    Features:
    {features_text}

    Build a complete, professional Markdown document with:
    1. Title + one-line summary
    2. Assumptions & Constraints
    3. Grouped features (Epics)
       • For each: short description, priority, complexity, 3 acceptance criteria, milestone
    4. Prioritized roadmap
    5. Suggested data models / API ideas
    6. Next steps & who should own them
    7. Recommended folder structure
    8. Tools & libraries list
    9. JSON summary of all features at the end

    Match the language of the input features.
    Output ONLY the Markdown + JSON block.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a sharp, experienced product architect."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=2000,
    )
    return response.choices[0].message.content.strip()
```

---

### `email_utils.py`  
**Sends the final file**  
Uses your Gmail token (from `core/utils/token.json`), attaches `.md`, sends it.

```python
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.json")

def send_markdown_email(to_email, project_name, md_content, token_path=TOKEN_PATH):
    creds = Credentials.from_authorized_user_file(token_path)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("gmail", "v1", credentials=creds)

    message = MIMEMultipart()
    message["to"] = to_email
    message["from"] = "me"
    message["subject"] = f"Your Project Spec: {project_name}"

    message.attach(MIMEText("Your full project specification is attached as a Markdown file.", "plain"))

    safe_name = "".join(c for c in project_name if c.isalnum() or c in " -_").rstrip()
    if not safe_name:
        safe_name = "Project_Spec"

    part = MIMEBase("application", "octet-stream")
    part.set_payload(md_content.encode("utf-8"))
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename='{safe_name}.md'")
    message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
```

---

## `templates/index.html` – The Only Page  
**What the user sees**  
Clean, centered, works on phone. One form. One button.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Project Spec Generator</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen flex items-center justify-center p-4">
  <div class="w-full max-w-2xl bg-white rounded-xl shadow-lg p-8">
    <h1 class="text-3xl font-bold text-center text-red-600 mb-6">Project Spec Generator</h1>
    <p class="text-gray-600 text-center mb-8">
      Just describe your idea. We’ll turn it into a full spec and email it to you.
    </p>

    {% if messages %}
      {% for message in messages %}
        <div class="mb-4 p-3 rounded bg-green-100 text-green-800 font-medium">{{ message }}</div>
      {% endfor %}
    {% endif %}

    <form method="post" class="space-y-6">
      {% csrf_token %}
      {{ form.as_p }}
      <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-3 rounded-lg transition">
        Generate & Send Spec
      </button>
    </form>

    <p class="text-xs text-gray-500 text-center mt-8">
      Powered by Django + OpenAI. No data stored beyond submission.
    </p>
  </div>
</body>
</html>
```

---

## Setup & Running It

### 1. Local Setup  
**2 minutes to run**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install django openai python-dotenv google-auth google-api-python-client
```

---

### 2. Generate Gmail Token (`token.json`) — **One-Time Script**  
**Create `generate_token.py` in project root**

```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=8080)

    # Saves token.json directly into core/utils/
    with open('core/utils/token.json', 'w') as token_file:
        token_file.write(creds.to_json())

    print("token.json created successfully in core/utils/!")

if __name__ == '__main__':
    main()
```

**Before running:**  
1. Go to [Google Cloud Console](https://console.cloud.google.com/)  
2. Enable Gmail API  
3. Create OAuth 2.0 Client ID → Desktop app  
4. Download `credentials.json` → put in project root  
5. Run: `python generate_token.py`  
6. Browser opens → allow access → `token.json` is saved in `core/utils/`

---

### 3. Run the App  
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## How It Works (Step by Step)

1. User hits `/` → sees form  
2. Types name, messy text, email → clicks **Generate & Send**  
3. Django saves to DB  
4. OpenAI extracts features  
5. We clean the list  
6. OpenAI builds full spec  
7. Gmail sends `.md` file  
8. Success message → user checks email

---


## Clone It

```bash
git clone ....
```

---

