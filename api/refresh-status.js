const { gh, WORKFLOW_FILE } = require("./_github");

// Consulta o status de uma execução do pipeline no GitHub Actions.
// Sem ?run_id=, cai pra run mais recente (best-effort).
module.exports = async function handler(req, res) {
  try {
    const runId = req.query && req.query.run_id;
    const path = runId
      ? `/actions/runs/${runId}`
      : `/actions/workflows/${WORKFLOW_FILE}/runs?per_page=1`;

    const runResp = await gh(path);
    if (!runResp.ok) {
      res.status(502).json({ error: "Falha ao consultar o GitHub Actions", detail: await runResp.text() });
      return;
    }
    const data = await runResp.json();
    const run = runId ? data : (data.workflow_runs || [])[0];

    if (!run) {
      res.status(200).json({ status: "unknown" });
      return;
    }

    res.status(200).json({
      status: run.status, // queued | in_progress | completed
      conclusion: run.conclusion, // success | failure | ... (null se ainda não terminou)
      updated_at: run.updated_at,
      run_id: run.id,
    });
  } catch (err) {
    res.status(500).json({ error: String((err && err.message) || err) });
  }
};
