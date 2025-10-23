from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
	class Meta:
		model=Project
		fields=["name", "features", "email"]

		widgets ={
			"name" : forms.TextInput(attrs={
				"class":"w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 text-black",
				"placeholder":"Enter project name"
				}),
			"features" : forms.Textarea(attrs={
				"class":"w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 text-black",
				"placeholder":"Enter feature description",
				"rows":"4"
			}),
			"email" : forms.TextInput(attrs={
				"class":"w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 text-black",
				"placeholder":"Enter your email",
				"autocomplete": "off",
			})
		}