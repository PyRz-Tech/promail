```markdown
---

## Gmail API OAuth2 Setup – Step-by-Step (No Bullshit)

You need a `token.json` in `core/utils/` to send emails.  
Here’s how to get it **without pain**.

---

### 1. Go to Google Cloud Console  
[https://console.cloud.google.com/](https://console.cloud.google.com/)

- Pick or create a **project** (e.g., `spec-generator`)
- Click **"Select a project"** → **New Project** → name it → Create

---

### 2. Enable Gmail API  
- Left menu → **APIs & Services** → **Library**  
- Search: `Gmail API` → Click it → **Enable**

---

### 3. Create OAuth 2.0 Credentials  
- Left menu → **APIs & Services** → **Credentials**  
- Top bar → **+ CREATE CREDENTIALS** → **OAuth client ID**  
- Application type: **Desktop app**  
- Name: `Spec Generator Desktop` → **Create**

You’ll get a popup with:
- **Client ID**
- **Client Secret**

Click **DOWNLOAD JSON** → Save as `credentials.json` in your **project root**

---

### 4. Put `credentials.json` in Project Root
```
myproject/
├── credentials.json   ← Put it here
├── core/
│   └── utils/
│       └── (token.json will go here)
└── ...
```

---

### 5. Run the Token Generator Script

Create `generate_token.py` in your project root:

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

---

### 6. Run It

```bash
python generate_token.py
```

- Browser opens → **Choose your Google account**  
- You’ll see: *"This app isn't verified"* → Click **Advanced** → **Go to Spec Generator (unsafe)**  
- Click **Allow**  
- Done → `token.json` is now in `core/utils/`

---

### 7. Delete `credentials.json` (Optional but Smart)

After `token.json` is created, **delete `credentials.json`** from your project.  
Never commit it to GitHub.

```bash
rm credentials.json
```

---

### 8. Test It

Run your Django app:

```bash
python manage.py runserver
```

Submit a test form → check your email → should get the `.md` file.

---

## Common Issues & Fixes

| Problem | Fix |
|-------|-----|
| `Invalid grant: Bad Request` | Delete `token.json` and rerun `generate_token.py` |
| App not verified warning | Normal for local apps — just click **Advanced → Go to...** |
| No email sent | Check Gmail spam, or re-authenticate |

---

