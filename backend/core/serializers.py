from rest_framework import serializers

from core.models import Procedure


class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ["id", "document", "procedure_type", "parent_procedure", "created_at", "updated_at"]


class RuleEvaluationInputSerializer(serializers.Serializer):
    standard_slug = serializers.CharField()
    current = serializers.JSONField()
    previous = serializers.JSONField(required=False, default=dict)
