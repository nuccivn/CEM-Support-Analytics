const { gh, sleep, WORKFLOW_FILE } = require("./_github");

// Períodos que o seletor do painel oferece. Whitelist fechada porque este
// endpoint é público (qualquer um com o link pode chamar) - não repassamos
// texto livre do cliente pro workflow_dispatch.
const DIAS_PERMITIDOS = new Set([30, 90, 180, 270, 365]);

// Dispara uma nova execução do pipeline (scripts 01-06 + push do output/)
// via GitHub Actions. Qualquer pessoa com o link do painel pode chamar
// isso - não há autenticação de usuário aqui, só o token de servidor que
// fala com o GitHub. Ver README.md > "Atualização automática".
module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "method not allowed" });
    return;
  }

  const diasPedido = Number((req.body && req.body.dias) || 365);
  const dias = DIAS_PERMITIDOS.has(diasPedido) ? diasPedido : 365;

  try {
    const emAndamentoResp = await gh(`/actions/workflows/${WORKFLOW_FILE}/runs?per_page=10`);
    if (!emAndamentoResp.ok) {
      res.status(502).json({ error: "Falha ao consultar o GitHub Actions", detail: await emAndamentoResp.text() });
      return;
    }
    const emAndamentoData = await emAndamentoResp.json();
    const jaRodando = (emAndamentoData.workflow_runs || []).find(
      (r) => r.status === "in_progress" || r.status === "queued"
    );
    if (jaRodando) {
      res.status(200).json({ status: "already_running", run_id: jaRodando.id, dias });
      return;
    }

    const dispatchedAt = new Date();
    const dispatchResp = await gh(`/actions/workflows/${WORKFLOW_FILE}/dispatches`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ref: "main", inputs: { dias: String(dias) } }),
    });
    if (dispatchResp.status !== 204) {
      res.status(502).json({ error: "Falha ao disparar o workflow", detail: await dispatchResp.text() });
      return;
    }

    // O GitHub demora alguns segundos pra listar a run recém-disparada;
    // tenta achar o id dela pra o cliente acompanhar uma run específica
    // (em vez da run mais recente qualquer, que pode ser outra).
    let novaRun = null;
    for (let i = 0; i < 6 && !novaRun; i++) {
      await sleep(1500);
      const runsResp = await gh(`/actions/workflows/${WORKFLOW_FILE}/runs?event=workflow_dispatch&per_page=5`);
      if (!runsResp.ok) continue;
      const runsData = await runsResp.json();
      novaRun = (runsData.workflow_runs || []).find((r) => new Date(r.created_at) >= dispatchedAt);
    }

    res.status(200).json({ status: "started", run_id: novaRun ? novaRun.id : null, dias });
  } catch (err) {
    res.status(500).json({ error: String((err && err.message) || err) });
  }
};
