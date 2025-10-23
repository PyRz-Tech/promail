from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=8080)

    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())

    print("✅ token.json created successfully!")

if __name__ == '__main__':
    main()
