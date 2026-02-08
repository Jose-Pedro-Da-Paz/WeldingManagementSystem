import { DashboardPage } from "./pages/DashboardPage";
import { ProcedureForm } from "./components/ProcedureForm";

export function App() {
  return (
    <main className="layout">
      <aside className="sidebar">
        <h1>Welding Qualifier</h1>
        <nav>
          <a>Dashboard</a>
          <a>Procedimentos</a>
          <a>Soldadores</a>
          <a>Qualificações</a>
          <a>Regras Ativas</a>
          <a>Auditoria</a>
        </nav>
      </aside>
      <section className="content">
        <DashboardPage />
        <ProcedureForm />
      </section>
    </main>
  );
}
