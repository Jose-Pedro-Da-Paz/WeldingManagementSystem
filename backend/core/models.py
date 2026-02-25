from datetime import date

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Organization(TimeStampedModel):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class RuleSet(TimeStampedModel):
    standard = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.standard} ({self.version})"


class Document(TimeStampedModel):
    STATUS_VALID = "VALID"
    STATUS_WARNING = "WARNING"
    STATUS_INVALID = "INVALID"
    STATUS_CHOICES = [
        (STATUS_VALID, "Valid"),
        (STATUS_WARNING, "Warning"),
        (STATUS_INVALID, "Invalid"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_VALID)
    active_rule_set = models.ForeignKey(RuleSet, on_delete=models.PROTECT)


class DocumentVersion(TimeStampedModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions")
    version = models.PositiveIntegerField()
    payload = models.JSONField(default=dict)
    changed_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("document", "version")


class Procedure(TimeStampedModel):
    TYPE_PWPS = "pWPS"
    TYPE_PQR = "PQR"
    TYPE_WPS = "WPS"
    TYPE_CHOICES = [(TYPE_PWPS, "pWPS"), (TYPE_PQR, "PQR"), (TYPE_WPS, "WPS")]

    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    procedure_type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    parent_procedure = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)


class Welder(TimeStampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=100)


class Qualification(TimeStampedModel):
    welder = models.ForeignKey(Welder, on_delete=models.CASCADE, related_name="qualifications")
    procedure = models.ForeignKey(Procedure, on_delete=models.PROTECT)
    continuity_until = models.DateField(null=True, blank=True)


class RuleEvaluationResult(TimeStampedModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    rule_set = models.ForeignKey(RuleSet, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=Document.STATUS_CHOICES)
    errors = models.JSONField(default=list)
    warnings = models.JSONField(default=list)
    explanations = models.JSONField(default=list)


class CertificateStatus(models.TextChoices):
    VALID = "VALID", "Valid"
    INVALID = "INVALID", "Invalid"
    REJECTED = "REJECTED", "Rejected"


class FunctionalKnowledgeStatus(models.TextChoices):
    ACCEPTABLE = "ACCEPTABLE", "Acceptable"
    NOT_ACCEPTABLE = "NOT_ACCEPTABLE", "Not Acceptable"


class JobKnowledgeStatus(models.TextChoices):
    VERIFIED = "VERIFIED", "Verified"
    NOT_VERIFIED = "NOT_VERIFIED", "Not Verified"


class RequalificationBasis(models.TextChoices):
    RETEST_6Y = "RETEST_6Y", "Retest every 6 years"
    RETEST_3Y = "RETEST_3Y", "Retest every 3 years"
    OTHER = "OTHER", "Other"


class SignatureRole(models.TextChoices):
    EXAMINER = "EXAMINER", "Examiner"
    APPROVED_BY = "APPROVED_BY", "Approved By"


class ResultDocumentType(models.TextChoices):
    VT = "VT", "VT"
    RT = "RT", "RT"
    UT = "UT", "UT"
    FUNCTIONAL_TEST = "FunctionalTest", "Functional Test"
    OTHER = "Other", "Other"


class RevalidationGroup(models.TextChoices):
    EMPLOYER_SUPERVISOR = "EMPLOYER_SUPERVISOR", "Employer/Supervisor"
    DECISION_MAKER = "DECISION_MAKER", "Decision-Maker"


class WelderOperatorCertificate(TimeStampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="certificates")
    certificate_number = models.CharField(max_length=64)
    ped_nobo = models.CharField(max_length=64, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    weld_date = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    company_name = models.CharField(max_length=255)
    manufacturer_wps = models.CharField(max_length=128, blank=True)
    welder_name = models.CharField(max_length=255)
    id_type = models.CharField(max_length=128, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=128, blank=True)
    photo = models.FileField(upload_to="certificate/photos/", null=True, blank=True)
    functional_knowledge_test_status = models.CharField(max_length=32, choices=FunctionalKnowledgeStatus.choices, default=FunctionalKnowledgeStatus.ACCEPTABLE)
    job_knowledge_status = models.CharField(max_length=32, choices=JobKnowledgeStatus.choices, default=JobKnowledgeStatus.VERIFIED)
    code_testing_standard = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)
    approvals_basis = models.JSONField(default=dict)
    requalification_basis = models.CharField(max_length=16, choices=RequalificationBasis.choices, default=RequalificationBasis.RETEST_6Y)
    notes_disclaimer_template_version = models.CharField(max_length=64, default="default-v1")
    global_status = models.CharField(max_length=16, choices=CertificateStatus.choices, default=CertificateStatus.VALID)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_certificates")
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="updated_certificates")

    class Meta:
        unique_together = ("organization", "certificate_number")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.weld_date and not self.valid_until:
            years = 6 if self.requalification_basis == RequalificationBasis.RETEST_6Y else 3 if self.requalification_basis == RequalificationBasis.RETEST_3Y else 0
            if years:
                self.valid_until = date(self.weld_date.year + years, self.weld_date.month, self.weld_date.day)
        self.global_status = CertificateStatus.REJECTED if self.functional_knowledge_test_status == FunctionalKnowledgeStatus.NOT_ACCEPTABLE else CertificateStatus.VALID
        super().save(*args, **kwargs)


class CertificateProcessEquipment(TimeStampedModel):
    certificate = models.OneToOneField(WelderOperatorCertificate, on_delete=models.CASCADE, related_name="process_equipment")
    test_piece_process = models.CharField(max_length=128, blank=True)
    range_process = models.CharField(max_length=128, blank=True)
    test_piece_equipment = models.CharField(max_length=255, blank=True)
    range_equipment = models.CharField(max_length=255, blank=True)
    test_piece_welding_unit = models.CharField(max_length=255, blank=True)
    range_welding_unit = models.CharField(max_length=255, blank=True)


class MechanizedWeldingDetails(TimeStampedModel):
    certificate = models.OneToOneField(WelderOperatorCertificate, on_delete=models.CASCADE, related_name="mechanized_details")
    visual_control = models.CharField(max_length=128, blank=True)
    visual_control_range = models.CharField(max_length=128, blank=True)
    automatic_arc_length_control = models.CharField(max_length=128, blank=True)
    automatic_arc_length_control_range = models.CharField(max_length=128, blank=True)
    automatic_joint_tracking = models.CharField(max_length=128, blank=True)
    automatic_joint_tracking_range = models.CharField(max_length=128, blank=True)
    welding_position = models.CharField(max_length=64, blank=True)
    welding_position_range = models.CharField(max_length=64, blank=True)
    single_run_multi_run = models.CharField(max_length=64, blank=True)
    single_run_multi_run_range = models.CharField(max_length=64, blank=True)
    material_backing = models.CharField(max_length=128, blank=True)
    material_backing_range = models.CharField(max_length=128, blank=True)
    consumable_insert = models.CharField(max_length=128, blank=True)
    consumable_insert_range = models.CharField(max_length=128, blank=True)


class AutomaticWeldingDetails(TimeStampedModel):
    certificate = models.OneToOneField(WelderOperatorCertificate, on_delete=models.CASCADE, related_name="automatic_details")
    joint_sensor = models.CharField(max_length=128, blank=True)
    joint_sensor_range = models.CharField(max_length=128, blank=True)
    arc_sensor_control = models.CharField(max_length=128, blank=True)
    arc_sensor_control_range = models.CharField(max_length=128, blank=True)
    single_run_multi_run = models.CharField(max_length=64, blank=True)
    single_run_multi_run_range = models.CharField(max_length=64, blank=True)
    type_of_welding_unit = models.CharField(max_length=128, blank=True)
    type_of_welding_unit_range = models.CharField(max_length=128, blank=True)


class CertificateResultDocument(TimeStampedModel):
    certificate = models.ForeignKey(WelderOperatorCertificate, on_delete=models.CASCADE, related_name="result_documents")
    title = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=128, blank=True)
    attachment = models.FileField(upload_to="certificate/documents/", null=True, blank=True)
    type = models.CharField(max_length=32, choices=ResultDocumentType.choices, default=ResultDocumentType.OTHER)


class CertificateSignature(TimeStampedModel):
    certificate = models.ForeignKey(WelderOperatorCertificate, on_delete=models.CASCADE, related_name="signatures")
    role = models.CharField(max_length=32, choices=SignatureRole.choices)
    name = models.CharField(max_length=255)
    signature_image = models.FileField(upload_to="certificate/signatures/", null=True, blank=True)
    signed_at = models.DateField(null=True, blank=True)


class CertificateRevalidation(TimeStampedModel):
    certificate = models.ForeignKey(WelderOperatorCertificate, on_delete=models.CASCADE, related_name="revalidations")
    group = models.CharField(max_length=32, choices=RevalidationGroup.choices)
    date = models.DateField(null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    signature = models.CharField(max_length=255, blank=True)
    order_index = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["group", "order_index", "date"]
