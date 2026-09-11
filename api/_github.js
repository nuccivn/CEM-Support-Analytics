const OWNER = "nuccivn";
const REPO = "CEM-Support-Analytics";
const WORKFLOW_FILE = "atualizar-dados.yml";

function token() {
  const t = process.env.GH_ACTIONS_TOKEN;
  if (!t) throw new Error("GH_ACTIONS_TOKEN não configurado nas variáveis de ambiente da Vercel");
  return t;
}

async function gh(path, options) {
  const res = await fetch(`https://api.github.com/repos/${OWNER}/${REPO}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token()}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      ...(options && options.headers),
    },
  });
  return res;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

module.exports = { gh, sleep, WORKFLOW_FILE };
