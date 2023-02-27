from rest_framework import serializers
from .models import testData

class testData_Serializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'title',
            'content',
        )
        model = testData