from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Project, ProjectOwner
from .serializer import ProjectSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import ProjectStatusSerializer

class CreateProjectView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise AuthenticationFailed('User is not authenticated')
        
        owner = get_object_or_404(ProjectOwner, user=self.request.user)
        serializer.save(owner=owner)

#عرض المشاريع المتاحه فقط
class ProjectStatusView(APIView):
    def get(self, request):
        projects = Project.objects.filter(status='active')
        serializer = ProjectStatusSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from investor.models import InvestmentOffer
from .serializer import InvestmentOfferSerializer
from rest_framework import status

class ProjectOffersView(APIView):
    def get(self, request, project_id):
        offers = InvestmentOffer.objects.filter(project_id=project_id)
        serializer = InvestmentOfferSerializer(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
