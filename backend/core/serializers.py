from rest_framework import serializers

from core.models import (
    AutomaticWeldingDetails,
    CertificateProcessEquipment,
    CertificateResultDocument,
    CertificateRevalidation,
    CertificateSignature,
    Procedure,
    WelderOperatorCertificate,
    MechanizedWeldingDetails,
)


class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ["id", "document", "procedure_type", "parent_procedure", "created_at", "updated_at"]


class RuleEvaluationInputSerializer(serializers.Serializer):
    rule_pack = serializers.CharField(help_text="Relative path, e.g. iso_15614_1/rules.json")
    payload = serializers.JSONField()
    previous_payload = serializers.JSONField(required=False, default=None)
    debug = serializers.BooleanField(required=False, default=False)


class CertificateProcessEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateProcessEquipment
        exclude = ["certificate"]


class MechanizedWeldingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MechanizedWeldingDetails
        exclude = ["certificate"]


class AutomaticWeldingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomaticWeldingDetails
        exclude = ["certificate"]


class CertificateResultDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateResultDocument
        exclude = ["certificate"]


class CertificateSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateSignature
        exclude = ["certificate"]


class CertificateRevalidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateRevalidation
        exclude = ["certificate"]


class WelderOperatorCertificateSerializer(serializers.ModelSerializer):
    process_equipment = CertificateProcessEquipmentSerializer(required=False, allow_null=True)
    mechanized_details = MechanizedWeldingDetailsSerializer(required=False, allow_null=True)
    automatic_details = AutomaticWeldingDetailsSerializer(required=False, allow_null=True)
    result_documents = CertificateResultDocumentSerializer(many=True, required=False)
    signatures = CertificateSignatureSerializer(many=True, required=False)
    revalidations = CertificateRevalidationSerializer(many=True, required=False)

    class Meta:
        model = WelderOperatorCertificate
        fields = "__all__"

    def create(self, validated_data):
        process_equipment = validated_data.pop("process_equipment", None)
        mechanized_details = validated_data.pop("mechanized_details", None)
        automatic_details = validated_data.pop("automatic_details", None)
        result_documents = validated_data.pop("result_documents", [])
        signatures = validated_data.pop("signatures", [])
        revalidations = validated_data.pop("revalidations", [])

        certificate = WelderOperatorCertificate.objects.create(**validated_data)
        if process_equipment:
            CertificateProcessEquipment.objects.create(certificate=certificate, **process_equipment)
        if mechanized_details:
            MechanizedWeldingDetails.objects.create(certificate=certificate, **mechanized_details)
        if automatic_details:
            AutomaticWeldingDetails.objects.create(certificate=certificate, **automatic_details)

        for doc in result_documents:
            CertificateResultDocument.objects.create(certificate=certificate, **doc)
        for signature in signatures:
            CertificateSignature.objects.create(certificate=certificate, **signature)
        for revalidation in revalidations:
            CertificateRevalidation.objects.create(certificate=certificate, **revalidation)
        return certificate

    def update(self, instance, validated_data):
        process_equipment = validated_data.pop("process_equipment", None)
        mechanized_details = validated_data.pop("mechanized_details", None)
        automatic_details = validated_data.pop("automatic_details", None)
        result_documents = validated_data.pop("result_documents", None)
        signatures = validated_data.pop("signatures", None)
        revalidations = validated_data.pop("revalidations", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if process_equipment is not None:
            CertificateProcessEquipment.objects.update_or_create(certificate=instance, defaults=process_equipment)
        if mechanized_details is not None:
            MechanizedWeldingDetails.objects.update_or_create(certificate=instance, defaults=mechanized_details)
        if automatic_details is not None:
            AutomaticWeldingDetails.objects.update_or_create(certificate=instance, defaults=automatic_details)

        if result_documents is not None:
            instance.result_documents.all().delete()
            for doc in result_documents:
                CertificateResultDocument.objects.create(certificate=instance, **doc)
        if signatures is not None:
            instance.signatures.all().delete()
            for signature in signatures:
                CertificateSignature.objects.create(certificate=instance, **signature)
        if revalidations is not None:
            instance.revalidations.all().delete()
            for revalidation in revalidations:
                CertificateRevalidation.objects.create(certificate=instance, **revalidation)
        return instance
