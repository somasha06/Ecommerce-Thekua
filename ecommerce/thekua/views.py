from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupRequestSerializer,OTPVerifySerializer,LoginSerializer,ProfileSerializer
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import *
# Create your views here.

class SignupRequestAPIView(APIView):
    def post(self,request):
        serializer=SignupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pending_user=serializer.save()

        return Response({"message": "OTP sent successfully","session_id": str(pending_user.session_id)},status=status.HTTP_200_OK)
    

class OTPVerifyAPIView(APIView):
    def post(self,request):
        serializer=OTPVerifySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response({"message": "User created successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            return Response(
                {
                    "message": "Login successful",
                    "user_id": data["user_id"],
                    "username": data["username"],
                    "access": data["access"],
                    "refresh": data["refresh"],
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        profile,created=Profile.objects.get_or_create(user=request.user)
        serializer=ProfileSerializer(profile)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def put(self,request):
        profile,created=Profile.objects.get_or_create(user=request.user)
        serializer=ProfileSerializer(profile,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)