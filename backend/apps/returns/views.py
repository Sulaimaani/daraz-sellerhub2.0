from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ReturnPackage, ReturnClaim, PackageInspection
from .serializers import ReturnPackageSerializer, ReturnClaimSerializer, PackageInspectionSerializer

class ReturnPackageViewSet(viewsets.ModelViewSet):
    queryset = ReturnPackage.objects.prefetch_related('items', 'inspections', 'claims', 'claims__evidence').all()
    serializer_class = ReturnPackageSerializer

class ReturnClaimViewSet(viewsets.ModelViewSet):
    queryset = ReturnClaim.objects.all()
    serializer_class = ReturnClaimSerializer

class PackageInspectionViewSet(viewsets.ModelViewSet):
    queryset = PackageInspection.objects.all()
    serializer_class = PackageInspectionSerializer
