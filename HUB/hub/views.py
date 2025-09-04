from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FullCDSerializer, RequestCDSerializer
from .models import CD


class CdRegisterAPIView(APIView):
    """
    - Distribution Center **registration** view
    - **Full serializer** with models.Base fields
    """
    def post(self, request, *args, **kwargs):
        serializer = FullCDSerializer(data=request.data)

        if serializer.is_valid():
            cd = serializer.save()
            return Response({
                "status": "success",
                "id": cd['id'],
                "created": cd['created'],
                "name": cd['name'],
                "region": cd['region'],
                "ip": cd['ip'],
                "action": "created"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": "error",
                "message": "Something went wrong. Check the documentation for more info."
            }, status=status.HTTP_400_BAD_REQUEST)


class CdPatchAPIView(APIView):
    """
    - PATCH/PUT methods for Distribution Centers objects.
    - *OBS.: This endpoint is not meant to be public, changing permissions soon.*
    """
    def patch(self, request, *args, **kwargs):
        cd_obj = get_object_or_404(CD) # lembrar do kwargs aqui para name/slug/id
        serializer = FullCDSerializer(data=request.data) 


        if serializer.is_valid():
            cd = serializer.save()
            return Response({
                "status": "success",
                "id": cd['id'],
                "modified": cd['modified'],
                "name": cd['name'],
                "region": cd['region'],
                "ip": cd['ip'],
                "action": "modified"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Something went wrong. Check the documentation for more info."
            }, status=status.HTTP_400_BAD_REQUEST)


class CdRequestAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RequestCDSerializer(data=request.data)
        data = serializer.validated_data

        print(data)