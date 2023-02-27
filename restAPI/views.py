#backend/post/views.py
from django.shortcuts import render
from rest_framework import generics

from .models import testData
from .serializers import testData_Serializer

class List_testData(generics.ListCreateAPIView):
    queryset = testData.objects.all()
    serializer_class = testData_Serializer

class Detail_testData(generics.RetrieveUpdateDestroyAPIView):
    queryset = testData.objects.all()
    serializer_class = testData_Serializer