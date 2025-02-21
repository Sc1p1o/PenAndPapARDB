from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CharacterStats
from .serializers import CharacterStatsSerializer


class CharacterStatsList(APIView):
    def get(self, request):
        stats = CharacterStats.objects.all()
        serializer = CharacterStatsSerializer(stats, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CharacterStatsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CharacterStatsDetail(APIView):
    def get(self, request, pk):
        try:
            stat = CharacterStats.objects.get(pk=pk)
            serializer = CharacterStatsSerializer(stat)
            return Response(serializer.data)
        except CharacterStats.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
