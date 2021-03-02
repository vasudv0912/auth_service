from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from app.models import Token
from app.utils import token_required
import redis
from app.utils import generate_token
from kafka import KafkaProducer
import json

client = redis.Redis(
host='redis',
port=6379)

class Register(APIView):
    def post(self, request, format=None):
        params = request.data
        user = User.objects.create_user(username=params['username'], password=params['password'])
        user.first_name=params['first_name']
        user.last_name=params['last_name']
        user.email=params['email']
        user.save()
        return Response({'msg': "USER REGISTERED"}, status=status.HTTP_200_OK)


class GetToken(APIView):

	def post(self, request, format=None):
	    username = request.data.get('username', None)
	    password = request.data.get('password', None)
	    if username is not None and password is not None:
	        user = authenticate(username=username, password=password)
	        if user is not None:
	            if user.is_active:
	                token = client.get(user.id)
	                print(token)
	                if token:
	                    # token = token_exist.first().token
	                    return Response({'token': token}, status=status.HTTP_200_OK)
	                else:
	               
	                    new_token = generate_token()

	                    client.set(user.id,new_token)

	                    return Response({'token': new_token}, status=status.HTTP_200_OK)
	            else:
	                return Response({'error': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
	        else:
	            return Response({'error': 'Invalid Username/Password'}, status=status.HTTP_400_BAD_REQUEST)
	    else:
	        return Response({'error': 'No Credentials found'}, status=status.HTTP_400_BAD_REQUEST)


class Book(APIView):

	@token_required

	def post (self,request,format=None):
		print(request.user_id)
		# producer = KafkaProducer(bootstrap_servers='127.0.0.1:9091')
		# producer.send('book', json.dumps(request.data).encode('utf-8'))
		# return Response({'msg':'Book Received'}, status=status.HTTP_200_OK)
		bootstrap_servers = ['172.17.0.1:9091']
		KAFKA_VERSION = (0,11,5)
		topicName = 'add_book'
		producer = KafkaProducer(bootstrap_servers = bootstrap_servers,value_serializer=lambda v: json.dumps(v).encode('utf-8'))
		producer.send(topicName, request.data)
		producer.flush()
		print(">>")
		return Response({'msg':'Book Received'}, status=status.HTTP_200_OK)