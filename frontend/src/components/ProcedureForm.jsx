import { useMemo, useState } from "react";

const statusIcon = {
  VALID: "✔",
  WARNING: "⚠",
  INVALID: "❌",
};

export function ProcedureForm() {
  const [data, setData] = useState({ base_material_group: "FM1", process: "135" });
  const [previous, setPrevious] = useState({ base_material_group: "FM1", process: "141" });

  const status = useMemo(() => {
    if (data.base_material_group !== previous.base_material_group) {
      return "INVALID";
    }
    if (data.process === "135") {
      return "WARNING";
    }
    return "VALID";
  }, [data, previous]);

  return (
    <article className="card">
      <h3>Simulação de avaliação</h3>
      <label>
        Grupo de material base
        <select
          value={data.base_material_group}
          onChange={(event) => setData((prev) => ({ ...prev, base_material_group: event.target.value }))}
        >
          <option value="FM1">FM1</option>
          <option value="FM2">FM2</option>
          <option value="FM3">FM3</option>
        </select>
      </label>
      <label>
        Processo
        <select value={data.process} onChange={(event) => setData((prev) => ({ ...prev, process: event.target.value }))}>
          <option value="135">135</option>
          <option value="141">141</option>
        </select>
      </label>
      <p className={`status ${status.toLowerCase()}`}>
        {statusIcon[status]} Status atual: {status}
      </p>
      <small>Campos dinâmicos serão dirigidos pelo endpoint /api/rules/evaluate/ no backend.</small>
    </article>
  );
}
