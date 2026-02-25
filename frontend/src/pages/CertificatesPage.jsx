import { useMemo, useState } from "react";

const emptyRevalidation = { group: "EMPLOYER_SUPERVISOR", date: "", title: "", signature: "", order_index: 0 };

export function CertificatesPage() {
  const [tab, setTab] = useState(1);
  const [form, setForm] = useState({
    certificate_number: "PTC26.00611.5308",
    ped_nobo: "1029",
    company_name: "Empresa Exemplo",
    welder_name: "Operador Exemplo",
    manufacturer_wps: "D1-WPS-P1-0027",
    id_type: "Cartão Cidadão",
    birth_date: "1989-05-10",
    nationality: "PT",
    code_testing_standard: "EN ISO 14732:2013 & 2014/68/EU",
    functional_knowledge_test_status: "ACCEPTABLE",
    job_knowledge_status: "VERIFIED",
    requalification_basis: "RETEST_6Y",
    approvals_basis: { iso_15614: false, iso_15613: false, iso_9606: false, iso_14732: true },
    process_equipment: { test_piece_process: "145", range_process: "145", test_piece_equipment: "Polysoud PC 600-3", range_equipment: "Polysoud PC 600-3", test_piece_welding_unit: "F-27265", range_welding_unit: "F-27265" },
    mechanized_details: { visual_control: "Direto", visual_control_range: "Direto", automatic_arc_length_control: "Sim", automatic_arc_length_control_range: "Sim", automatic_joint_tracking: "NA", automatic_joint_tracking_range: "NA", welding_position: "PA", welding_position_range: "PA", single_run_multi_run: "Multipasse", single_run_multi_run_range: "Multipasse", material_backing: "Gás backing", material_backing_range: "Gás backing", consumable_insert: "NA", consumable_insert_range: "NA" },
    automatic_details: { joint_sensor: "NA", joint_sensor_range: "NA", arc_sensor_control: "NA", arc_sensor_control_range: "NA", single_run_multi_run: "NA", single_run_multi_run_range: "NA", type_of_welding_unit: "NA", type_of_welding_unit_range: "NA" },
    result_documents: [{ title: "Relatório VT", reference_number: "VT-001", type: "VT" }],
    signatures: [{ role: "EXAMINER", name: "Examinador A", signed_at: "2026-02-08" }, { role: "APPROVED_BY", name: "Approved Manager", signed_at: "2026-02-08" }],
    revalidations: [emptyRevalidation],
  });

  const status = useMemo(() => (form.functional_knowledge_test_status === "NOT_ACCEPTABLE" ? "REJECTED" : "VALID"), [form]);

  const setField = (field, value) => setForm((prev) => ({ ...prev, [field]: value }));

  const updateNested = (key, field, value) => setForm((prev) => ({ ...prev, [key]: { ...prev[key], [field]: value } }));

  const addRevalidation = () => setForm((prev) => ({ ...prev, revalidations: [...prev.revalidations, { ...emptyRevalidation, order_index: prev.revalidations.length }] }));

  const updateRevalidation = (index, field, value) =>
    setForm((prev) => ({ ...prev, revalidations: prev.revalidations.map((item, i) => (i === index ? { ...item, [field]: value } : item)) }));

  const removeRevalidation = (index) =>
    setForm((prev) => ({ ...prev, revalidations: prev.revalidations.filter((_, i) => i !== index).map((item, i) => ({ ...item, order_index: i })) }));

  const exportPdf = async () => {
    alert("Conecte este botão ao endpoint POST /api/certificates/{id}/export-pdf/ após salvar o certificado.");
  };

  return (
    <section>
      <h2>Certificado de Operador de Soldador</h2>
      <p>Status calculado: <strong>{status}</strong></p>
      <div className="tabs">
        {[1, 2, 3, 4, 5, 6].map((n) => (
          <button key={n} className={tab === n ? "active" : ""} onClick={() => setTab(n)}>Aba {n}</button>
        ))}
      </div>

      {tab === 1 && (
        <div className="card grid2">
          <label>Certificate No<input value={form.certificate_number} onChange={(e) => setField("certificate_number", e.target.value)} /></label>
          <label>PED NoBo<input value={form.ped_nobo} onChange={(e) => setField("ped_nobo", e.target.value)} /></label>
          <label>Nome Operador<input value={form.welder_name} onChange={(e) => setField("welder_name", e.target.value)} /></label>
          <label>Empresa<input value={form.company_name} onChange={(e) => setField("company_name", e.target.value)} /></label>
          <label>Tipo ID<input value={form.id_type} onChange={(e) => setField("id_type", e.target.value)} /></label>
          <label>Nacionalidade<input value={form.nationality} onChange={(e) => setField("nationality", e.target.value)} /></label>
        </div>
      )}

      {tab === 2 && (
        <div className="card grid2">
          <label>Code/Testing Standard<textarea value={form.code_testing_standard} onChange={(e) => setField("code_testing_standard", e.target.value)} /></label>
          <label>Manufacturer WPS<input value={form.manufacturer_wps} onChange={(e) => setField("manufacturer_wps", e.target.value)} /></label>
          <label>Functional Knowledge
            <select value={form.functional_knowledge_test_status} onChange={(e) => setField("functional_knowledge_test_status", e.target.value)}>
              <option value="ACCEPTABLE">Acceptable</option>
              <option value="NOT_ACCEPTABLE">Not acceptable</option>
            </select>
          </label>
          <label>Job Knowledge
            <select value={form.job_knowledge_status} onChange={(e) => setField("job_knowledge_status", e.target.value)}>
              <option value="VERIFIED">Verified</option>
              <option value="NOT_VERIFIED">Not verified</option>
            </select>
          </label>
        </div>
      )}

      {tab === 3 && (
        <div className="card grid2">
          <label>Process (Test Piece)<input value={form.process_equipment.test_piece_process} onChange={(e) => updateNested("process_equipment", "test_piece_process", e.target.value)} /></label>
          <label>Process (Range)<input value={form.process_equipment.range_process} onChange={(e) => updateNested("process_equipment", "range_process", e.target.value)} /></label>
          <label>Equipment (Test Piece)<input value={form.process_equipment.test_piece_equipment} onChange={(e) => updateNested("process_equipment", "test_piece_equipment", e.target.value)} /></label>
          <label>Equipment (Range)<input value={form.process_equipment.range_equipment} onChange={(e) => updateNested("process_equipment", "range_equipment", e.target.value)} /></label>
          <label>Welding Unit (Test Piece)<input value={form.process_equipment.test_piece_welding_unit} onChange={(e) => updateNested("process_equipment", "test_piece_welding_unit", e.target.value)} /></label>
          <label>Welding Unit (Range)<input value={form.process_equipment.range_welding_unit} onChange={(e) => updateNested("process_equipment", "range_welding_unit", e.target.value)} /></label>
        </div>
      )}

      {tab === 4 && (
        <div className="card">
          <h3>Base de Aprovação</h3>
          <label><input type="checkbox" checked={form.approvals_basis.iso_15614} onChange={(e) => setField("approvals_basis", { ...form.approvals_basis, iso_15614: e.target.checked })} /> ISO 15614</label>
          <label><input type="checkbox" checked={form.approvals_basis.iso_15613} onChange={(e) => setField("approvals_basis", { ...form.approvals_basis, iso_15613: e.target.checked })} /> ISO 15613</label>
          <label><input type="checkbox" checked={form.approvals_basis.iso_9606} onChange={(e) => setField("approvals_basis", { ...form.approvals_basis, iso_9606: e.target.checked })} /> ISO 9606</label>
          <label><input type="checkbox" checked={form.approvals_basis.iso_14732} onChange={(e) => setField("approvals_basis", { ...form.approvals_basis, iso_14732: e.target.checked })} /> ISO 14732</label>
        </div>
      )}

      {tab === 5 && (
        <div className="card grid2">
          <label>Requalification Basis
            <select value={form.requalification_basis} onChange={(e) => setField("requalification_basis", e.target.value)}>
              <option value="RETEST_6Y">Retest 6 years</option>
              <option value="RETEST_3Y">Retest 3 years</option>
              <option value="OTHER">Other</option>
            </select>
          </label>
          <label>Data de Nascimento<input type="date" value={form.birth_date} onChange={(e) => setField("birth_date", e.target.value)} /></label>
        </div>
      )}

      {tab === 6 && (
        <div className="card">
          <h3>Revalidações</h3>
          {form.revalidations.map((row, index) => (
            <div key={index} className="reval-row">
              <select value={row.group} onChange={(e) => updateRevalidation(index, "group", e.target.value)}>
                <option value="EMPLOYER_SUPERVISOR">Employer/Supervisor</option>
                <option value="DECISION_MAKER">Decision-Maker</option>
              </select>
              <input type="date" value={row.date} onChange={(e) => updateRevalidation(index, "date", e.target.value)} />
              <input placeholder="Título/Função" value={row.title} onChange={(e) => updateRevalidation(index, "title", e.target.value)} />
              <input placeholder="Assinatura" value={row.signature} onChange={(e) => updateRevalidation(index, "signature", e.target.value)} />
              <button onClick={() => removeRevalidation(index)}>Remover</button>
            </div>
          ))}
          <button onClick={addRevalidation}>Adicionar linha</button>
        </div>
      )}

      <article className="preview card">
        <h3>Preview (estrutura do certificado)</h3>
        <p><strong>CERTIFICADO DE OPERADOR DE SOLDADOR / WELDER OPERATOR APPROVAL TEST CERTIFICATE</strong></p>
        <p>No: {form.certificate_number} | PED NoBo: {form.ped_nobo}</p>
        <p>Welder: {form.welder_name} | Company: {form.company_name}</p>
        <p>WPS: {form.manufacturer_wps} | Standard: {form.code_testing_standard}</p>
        <p>Functional Knowledge: {form.functional_knowledge_test_status} | Job Knowledge: {form.job_knowledge_status}</p>
        <button onClick={exportPdf}>Exportar PDF</button>
      </article>
    </section>
  );
}
