from rest_framework import serializers
from .models import FinanceTransaction, FinanceStatement, FinanceAudit, FinanceIssue

class FinanceTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceTransaction
        fields = '__all__'

class FinanceStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceStatement
        fields = '__all__'

class FinanceIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceIssue
        fields = '__all__'

class FinanceAuditSerializer(serializers.ModelSerializer):
    issues = FinanceIssueSerializer(many=True, read_only=True)
    
    class Meta:
        model = FinanceAudit
        fields = '__all__'
