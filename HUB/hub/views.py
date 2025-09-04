from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
import requests

from .serializers import FullCDSerializer, RequestCDSerializer
from .models import CD


class CdRegisterAPIView(APIView):
    """
    **POST** Distribution Center **creation** objects endpoint
    - **Full serializer** with models.Base fields
    """
    def post(self, request, *args, **kwargs):
        serializer = FullCDSerializer(data=request.data)

        if serializer.is_valid():
            cd = serializer.save()
            return Response({
                "status": "success",
                "id": cd.id,
                "created": cd.created,
                "name": cd.name,
                "region": cd.region,
                "ip": cd.ip,
                "balance": cd.balance,
                "action": "created"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": "error",
                "message": "Something went wrong. Check the documentation for more info.",
                "error_msg": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class CdPatchAPIView(APIView):
    """
    **PATCH** to update Distribution Centers objects fields.
    - *OBS.: This endpoint is not meant to be public, changing permissions soon.*
    - *WARNING: This endpoint is not meant to be public! Permissions will be aplied to this soon.*
    """
    def patch(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        cd_obj = get_object_or_404(CD, slug=slug)
        serializer = FullCDSerializer(cd_obj, data=request.data, partial=True) 

        if serializer.is_valid():
            cd = serializer.save()
            return Response({
                "status": "success",
                "id": cd.id,
                "modified": cd.modified,
                "name": cd.name,
                "region": cd.region,
                "ip": cd.ip,
                "action": "modified"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Something went wrong. Check the documentation for more info."
            }, status=status.HTTP_400_BAD_REQUEST)


class CdListAPIView(APIView):
    """
    **GET** for single **object** or **list** [CD]
    - REQUEST accepts *identifier* or it **will bring the list of collection to response**
    - IDENTIFIER: **slug** or **ID**
    """
    def get(self, request, *args, **kwargs):
        identifier = kwargs.get('slug') or kwargs.get('pk')

        if identifier:
            if str(identifier).isdigit():
                cd = get_object_or_404(CD, id=identifier)
            else:
                cd = get_object_or_404(CD, slug=identifier)

            serializer = FullCDSerializer(cd)
        else:
            cd = CD.objects.all()
            serializer = FullCDSerializer(cd, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CdRequestAPIView(APIView):
    """
    **POST** - Transaction trade for Distribution Centers
    - CDs trade products trough this endpoint
    - Buyer CD will request this endpoint to ask HUB for more products
    - HUB will gather all candidates, choosing the cheaper one
    - HUB validates and operate the trade between the CD actors
    """
    def post(self, request, *args, **kwargs):
        serializer = RequestCDSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        product = data['product']
        quantity = data['quantity']
        cds = CD.objects.filter(is_active=True)
        seller = None

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
            port = request.META.get("REMOTE_PORT")
        
        formated_ip = f"{ip}:{port}"
        try:
            for cd in cds:
                if cd.ip == f"{ip}:{port}":
                    continue
                
                response_data = {
                    "product": product,
                    "quantity": quantity
                }

                cd_response = requests.get(
                    url=f"http://{cd.ip}/cd/v1/request/",
                    data=response_data,
                    timeout=5
                )

                cd_response.raise_for_status()
                response_data = cd_response.json()

                if not response_data['available']:
                    continue

                if seller:
                    if response_data['price'] < seller['price']:
                        seller = {"cd": cd.name, "price": response_data['price'], "quantity": response_data['quantity']}
                else:
                    seller = {"cd": cd.name, "price": response_data['price'], "quantity": response_data['quantity']}
            
            if not seller:
                return Response({
                    "status": "error",
                    "message": f"Could not find any CD with the requested amount of {product}"
                }, status=status.HTTP_200_OK)
            
            suplier = get_object_or_404(CD, slug=product)
            buyer = get_object_or_404(CD, ip=formated_ip)

            target_url = f"http://{buyer.ip}/cd/v1/product/sell/{product}/{quantity}/"
            origin_url = f"http://{formated_ip}/cd/product/buy/{product}/{quantity}/"

            try:
                target_response = requests.post(
                    url=target_url,
                    timeout=5
                )
                target_response.raise_for_status()

                origin_response = requests.post(
                    url=origin_url,
                    timeout=5
                )
                origin_response.raise_for_status()
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": "Something went wrong!",
                    "error_msg": str(e)
                }, status=status.HTTP_424_FAILED_DEPENDENCY)

            if target_response.status_code == 200 and origin_response.status_code == 200:
                return Response({
                    "status": "success",
                    "product": product,
                    "quantity": quantity,
                    "buyer": buyer.name,
                    "suplier": suplier.name,
                    "action": "trade"
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "error",
                    "message": "Something went wrong with the transaction!",
                    "error_msg_origin": origin_response.raise_for_status,
                    "error_msg_target": target_response.raise_for_status,
                    "msg": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "error_msg": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)