from django.shortcuts import render
from django.views.generic import CreateView
from .models import Project
from .forms import ProjectForm
from core.utils.email_utils import send_markdown_email
from core.utils.clean_features import clean_features
from core.utils.feature_extractor import extract_features_from_text
from core.utils.markdown_generator import generate_markdown
from django.contrib import messages

# Create your views here.



class PromailListView(CreateView):
    form_class=ProjectForm
    model=Project
    template_name="index.html"
    success_url="/"


    def form_valid(self, form):
        response=super().form_valid(form)
        
        project_name = form.cleaned_data['name']
        features_text = form.cleaned_data['features']
        email = form.cleaned_data['email']


        features = extract_features_from_text(features_text)
        filtered_features = clean_features(features)
        md_context=generate_markdown([filtered_features], project_name)


        send_markdown_email(email, project_name, md_context)

        messages.success(self.request, "✅ Project submitted and email sent successfully!")
        return response