# CreateApis

A quick way to make APIs for Django-Rest-Framework Project

Steps: 
	1. Clone the project inside Django Application
	2. Install required libraries using requirements.txt file
		Go to terminal: pip3 install requirements.txt

#How to Create API using this

#Sample views.py file
	from app.models import Subject
	from app.serializer import SubjectSerializer
	from CreateApis.ApiCreator_library.ApiCreator import ApiCreator 
	
	class SubjectView(ApiCreator):
    		model = Subject
    		model_serializer = SubjectSerializer
    		JWT_permission_on = ["POST", "PUT", "DELETE"]
    		
# Sample urls.py file
	from app.views import SubjectView
	urlpatterns = [
			...
			path('subject', views.SubjectView.as_view()),
			...
			]

# Sample models.py file
	from django.db import models
	
	class Subject(models.Model):
    		subject_name = models.CharField(max_length=100)

		
# A Sample serializer.py file 
	class SubjectSerializer(serializers.ModelSerializer):
	    class Meta:
		model = Subject
		fields = ['subject_name']
