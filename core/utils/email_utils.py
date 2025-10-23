from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

current_dir = os.path.dirname(__file__)
token_path = os.path.join(current_dir, "token.json")

def send_markdown_email(to_email, project_name, md_content, token_path=token_path):

	creds=Credentials.from_authorized_user_file(token_path)
	service=build("gmail", "v1", credentials=creds)

	message=MIMEMultipart()
	message["to"]=to_email
	message["subject"]=f"Project Summary: {project_name}"

	body=MIMEText("Attached is your Mardown file.", "plain")
	message.attach(body)

	part=MIMEBase("application", "octet-stream")
	part.set_payload(md_content.encode("utf-8"))
	encoders.encode_base64(part)
	part.add_header("Content-Disposition", f"attachment; filename='{project_name}.md'")
	message.attach(part)

	raw=base64.urlsafe_b64encode(message.as_bytes()).decode()
	service.users().messages().send(userId='me', body={'raw':raw}).execute()