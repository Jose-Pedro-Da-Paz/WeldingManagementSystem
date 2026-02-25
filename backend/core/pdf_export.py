from __future__ import annotations

from io import BytesIO

from core.models import RevalidationGroup, WelderOperatorCertificate


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_page_stream(lines: list[str]) -> str:
    stream_lines = ["BT", "/F1 10 Tf", "40 800 Td", "14 TL"]
    for idx, line in enumerate(lines):
        text_cmd = f"({_escape(line)}) Tj"
        stream_lines.append(text_cmd if idx == 0 else f"T* {text_cmd}")
    stream_lines.append("ET")
    return "\n".join(stream_lines)


def generate_certificate_pdf(certificate: WelderOperatorCertificate) -> bytes:
    employer_rows = certificate.revalidations.filter(group=RevalidationGroup.EMPLOYER_SUPERVISOR).order_by("order_index")
    decision_rows = certificate.revalidations.filter(group=RevalidationGroup.DECISION_MAKER).order_by("order_index")

    pages_data = [
        [
            "CERTIFICADO DE OPERADOR DE SOLDADOR / WELDER OPERATOR APPROVAL TEST CERTIFICATE",
            f"Certificate No: {certificate.certificate_number}  PED NoBo: {certificate.ped_nobo}",
            f"Operator: {certificate.welder_name} | Company: {certificate.company_name}",
            f"ID Type: {certificate.id_type} | Birth/Nationality: {certificate.birth_date} / {certificate.nationality}",
            f"Manufacturer WPS: {certificate.manufacturer_wps}",
            f"Functional Knowledge: {certificate.functional_knowledge_test_status}",
            f"Job Knowledge: {certificate.job_knowledge_status}",
            f"Code/Standard: {certificate.code_testing_standard}",
            "Main Tables: Process / Equipment / Welding Unit + Mechanized/Automatic details",
            "Page 1/4",
        ],
        [
            "Approval Basis (4.1): ISO 15614 / ISO 15613 / ISO 9606 / ISO 14732",
            f"Selected basis: {certificate.approvals_basis}",
            "Qualification results documents:",
            *[f"- {doc.type}: {doc.title} ({doc.reference_number})" for doc in certificate.result_documents.all()[:8]],
            f"Requalification basis: {certificate.requalification_basis} | Valid until: {certificate.valid_until}",
            f"Examiner / Approved by signatures count: {certificate.signatures.count()}",
            "Revalidation tables continue on pages 3 and 4",
            "Page 2/4",
        ],
        [
            "Revalidation by Employer/Supervisor",
            *[f"- {row.date} | {row.title} | {row.signature}" for row in employer_rows[:20]],
            "Page 3/4",
        ],
        [
            "Revalidation by Decision-Maker",
            *[f"- {row.date} | {row.title} | {row.signature}" for row in decision_rows[:20]],
            "Page 4/4",
        ],
    ]

    buffer = BytesIO()
    objects = []

    objects.append("1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj")

    kids_refs = [f"{3 + i*2} 0 R" for i in range(4)]
    objects.append(f"2 0 obj << /Type /Pages /Count 4 /Kids [{' '.join(kids_refs)}] >> endobj")

    for i, page_lines in enumerate(pages_data):
        page_obj_num = 3 + i * 2
        content_obj_num = page_obj_num + 1
        stream = _build_page_stream(page_lines)
        objects.append(
            f"{page_obj_num} 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 11 0 R >> >> /Contents {content_obj_num} 0 R >> endobj"
        )
        objects.append(
            f"{content_obj_num} 0 obj << /Length {len(stream.encode('utf-8'))} >> stream\n{stream}\nendstream endobj"
        )

    objects.append("11 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj")

    header = "%PDF-1.4\n"
    buffer.write(header.encode("utf-8"))
    xref_positions = [0]
    for obj in objects:
        xref_positions.append(buffer.tell())
        buffer.write((obj + "\n").encode("utf-8"))

    xref_start = buffer.tell()
    buffer.write(f"xref\n0 {len(xref_positions)}\n".encode("utf-8"))
    buffer.write(b"0000000000 65535 f \n")
    for pos in xref_positions[1:]:
        buffer.write(f"{pos:010d} 00000 n \n".encode("utf-8"))

    buffer.write(
        (
            f"trailer << /Size {len(xref_positions)} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode("utf-8")
    )
    return buffer.getvalue()
