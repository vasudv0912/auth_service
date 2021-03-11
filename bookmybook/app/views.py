from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from app.models import Token, Pin
from app.utils import token_required
import redis
from app.utils import generate_token
from kafka import KafkaProducer
import json
import random
from grpc_requests import Client

bootstrap_servers = ['172.17.0.1:9091']
KAFKA_VERSION = (0, 11, 5)
client = redis.Redis(
    host='redis',
    port=6379)



grpc = Client.get_by_endpoint("library:50051")
# if you want connect tls
# client = Client.get_by_endpoint("localhost:443",ssl=True)
# or if you want Compression connect
# client = Client.get_by_endpoint("localhost:443",compression=grpc.Compression.Gzip)
# assert client.service_names == ["library.Library",'grpc.health.v1.Health']

health = grpc.service('grpc.health.v1.Health')
assert health.method_names == ('Check', 'Watch')

result = health.Check()
assert result == {'status': 'SERVING'}

library = grpc.service("library.Library")


class Register(APIView):
    def post(self, request, format=None):
        params = request.data
        user = User.objects.create_user(
            username=params['username'], password=params['password'])
        user.first_name = params['first_name']
        user.last_name = params['last_name']
        user.email = params['email']
        user.save()
        pin = Pin()
        pin.user_id = user.id
        pin.pin = random.randint(999, 9999)
        pin.save()
        wallet_bal = {"user_id": user.id, "balance": 0}
        topicName = 'wallet'
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topicName, wallet_bal)
        producer.flush()
        # request_data = {"name": user.first_name}
        # result = library.SayHello(request_data)
        # print(result)

        return Response({'msg':"USER REGISTERED"}, status=status.HTTP_200_OK)


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

                        client.set(user.id, new_token)

                        return Response({'token': new_token}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Invalid Username/Password'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'No Credentials found'}, status=status.HTTP_400_BAD_REQUEST)


class AddBook(APIView):

    @token_required
    def post(self, request, format=None):
        request.data['owner_id'] = request.user_id
        print(request.data)
        topicName = 'add_book'
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topicName, request.data)
        producer.flush()
        print(">>")
        return Response({'msg': 'Book Received'}, status=status.HTTP_200_OK)


class IssueBook(APIView):

    @token_required
    def post(self, request, format=None):
        request.data['_to'] = request.user_id
        topicName = 'issue_book'
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topicName, request.data)
        producer.flush()
        return Response({'msg': 'Book Issued'}, status=status.HTTP_200_OK)


class EditBook(APIView):

    @token_required
    def post(self, request, format=None):
        request.data['owner_id'] = request.user_id
        topicName = 'edit_book'
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topicName, request.data)
        producer.flush()
        return Response({'msg': 'Book Details Updated Sucessfully'}, status=status.HTTP_200_OK)


class ReleaseBook(APIView):
    @token_required
    def post(self, request, format=None):
        request.data['current_owner_id'] = request.user_id
        topicName = 'release_book'
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topicName, request.data)
        producer.flush()
        return Response({'msg': 'Book Released'}, status=status.HTTP_200_OK)


class DeleteBook(APIView):
    @token_required
    def post(self, request, format=None):
        request.data['current_owner_id'] = request.user_id
        topicName = 'delete_book'
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topicName, request.data)
        producer.flush()
        return Response({'msg': 'Book Deleted '}, status=status.HTTP_200_OK)


class Wishlist(APIView):
    @token_required
    def post(self, request, format=None):
        request.data['user_id'] = request.user_id
        topicName = 'wishlist'
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topicName, request.data)
        producer.flush()
        return Response({'msg': 'Book Added To Your Wishlist '}, status=status.HTTP_200_OK)


class Transaction(APIView):
    @token_required
    def post(self, request, format=None):
        pin = Pin.objects.get(user_id=request.user_id)
        if pin.pin == request.data['pin']:
            request.data['_from'] = request.user_id
            topicName = 'transaction'
            producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                     value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            producer.send(topicName, request.data)
            producer.flush()
            return Response({'msg': ' Transaction Sucessfull'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid Pin'}, status=status.HTTP_400_BAD_REQUEST)




class  GetBookdetails(APIView):
    @token_required
    def get(self,request,format=None):
        request_data = {"book_id": request.data['book_id']}
        result = library.GetBookDetails(request_data)
        print(result)

        return Response(result, status=status.HTTP_200_OK)



class GetAvailableBooks(APIView):
    @token_required
    def get(self,request,format=None):
        result=library.GetAvailableBooks()
        return Response(result,status=status.HTTP_200_OK)
