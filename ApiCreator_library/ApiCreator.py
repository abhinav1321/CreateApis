from django.views import View
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser
import io


class ApiCreator(View):
    '''
        Create API Automatically by providing model and serializers
        Http methods : GET, POST, PUT, DELETE
        Response Type: Http with Json Data
    '''
    model = None
    model_serializer = None
    user_model = None

    def get(self, request):
        pk = request.GET.get('id')
        obj = self.model.objects.get(id=pk)
        serialized_data = self.model_serializer(obj)
        json_renderer = JSONRenderer().render(serialized_data.data)
        # return JsonResponse(serialized_data)
        return HttpResponse(json_renderer)

    def post(self, request):
        json_data = request.body
        stream = io.BytesIO(json_data)
        python_data = JSONParser().parse(stream)
        if self.user_model:
            python_data['user'] = self.user_model.objects.get(username=python_data['user'])
        serializer = self.model_serializer(data=python_data)
        if serializer.is_valid():
            serializer.save()
            res = {'msg': 'created'}
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type='application/json')
        else:
            return HttpResponse('not created')

    def put(self, request):
        json_data = request.body
        stream = io.BytesIO(json_data)
        python_data = JSONParser().parse(stream)
        if self.user_model and 'user' in python_data.keys():
            python_data['user'] = self.user_model.objects.get(username=python_data['user'])
        id = python_data.get('id')
        obj = self.model.objects.get(id=id)
        serializer = self.model_serializer(obj, data=python_data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return HttpResponse('updated successfully')

    def delete(self, request):
        json_data = request.body
        stream = io.BytesIO(json_data)
        python_data = JSONParser().parse(stream)
        id = python_data.get('id')
        obj = self.model.objects.get(id=id)
        obj.delete()
        return HttpResponse('deleted' + str(id))
