from rest_framework import serializers

from core.models import Procedure


class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ["id", "document", "procedure_type", "parent_procedure", "created_at", "updated_at"]


class RuleEvaluationInputSerializer(serializers.Serializer):
    rule_pack = serializers.CharField(help_text="Relative path, e.g. iso_15614_1/rules.json")
    payload = serializers.JSONField()
    previous_payload = serializers.JSONField(required=False, default=None)
    debug = serializers.BooleanField(required=False, default=False)
