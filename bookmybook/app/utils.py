from rest_framework.response import Response
from rest_framework import status
import binascii
import os
import redis
client = redis.Redis(
host='redis',
port=6379)


def token_required(func):
    def inner(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if auth_header is not None:
            tokens = auth_header.split(' ')
            if len(tokens) == 2:
                
                try:
                    if client.get(tokens[0]).decode('utf-8') == tokens[1]:
                        request.user_id = tokens[0]
                        request.token=tokens[1]
                        return func(self, request)
                except Exception as e :
                    return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'error': 'Invalid Header'}, status=status.HTTP_401_UNAUTHORIZED)
    return inner

def generate_token():
    return binascii.hexlify(os.urandom(20)).decode('utf-8')