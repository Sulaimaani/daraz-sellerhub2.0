from rest_framework import serializers
from .models import ReturnPackage, ReturnItem, PackageInspection, ReturnClaim, ClaimEvidence

class ClaimEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimEvidence
        fields = '__all__'

class ReturnClaimSerializer(serializers.ModelSerializer):
    evidence = ClaimEvidenceSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReturnClaim
        fields = '__all__'

class PackageInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageInspection
        fields = '__all__'

class ReturnItemSerializer(serializers.ModelSerializer):
    inspections = PackageInspectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReturnItem
        fields = '__all__'

class ReturnPackageSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, read_only=True)
    claims = ReturnClaimSerializer(many=True, read_only=True)
    
    # We will compute queue and deadline dynamically in the view or here
    queue = serializers.SerializerMethodField()
    deadline = serializers.SerializerMethodField()
    
    class Meta:
        model = ReturnPackage
        fields = '__all__'
        
    def get_queue(self, obj):
        from .classify import classify_package
        return classify_package(obj)
        
    def get_deadline(self, obj):
        from .deadlines import calculate_deadline
        return calculate_deadline(obj)
