from django.views import View
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser
import io
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.decorators import permission_classes as permission
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from rest_framework.views import APIView


class ApiCreator(APIView):
    '''
        Create API Automatically by providing model and serializers
        Http methods : GET, POST, PUT, DELETE
        Response Type: Http with Json Data

        model, model_serializer  = ModelName, ModelSerializerName
        is_required_login = True
        root_login_url = 'Https://root-login-url'
        JWT_Permission = [IsAuthenticated]
        permission_on = ['GET', 'POST', 'PUT', "DELETE']
    '''

    model = None
    model_serializer = None
    user_model = None
    is_required_login = False
    root_login_url = ''
    permission_classes = []
    JWT_permission_on = []

    def dispatch(self, request, *args, **kwargs):
        """
        Overriding dispatch method of APIView to get JWT auth on customised view
        JWT_permission_on = ["POST", "PUT", "DELETE"] : Can select view of your choice


        `.dispatch()` is pretty much the same as Django's regular dispatch,
        but with extra hooks for startup, finalize, and exception handling.
        """
        try:
            if request.method.lower() in [x.lower() for x in self.JWT_permission_on]:
                self.permission_classes = [IsAuthenticated]
        except Exception as e:
            print(e)

        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            self.initial(request, *args, **kwargs)

            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(),
                                  self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response


    def get(self, request):
        print(self.is_required_login)
        if self.is_required_login:
            if not request.user.is_authenticated:
                return redirect('http://localhost:8000/auth/login')
        else:
            return self.get_func(request)

    def get_func(self, request):

        pk = request.GET.get('id', None)
        if not pk:
            obj = self.model.objects.all()
            serialized_data = self.model_serializer(obj, many=True)
        else:
            obj = self.model.objects.get(id=pk)
            serialized_data = self.model_serializer(obj)
        json_renderer = JSONRenderer().render(serialized_data.data)
        # return JsonResponse(serialized_data)
        current_site = get_current_site(request)
        print(current_site)

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

