/* ============================================================
   PatasPerto — front-end (app.js)
   Os dados NÃO estão mais chumbados aqui: lojas, produtos,
   ofertas e clínicas vêm da API Flask (app.py) que lê o SQLite.
   Seções: Loja · Recomendação (IA) · Emergência · Perfil
   ============================================================ */

const API = "";            // mesma origem (a página é servida pelo Flask)
const TUTOR_ID = 1;        // tutor demo cadastrado no banco

const ILUSTRACOES = {
  racaoCao: '<svg viewBox="0 0 100 100"><rect x="28" y="26" width="44" height="58" rx="6" fill="#D98A3D"/><path d="M28 26 L40 19 L60 19 L72 26 Z" fill="#B5702B"/><circle cx="50" cy="56" r="6" fill="#5A3A1A"/><circle cx="42" cy="48" r="3" fill="#5A3A1A"/><circle cx="50" cy="46" r="3" fill="#5A3A1A"/><circle cx="58" cy="48" r="3" fill="#5A3A1A"/></svg>',
  racaoGato: '<svg viewBox="0 0 100 100"><rect x="28" y="26" width="44" height="58" rx="6" fill="#3E8FC0"/><path d="M28 26 L40 19 L60 19 L72 26 Z" fill="#2E6E96"/><ellipse cx="47" cy="56" rx="12" ry="7" fill="#fff"/><path d="M58 56 L67 49 L67 63 Z" fill="#fff"/><circle cx="42" cy="54" r="1.6" fill="#2E6E96"/></svg>',
  bola: '<svg viewBox="0 0 100 100"><circle cx="50" cy="52" r="26" fill="#E24B4A"/><line x1="24" y1="52" x2="76" y2="52" stroke="#B23636" stroke-width="3"/><ellipse cx="50" cy="52" rx="10" ry="26" fill="none" stroke="#B23636" stroke-width="3"/><circle cx="42" cy="44" r="6" fill="#fff" opacity="0.55"/></svg>',
  caminha: '<svg viewBox="0 0 100 100"><ellipse cx="50" cy="74" rx="32" ry="11" fill="#B98E57"/><ellipse cx="50" cy="70" rx="26" ry="8" fill="#E7D3A8"/><path d="M30 68 q20 -17 40 0 q-20 7 -40 0 Z" fill="#8A7A63"/><circle cx="35" cy="63" r="6" fill="#8A7A63"/><path d="M31 59 l1 -5 4 3 Z" fill="#8A7A63"/><path d="M39 59 l-1 -5 -4 3 Z" fill="#8A7A63"/></svg>',
  areia: '<svg viewBox="0 0 100 100"><rect x="30" y="26" width="40" height="56" rx="6" fill="#8FB3C7"/><path d="M30 26 L41 20 L59 20 L70 26 Z" fill="#6E93A8"/><g fill="#4F6B7D"><circle cx="42" cy="52" r="2"/><circle cx="50" cy="48" r="2"/><circle cx="58" cy="54" r="2"/><circle cx="46" cy="60" r="2"/><circle cx="55" cy="62" r="2"/><circle cx="50" cy="56" r="2"/></g></svg>',
  petisco: '<svg viewBox="0 0 100 100"><g transform="rotate(-28 50 50)" fill="#E8C98A" stroke="#C9A461" stroke-width="2"><circle cx="32" cy="45" r="7"/><circle cx="32" cy="57" r="7"/><circle cx="68" cy="45" r="7"/><circle cx="68" cy="57" r="7"/><rect x="32" y="44" width="36" height="14" rx="4"/></g></svg>'
,
  antipulgas: '<svg viewBox="0 0 100 100"><path d="M40 20 h20 v14 l8 10 v34 a8 8 0 0 1 -8 8 h-20 a8 8 0 0 1 -8 -8 v-34 l8 -10 Z" fill="#7BC47F"/><rect x="40" y="14" width="20" height="8" rx="2" fill="#4E8F52"/><path d="M36 56 h28" stroke="#fff" stroke-width="3"/><circle cx="50" cy="70" r="6" fill="#fff"/></svg>',
  shampoo: '<svg viewBox="0 0 100 100"><rect x="34" y="34" width="32" height="50" rx="8" fill="#6FB1E8"/><rect x="42" y="18" width="16" height="18" rx="3" fill="#3C7FB8"/><rect x="45" y="12" width="10" height="8" rx="2" fill="#2E6693"/><ellipse cx="50" cy="60" rx="10" ry="12" fill="#fff" opacity=".7"/></svg>',
  dental: '<svg viewBox="0 0 100 100"><path d="M30 30 q20 -14 40 0 q6 22 -4 46 q-6 8 -10 -6 q-4 -12 -12 0 q-4 14 -10 6 q-10 -24 -4 -46 Z" fill="#fff" stroke="#8FC9A0" stroke-width="4"/><path d="M40 40 q10 -6 20 0" stroke="#8FC9A0" stroke-width="3" fill="none"/></svg>',
  escova: '<svg viewBox="0 0 100 100"><rect x="46" y="30" width="10" height="56" rx="5" fill="#F0A24A"/><rect x="40" y="14" width="22" height="20" rx="4" fill="#fff" stroke="#C9A461" stroke-width="2"/><g fill="#E24B4A"><rect x="43" y="17" width="3" height="14"/><rect x="49" y="17" width="3" height="14"/><rect x="55" y="17" width="3" height="14"/></g></svg>',
  suplemento: '<svg viewBox="0 0 100 100"><rect x="30" y="30" width="40" height="54" rx="8" fill="#F2C14E"/><rect x="34" y="22" width="32" height="12" rx="3" fill="#C9962B"/><rect x="36" y="46" width="28" height="22" rx="3" fill="#fff"/><path d="M42 57 h16 M50 49 v16" stroke="#E24B4A" stroke-width="4"/></svg>',
  racaoSenior: '<svg viewBox="0 0 100 100"><rect x="28" y="26" width="44" height="58" rx="6" fill="#8E6BBF"/><path d="M28 26 L40 19 L60 19 L72 26 Z" fill="#6A4D94"/><text x="50" y="62" text-anchor="middle" font-size="22" font-weight="bold" fill="#fff" font-family="Arial">7+</text></svg>',
  racaoLight: '<svg viewBox="0 0 100 100"><rect x="28" y="26" width="44" height="58" rx="6" fill="#5DC1A0"/><path d="M28 26 L40 19 L60 19 L72 26 Z" fill="#3E9A7C"/><path d="M38 62 q12 -22 24 0" stroke="#fff" stroke-width="4" fill="none"/><circle cx="50" cy="48" r="4" fill="#fff"/></svg>',
  tapete: '<svg viewBox="0 0 100 100"><rect x="18" y="30" width="64" height="44" rx="6" fill="#DDE9F7" stroke="#9DB9DA" stroke-width="3"/><path d="M26 38 h48 M26 46 h48 M26 54 h48 M26 62 h48" stroke="#B8CFE9" stroke-width="2"/><ellipse cx="62" cy="58" rx="9" ry="6" fill="#F2D77A"/></svg>'
};

/* ---- Classes de domínio (as mesmas do protótipo; agora hidratadas via API) ---- */
class Loja {
  constructor(d) { Object.assign(this, { id: d.id, nome: d.nome, distanciaKm: d.distancia_km, nota: d.nota, qtdAvaliacoes: d.qtd_avaliacoes, endereco: d.endereco }); }
}
class Produto {
  constructor(d) { Object.assign(this, { id: d.id, nome: d.nome, categoria: d.categoria, grupoIa: d.grupo_ia, img: d.img, descricao: d.descricao, caracteristicas: d.caracteristicas, comentarios: d.comentarios }); }
  mediaAvaliacoes() { return this.comentarios.length ? this.comentarios.reduce((s, c) => s + c.nota, 0) / this.comentarios.length : 0; }
}
class Oferta {
  constructor(id, produto, loja, preco, entrega) { Object.assign(this, { id, produto, loja, preco, entrega }); }
  frete() { return this.preco >= 100 ? 0 : Math.round((8.90 + this.loja.distanciaKm * 4) * 100) / 100; }
  prazoEntrega() { const d = this.loja.distanciaKm; return d < 1 ? "1 dia útil" : d < 2 ? "2 dias úteis" : "3 dias úteis"; }
  tempoRetirada() { return Math.max(2, Math.round(this.loja.distanciaKm * 4)) + " min de carro"; }
}
class Catalogo {
  constructor() { this.ofertas = []; }
  adicionar(o) { this.ofertas.push(o); }
  buscar(termo) { const t = this._n(termo); return t === "" ? this.ofertas.slice() : this.ofertas.filter(o => this._n(o.produto.nome).includes(t) || this._n(o.produto.categoria).includes(t)); }
  ofertasDoProduto(p) { return this.ofertas.filter(o => o.produto.id === p.id); }
  _n(t) { return t.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim(); }
}

const catalogo = new Catalogo();
let metricasModelo = null;

/* ---- Utilidades ---- */
const $ = id => document.getElementById(id);
const grade = $("grade"), info = $("info"), campo = $("campoBusca");
const telas = { lista: $("telaLista"), produto: $("telaProduto"), emergencia: $("telaEmergencia"), recomendacao: $("telaRecomendacao"), perfil: $("telaPerfil") };
let termoAtual = "", ordemAtual = "preco";

const fmt = v => "R$ " + v.toFixed(2).replace(".", ",");
const num1 = v => v.toFixed(1).replace(".", ",");
const pct = p => Math.round(p * 100) + "%";
const iconeEntrega = e => e.startsWith("Retira") ? "🏪" : "🚚";
const estrelas = n => "★".repeat(n) + "☆".repeat(5 - n);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const horaAgora = () => new Date().toTimeString().slice(0, 5);

function toast(msg, ms = 2600) {
  const t = $("toast"); t.textContent = msg; t.classList.remove("oculto");
  clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.add("oculto"), ms);
}

async function api(caminho, opcoes) {
  const r = await fetch(API + caminho, opcoes ? { headers: { "Content-Type": "application/json" }, ...opcoes } : undefined);
  const corpo = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(corpo.erro || ("HTTP " + r.status));
  return corpo;
}

const MSG_SEM_API = 'Não foi possível falar com o back-end. Inicie a API com <code>python app.py</code> e abra <b>http://127.0.0.1:5000</b>.';

/* ---- Carregamento dos dados (a base agora vem do SQLite via API) ---- */
async function carregarDados() {
  try {
    const ofertas = await api("/api/ofertas");
    const lojas = {}, produtos = {};
    ofertas.forEach(o => {
      lojas[o.loja.id] = lojas[o.loja.id] || new Loja(o.loja);
      produtos[o.produto.id] = produtos[o.produto.id] || new Produto(o.produto);
      catalogo.adicionar(new Oferta(o.id, produtos[o.produto.id], lojas[o.loja.id], o.preco, o.entrega));
    });
    render();
  } catch (e) {
    info.textContent = "";
    grade.innerHTML = '<div class="aviso-erro" style="grid-column:1/-1">' + MSG_SEM_API + '</div>';
  }
  api("/api/modelo/metricas").then(m => { metricasModelo = m; }).catch(() => {});
}

/* ---- Lista / grade ---- */
function render() {
  let res = catalogo.buscar(termoAtual);
  if (ordemAtual === "preco") res.sort((a, b) => a.preco - b.preco);
  else res.sort((a, b) => a.loja.distanciaKm - b.loja.distanciaKm);

  let menor = null, perto = null;
  res.forEach(o => {
    if (!menor || o.preco < menor.preco) menor = o;
    if (!perto || o.loja.distanciaKm < perto.loja.distanciaKm) perto = o;
  });

  grade.innerHTML = "";
  if (res.length === 0) {
    info.textContent = "";
    grade.innerHTML = '<p class="vazio">Nenhum produto encontrado para “' + esc(termoAtual) + '”. Tente “ração”, “antipulgas” ou “dental”.</p>';
    return;
  }
  info.textContent = res.length + " ofertas perto de você" + (termoAtual.trim() ? " para “" + termoAtual + "”" : "") + " · dados do banco SQLite";

  res.forEach(o => {
    let badges = "";
    if (o === menor) badges += '<span class="badge verde">Menor preço</span>';
    if (o === perto) badges += '<span class="badge azul">Mais perto</span>';
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML =
      (badges ? '<div class="badges">' + badges + '</div>' : '') +
      '<div class="imgbox">' + (ILUSTRACOES[o.produto.img] || "") + '</div>' +
      '<div class="corpo">' +
        '<p class="preco">' + fmt(o.preco) + '</p>' +
        '<p class="titulo">' + esc(o.produto.nome) + '</p>' +
        '<p class="aval">★ ' + num1(o.loja.nota) + ' <span class="qtd">(' + o.loja.qtdAvaliacoes + ')</span></p>' +
        '<p class="entrega">' + iconeEntrega(o.entrega) + ' ' + o.entrega + ' · ' + num1(o.loja.distanciaKm) + ' km</p>' +
        '<p class="loja">' + esc(o.loja.nome) + '</p>' +
      '</div>';
    card.addEventListener("click", () => abrirProduto(o));
    grade.appendChild(card);
  });
}

/* ---- Página do produto ---- */
function abrirProduto(o) {
  const prod = o.produto, frete = o.frete(), media = prod.mediaAvaliacoes();
  const freteTxt = frete === 0 ? "Grátis" : fmt(frete);

  const tabelaCarac = '<table class="tabela">' + prod.caracteristicas.map(c => '<tr><td class="rot">' + esc(c[0]) + '</td><td>' + esc(c[1]) + '</td></tr>').join('') + '</table>';
  const listaComent = prod.comentarios.map(c =>
    '<div class="coment"><div class="topo"><span class="autor">' + esc(c.autor) + '</span><span class="estrelas">' + estrelas(c.nota) + '</span></div><p class="txt">' + esc(c.texto) + '</p></div>').join('');
  const painelAval = '<div class="resumo-aval"><span class="big">' + num1(media) + '</span><span><span class="estr">' + estrelas(Math.round(media)) + '</span><br><small>' + prod.comentarios.length + ' avaliações</small></span></div>' + listaComent;

  const outras = catalogo.ofertasDoProduto(prod).filter(x => x !== o).sort((a, b) => a.preco - b.preco);
  const outrasHtml = outras.length ? '<div class="outras"><h3>Outras lojas com este produto</h3>' +
    outras.map((x, i) => '<div class="oferta-lin" data-idx="' + i + '"><div class="mini">' + ILUSTRACOES[x.produto.img] + '</div>' +
      '<div class="ol-nome">' + esc(x.loja.nome) + '<small>📍 ' + num1(x.loja.distanciaKm) + ' km · ' + esc(x.loja.endereco) + '</small></div>' +
      '<div class="ol-preco">' + fmt(x.preco) + '</div></div>').join("") + '</div>' : "";

  telas.produto.innerHTML =
    '<button class="voltar" id="btVoltar">← Voltar aos resultados</button>' +
    '<div class="det-img">' + ILUSTRACOES[prod.img] + '</div>' +
    '<p class="det-cat">' + esc(prod.categoria) + '</p>' +
    '<h2 class="det-titulo">' + esc(prod.nome) + '</h2>' +
    '<p class="det-aval">★ ' + num1(media) + ' <span class="qtd">(' + prod.comentarios.length + ' avaliações)</span></p>' +
    '<p class="det-preco">' + fmt(o.preco) + '</p>' +
    '<div class="secao"><h3>Vendido por</h3><p><b>' + esc(o.loja.nome) + '</b> · ★ ' + num1(o.loja.nota) + '</p>' +
      '<p class="local">📍 ' + esc(o.loja.endereco) + ' — a ' + num1(o.loja.distanciaKm) + ' km de você</p></div>' +
    '<div class="opcoes">' +
      '<div class="opcao"><h4>🏪 Retirar na loja</h4><p class="destaque">Retire hoje</p><p>' + esc(o.loja.endereco) + '</p><p>A ' + num1(o.loja.distanciaKm) + ' km (~' + o.tempoRetirada() + ')</p><p>Sem custo de entrega</p></div>' +
      '<div class="opcao"><h4>🚚 Receber em casa</h4><p class="destaque">Chega em ' + o.prazoEntrega() + '</p><p>Frete: ' + freteTxt + '</p>' +
        (frete === 0 ? '<p>Frete grátis acima de R$ 100</p>' : '<p>Calculado pela distância da loja</p>') + '</div>' +
    '</div>' +
    '<div class="acoes"><button class="comprar" id="btComprar">Comprar agora</button><button class="carrinho" id="btCarrinho">Adicionar ao carrinho</button></div>' +
    '<p class="explica">🛒 Cada compra é gravada no banco e passa a fazer parte do seu histórico — é esse dado que alimenta a recomendação da IA.</p>' +
    '<div class="abas"><button class="aba ativa" data-aba="desc">Descrição</button><button class="aba" data-aba="carac">Características</button><button class="aba" data-aba="aval">Avaliações (' + prod.comentarios.length + ')</button></div>' +
    '<div class="painel" id="painel-desc"><p class="secao" style="margin:0">' + esc(prod.descricao) + '</p></div>' +
    '<div class="painel oculto" id="painel-carac">' + tabelaCarac + '</div>' +
    '<div class="painel oculto" id="painel-aval">' + painelAval + '</div>' + outrasHtml;

  $("btVoltar").addEventListener("click", () => mostrar("lista"));
  $("btComprar").addEventListener("click", () => comprar(o));
  $("btCarrinho").addEventListener("click", () => toast("Item adicionado ao carrinho (simulação)."));
  telas.produto.querySelectorAll(".oferta-lin").forEach((el, i) => el.addEventListener("click", () => abrirProduto(outras[i])));
  telas.produto.querySelectorAll(".aba").forEach(b => b.addEventListener("click", () => {
    telas.produto.querySelectorAll(".aba").forEach(x => x.classList.remove("ativa"));
    telas.produto.querySelectorAll(".painel").forEach(x => x.classList.add("oculto"));
    b.classList.add("ativa"); telas.produto.querySelector("#painel-" + b.dataset.aba).classList.remove("oculto");
  }));
  mostrar("produto");
}

async function comprar(o) {
  const bt = $("btComprar"); bt.disabled = true; bt.textContent = "Registrando…";
  try {
    const r = await api("/api/compras", { method: "POST", body: JSON.stringify({ tutor_id: TUTOR_ID, oferta_id: o.id }) });
    const f = r.historico.features;
    toast("✅ Compra registrada em " + o.loja.nome + ". Histórico: " + r.historico.total_compras_janela + " compras nos últimos 90 dias (" + f.compras_mes + "/mês).", 4000);
  } catch (e) { toast("Erro ao registrar compra: " + e.message); }
  bt.disabled = false; bt.textContent = "Comprar agora";
}

/* ================= PERFIL (tutor + pet) ================= */
const PERFIL_PADRAO = { nome: "Ana Ribeiro", email: "ana.ribeiro@exemplo.com", telefone: "(19) 98888-0000", endereco: "Rua das Acácias, 300 · Centro",
  petNome: "Thor", especie: "cao", idade: 6, porte: "medio", foto: "🐶" };
function lerPerfil() { try { return { ...PERFIL_PADRAO, ...JSON.parse(localStorage.getItem("perfil") || "{}") }; } catch { return { ...PERFIL_PADRAO }; } }
function salvarPerfil(p) { try { localStorage.setItem("perfil", JSON.stringify(p)); } catch {} atualizarConta(); }
function atualizarConta() { $("contaNome").textContent = lerPerfil().nome.split(" ")[0] || "Perfil"; }

function renderPerfil() {
  const p = lerPerfil();
  const opt = (v, atual, rotulo) => '<option value="' + v + '"' + (v === atual ? ' selected' : '') + '>' + rotulo + '</option>';
  telas.perfil.innerHTML =
    '<div class="perfil-topo"><div class="foto-perfil" id="fotoPet">' + p.foto + '</div><p>Toque na foto para trocar</p></div>' +
    '<div class="bloco"><h3>👤 Tutor</h3><div class="form-grid">' +
      '<div><label class="rotulo">Nome</label><input class="campo" id="pNome" value="' + esc(p.nome) + '"></div>' +
      '<div><label class="rotulo">E-mail</label><input class="campo" id="pEmail" value="' + esc(p.email) + '"></div>' +
      '<div><label class="rotulo">Telefone</label><input class="campo" id="pTel" value="' + esc(p.telefone) + '"></div>' +
      '<div><label class="rotulo">Endereço</label><input class="campo" id="pEnd" value="' + esc(p.endereco) + '"></div></div></div>' +
    '<div class="bloco"><h3>🐾 Pet</h3><div class="form-grid">' +
      '<div><label class="rotulo">Nome do pet</label><input class="campo" id="pPet" value="' + esc(p.petNome) + '"></div>' +
      '<div><label class="rotulo">Espécie</label><select class="campo" id="pEsp">' + opt("cao", p.especie, "Cão") + opt("gato", p.especie, "Gato") + '</select></div>' +
      '<div><label class="rotulo">Idade (anos)</label><input class="campo" id="pIdade" type="number" min="0" max="25" step="0.5" value="' + p.idade + '"></div>' +
      '<div><label class="rotulo">Porte</label><select class="campo" id="pPorte">' + opt("pequeno", p.porte, "Pequeno") + opt("medio", p.porte, "Médio") + opt("grande", p.porte, "Grande") + '</select></div></div>' +
      '<p class="explica">Espécie, idade e porte entram como variáveis do modelo de recomendação.</p></div>' +
    '<div class="bloco" id="blocoHist"><h3>🛒 Histórico de compras <span class="rot-db">consulta ao banco</span></h3><p class="origem">últimos 90 dias · tabela compras do SQLite</p><p class="vazio-clin">Carregando…</p></div>' +
    '<button class="btn-prim" id="btSalvarPerfil">Salvar perfil</button>';

  $("fotoPet").addEventListener("click", () => { const f = ["🐶", "🐱", "🐕", "🐈", "🐾"]; p.foto = f[(f.indexOf(p.foto) + 1) % f.length]; $("fotoPet").textContent = p.foto; });
  $("pEsp").addEventListener("change", e => { if (e.target.value === "gato") $("pPorte").value = "pequeno"; });
  $("btSalvarPerfil").addEventListener("click", () => {
    salvarPerfil({ nome: $("pNome").value, email: $("pEmail").value, telefone: $("pTel").value, endereco: $("pEnd").value,
      petNome: $("pPet").value, especie: $("pEsp").value, idade: parseFloat($("pIdade").value) || 0, porte: $("pPorte").value, foto: p.foto });
    toast("Perfil salvo (persistido no navegador).");
  });
  api("/api/tutores/" + TUTOR_ID + "/historico").then(h => {
    const f = h.features;
    const linhas = Object.keys(f).filter(k => k.startsWith("gasto_") && f[k] > 0).map(k => '<tr><td class="rot">' + k.replace("gasto_", "R$/mês em ") + '</td><td>' + fmt(f[k]) + '</td></tr>').join("");
    $("blocoHist").querySelector(".vazio-clin").outerHTML =
      '<table class="tabela"><tr><td class="rot">Compras na janela</td><td>' + h.total_compras_janela + ' (' + f.compras_mes + ' por mês)</td></tr>' + linhas + '</table>' +
      (h.recentes.length ? '<p class="explica">Últimas: ' + h.recentes.slice(0, 4).map(r => esc(r.nome) + ' (' + r.data + ')').join(' · ') + '</p>' : '');
  }).catch(() => { $("blocoHist").querySelector(".vazio-clin").innerHTML = MSG_SEM_API; });
}

/* ================= RECOMENDAÇÃO (IA + banco) ================= */
const SITUACOES = [
  ["checkup", "Consulta de rotina / check-up"], ["coceira", "Coceira, pele irritada"], ["mau_halito", "Mau hálito, tártaro"],
  ["mancando", "Mancando, dificuldade para andar"], ["ganho_peso", "Ganho de peso"], ["vomito", "Vômito ocasional"],
  ["engasgo", "Engasgo"], ["sangramento", "Sangramento / corte"], ["toxico", "Ingestão de algo tóxico"], ["convulsao", "Convulsão"], ["insolacao", "Superaquecimento (insolação)"],
];
const NOME_SIT = Object.fromEntries(SITUACOES);

function renderRecomendacao(situacaoInicial) {
  const p = lerPerfil();
  telas.recomendacao.innerHTML =
    '<h2 class="det-titulo">🤖 Que atendimento o ' + esc(p.petNome) + ' precisa?</h2>' +
    '<p class="secao" style="margin:6px 0 0">O modelo de IA combina o perfil do pet, a situação relatada e o <b>seu histórico de compras na loja</b> para indicar a especialidade veterinária. Depois, o banco lista as clínicas abertas.</p>' +
    '<div class="bloco"><div class="form-grid">' +
      '<div><label class="rotulo">Espécie</label><select class="campo" id="rEsp"><option value="cao"' + (p.especie === "cao" ? " selected" : "") + '>Cão</option><option value="gato"' + (p.especie === "gato" ? " selected" : "") + '>Gato</option></select></div>' +
      '<div><label class="rotulo">Idade (anos)</label><input class="campo" id="rIdade" type="number" min="0" max="25" step="0.5" value="' + p.idade + '"></div>' +
      '<div><label class="rotulo">Porte</label><select class="campo" id="rPorte">' + ["pequeno", "medio", "grande"].map(v => '<option value="' + v + '"' + (v === p.porte ? " selected" : "") + '>' + v[0].toUpperCase() + v.slice(1) + '</option>').join("") + '</select></div>' +
      '<div><label class="rotulo">Horário da consulta</label><input class="campo" id="rHora" type="time" value="' + horaAgora() + '"></div>' +
    '</div>' +
    '<label class="rotulo">Situação do pet</label><select class="campo" id="rSit">' + SITUACOES.map(([v, r]) => '<option value="' + v + '"' + (v === situacaoInicial ? " selected" : "") + '>' + r + '</option>').join("") + '</select>' +
    '<button class="btn-prim" id="btRecomendar">Pedir recomendação</button></div>' +
    '<div id="resRec"></div>';
  $("btRecomendar").addEventListener("click", pedirRecomendacao);
}

async function pedirRecomendacao() {
  const bt = $("btRecomendar"), res = $("resRec");
  bt.disabled = true; bt.textContent = "Consultando o modelo…";
  const corpo = { tutor_id: TUTOR_ID, especie: $("rEsp").value, idade_anos: parseFloat($("rIdade").value) || 0, porte: $("rPorte").value, situacao: $("rSit").value, hora: $("rHora").value || horaAgora() };
  try {
    const r = await api("/api/recomendar", { method: "POST", body: JSON.stringify(corpo) });
    res.innerHTML = htmlIA(r.ia, corpo) + htmlClinicas(r.banco) + htmlRodapeModelo();
  } catch (e) {
    res.innerHTML = '<div class="aviso-erro">' + (e.message.startsWith("HTTP") || e.message.includes("fetch") ? MSG_SEM_API : esc(e.message)) + '</div>';
  }
  bt.disabled = false; bt.textContent = "Pedir recomendação";
  res.scrollIntoView({ behavior: "smooth", block: "start" });
}

function htmlIA(ia, corpo) {
  const f = ia.features_usadas;
  const gastos = Object.keys(f).filter(k => k.startsWith("gasto_")).sort((a, b) => f[b] - f[a]).slice(0, 4).filter(k => f[k] > 0)
    .map(k => k.replace("gasto_", "") + " " + fmt(f[k]) + "/mês").join(" · ");
  const barras = ia.probabilidades.map((x, i) => '<div class="barra-prob' + (i === 0 ? " top" : "") + '"><span>' + esc(x.nome.split(" (")[0]) + '</span><div class="trilho"><div class="fill" style="width:' + (x.p * 100) + '%"></div></div><span class="pct">' + pct(x.p) + '</span></div>').join("");
  return '<div class="bloco"><h3>Especialidade indicada <span class="rot-ia">IA · Random Forest</span></h3><p class="origem">' + esc(ia.origem) + '</p>' +
    '<div class="resultado"><span class="big">' + esc(ia.especialidade_nome) + '</span><span class="conf">confiança ' + pct(ia.confianca) + '</span></div>' +
    '<div class="barras">' + barras + '</div>' +
    '<p class="explica"><b>O que o modelo recebeu:</b> ' + (corpo.especie === "cao" ? "cão" : "gato") + ', ' + corpo.idade_anos + ' anos, porte ' + corpo.porte + ', situação “' + esc(NOME_SIT[corpo.situacao] || corpo.situacao) + '”; ' +
    'do banco: ' + ia.historico_compras.total_compras_janela + ' compras em ' + ia.historico_compras.janela_dias + ' dias (' + f.compras_mes + '/mês)' + (gastos ? ' — ' + gastos : '') + '.</p></div>';
}

function htmlClinicas(b) {
  const lista = b.clinicas.length ? b.clinicas.map(c =>
    '<div class="clinica"><div class="cl-info"><span class="cl-nome">' + esc(c.nome) + '</span>' +
    '<small>📍 ' + esc(c.endereco) + ' — ' + num1(c.distancia_km) + ' km</small><small>📞 ' + esc(c.telefone) + ' · ' + (c.aberto_24h ? 'aberta 24h' : c.abre + '–' + c.fecha) + '</small></div>' +
    (c.aberto_24h ? '<span class="tag24">24h</span>' : '<span class="tag24">aberta</span>') + '</div>').join("") :
    '<p class="vazio-clin">Nenhuma clínica com essa especialidade aberta às ' + b.hora_consultada + '. Tente outro horário ou veja as clínicas de emergência 24h.</p>';
  return '<div class="bloco"><h3>Clínicas abertas às ' + b.hora_consultada + ' <span class="rot-db">consulta ao banco</span></h3>' +
    '<p class="origem">filtro SQL: especialidade = ' + esc(b.especialidade_filtrada) + ' e horário dentro do funcionamento · ' + esc(b.origem) + '</p>' + lista + '</div>';
}

function htmlRodapeModelo() {
  if (!metricasModelo) return "";
  const m = metricasModelo;
  return '<p class="rodape-modelo">Modelo: ' + esc(m.algoritmo) + ' · treinado com ' + m.n_linhas + ' linhas sintéticas · acurácia no teste ' + pct(m.acuracia) + ' (validação cruzada ' + pct(m.cv_media) + ')</p>';
}

/* ================= EMERGÊNCIA (primeiros socorros + clínicas) ================= */
const vetFamilia = { nome: "Dra. Marina Alves", clinica: "Clínica VidaPet", telefone: "(19) 99999-0001", distanciaKm: 0.6 };
const primeirosSocorros = [
  { id: "engasgo", icone: "😮‍💨", titulo: "Engasgo",
    passos: ["Mantenha a calma e contenha o animal com cuidado para não se machucar.", "Abra a boca e verifique se o objeto está visível; retire apenas se conseguir alcançá-lo sem empurrar.", "Em cães pequenos, segure-o de cabeça para baixo por instantes; em cães grandes, eleve as patas traseiras.", "Se não resolver em segundos, leve imediatamente ao veterinário."],
    alerta: "Não coloque a mão fundo na garganta às cegas — você pode empurrar o objeto ainda mais." },
  { id: "sangramento", icone: "🩹", titulo: "Sangramento / corte",
    passos: ["Pressione o local com um pano limpo ou gaze por alguns minutos.", "Se encharcar, não retire o pano: coloque outro por cima e continue pressionando.", "Mantenha o animal o mais calmo e imóvel possível.", "Procure atendimento se o sangramento for intenso ou não parar."], alerta: "" },
  { id: "toxico", icone: "☠️", titulo: "Ingestão de algo tóxico",
    passos: ["Afaste o animal da substância e tente identificar o que foi ingerido.", "NÃO induza o vômito sem orientação do veterinário.", "Guarde a embalagem ou o rótulo do produto para mostrar ao profissional.", "Ligue para o veterinário ou vá à clínica imediatamente."],
    alerta: "Alguns produtos causam mais dano se vomitados — só induza o vômito se o veterinário orientar." },
  { id: "convulsao", icone: "⚡", titulo: "Convulsão",
    passos: ["Afaste móveis e objetos ao redor para o animal não se machucar.", "Não coloque a mão na boca dele.", "Observe e anote quanto tempo dura a crise.", "Depois da crise, deixe-o em ambiente calmo e procure o veterinário."], alerta: "" },
  { id: "insolacao", icone: "🌡️", titulo: "Superaquecimento (insolação)",
    passos: ["Leve o animal para um local fresco e à sombra.", "Molhe o corpo com água em temperatura ambiente (nunca gelada).", "Ofereça água fresca em pequena quantidade.", "Procure o veterinário — insolação é uma emergência."],
    alerta: "Água muito gelada pode causar choque térmico; use água natural." },
];
const tEmg = telas.emergencia;

function wireEmg() {
  const bv = $("btVoltarEmg"); if (bv) bv.addEventListener("click", renderEmergenciaHome);
  tEmg.querySelectorAll("[data-clinicas]").forEach(b => b.addEventListener("click", renderClinicasEmergencia));
  tEmg.querySelectorAll("[data-sos]").forEach(b => b.addEventListener("click", renderSOS));
  tEmg.querySelectorAll("[data-rec]").forEach(b => b.addEventListener("click", () => { mostrar("recomendacao"); renderRecomendacao(b.dataset.rec); }));
}

function renderEmergenciaHome() {
  tEmg.innerHTML =
    '<div class="aviso">⚠️ As orientações abaixo são educativas e não substituem o atendimento veterinário. Em caso de emergência, procure um profissional.</div>' +
    '<div class="sos-card"><h3>🚑 Emergência veterinária</h3><p>Seu pet está passando mal? Acione o veterinário da família ou encontre a clínica mais próxima.</p>' +
      '<button class="btn-sos" data-sos>Acionar veterinário da família</button><button class="btn-sec" data-clinicas>Ver clínicas próximas</button></div>' +
    '<h3 class="emg-h3">Primeiros socorros — o que fazer</h3><div class="sit-lista">' +
      primeirosSocorros.map(s => '<div class="sit-item" data-id="' + s.id + '"><span class="ic">' + s.icone + '</span><span class="nm">' + s.titulo + '</span></div>').join('') + '</div>';
  wireEmg();
  tEmg.querySelectorAll(".sit-item").forEach(el => el.addEventListener("click", () => renderSituacao(el.dataset.id)));
}

function renderSituacao(id) {
  const s = primeirosSocorros.find(x => x.id === id);
  tEmg.innerHTML =
    '<button class="voltar" id="btVoltarEmg">← Voltar</button><h2 class="det-titulo">' + s.icone + ' ' + s.titulo + '</h2>' +
    '<ol class="passos">' + s.passos.map(p => '<li>' + p + '</li>').join('') + '</ol>' +
    (s.alerta ? '<div class="alerta-passo">⚠️ ' + s.alerta + '</div>' : '') +
    '<button class="btn-sos" data-sos style="margin-top:18px">Acionar veterinário da família</button>' +
    '<button class="btn-sec" data-rec="' + s.id + '">🤖 Ver recomendação da IA para esta situação</button>' +
    '<button class="btn-sec" data-clinicas>Ver clínicas próximas</button>';
  wireEmg();
}

function renderSOS() {
  const p = lerPerfil();
  tEmg.innerHTML =
    '<button class="voltar" id="btVoltarEmg">← Voltar</button><h2 class="det-titulo">🚑 Acionar veterinário</h2>' +
    '<p class="secao" style="margin:8px 0 0">Envie um alerta para <b>' + vetFamilia.nome + '</b> (' + vetFamilia.clinica + ') com as primeiras informações. Ela poderá ir até você.</p>' +
    '<label class="rotulo">Nome do pet</label><input class="campo" id="fPet" value="' + esc(p.petNome) + '">' +
    '<label class="rotulo">Espécie</label><select class="campo" id="fEspecie"><option' + (p.especie === "cao" ? " selected" : "") + '>Cão</option><option' + (p.especie === "gato" ? " selected" : "") + '>Gato</option><option>Outro</option></select>' +
    '<label class="rotulo">Situação</label><select class="campo" id="fSituacao">' + primeirosSocorros.map(s => '<option>' + s.titulo + '</option>').join('') + '<option>Outra</option></select>' +
    '<label class="rotulo">Observações</label><textarea class="campo" id="fObs" rows="3" placeholder="Descreva rapidamente o que está acontecendo"></textarea>' +
    '<button class="btn-sos" id="btEnviar" style="margin-top:16px">Enviar alerta</button><button class="btn-sec" data-clinicas>Prefiro levar — ver clínicas próximas</button>';
  wireEmg(); $("btEnviar").addEventListener("click", enviarSOS);
}

function enviarSOS() {
  const pet = $("fPet").value || "Seu pet", esp = $("fEspecie").value, sit = $("fSituacao").value, obs = $("fObs").value || "—";
  const tempo = Math.round(10 + vetFamilia.distanciaKm * 4);
  tEmg.innerHTML =
    '<div class="confirma"><div class="check">✅</div><h3>Alerta enviado</h3><p class="secao" style="margin:0 auto;max-width:440px"><b>' + vetFamilia.nome + '</b> (' + vetFamilia.clinica + ') foi notificada e está a caminho.<br>Chegada estimada: ~' + tempo + ' min.</p></div>' +
    '<div class="secao"><h3>Informações enviadas ao veterinário</h3><table class="tabela"><tr><td class="rot">Pet</td><td>' + esc(pet) + ' (' + esc(esp) + ')</td></tr><tr><td class="rot">Situação</td><td>' + esc(sit) + '</td></tr><tr><td class="rot">Observações</td><td>' + esc(obs) + '</td></tr></table></div>' +
    '<button class="btn-sec" data-clinicas>Caso não seja possível, ver clínicas próximas</button><button class="btn-sec" id="btVoltarEmg">Voltar ao início</button>';
  wireEmg();
}

async function renderClinicasEmergencia() {
  const hora = horaAgora();
  tEmg.innerHTML = '<button class="voltar" id="btVoltarEmg">← Voltar</button><h2 class="det-titulo">🏥 Clínicas de emergência abertas agora <span class="rot-db">consulta ao banco</span></h2>' +
    '<p class="secao" style="margin:8px 0 14px">Filtro: especialidade “emergencia”, abertas às ' + hora + ', ordenadas pela distância.</p><div id="listaClin"><p class="vazio-clin">Carregando…</p></div>';
  wireEmg();
  try {
    const cl = await api("/api/clinicas?especialidade=emergencia&hora=" + hora);
    $("listaClin").innerHTML = cl.map(c => '<div class="clinica"><div class="cl-info"><span class="cl-nome">' + esc(c.nome) + (c.id === 1 ? ' · sua clínica' : '') + '</span>' +
      '<small>📍 ' + esc(c.endereco) + ' — ' + num1(c.distancia_km) + ' km</small><small>📞 ' + esc(c.telefone) + '</small></div>' + (c.aberto_24h ? '<span class="tag24">24h</span>' : '<span class="tag24">aberta</span>') + '</div>').join('');
  } catch { $("listaClin").innerHTML = '<div class="aviso-erro">' + MSG_SEM_API + '</div>'; }
}

/* ---- Navegação ---- */
const navs = { lista: $("navLoja"), recomendacao: $("navRec"), emergencia: $("navEmg") };
function mostrar(nome) {
  Object.entries(telas).forEach(([k, el]) => { el.style.display = k === nome ? "block" : "none"; });
  Object.entries(navs).forEach(([k, el]) => el.classList.toggle("ativo", k === nome));
  window.scrollTo(0, 0);
}
navs.lista.addEventListener("click", () => mostrar("lista"));
navs.recomendacao.addEventListener("click", () => { mostrar("recomendacao"); renderRecomendacao("checkup"); });
navs.emergencia.addEventListener("click", () => { mostrar("emergencia"); renderEmergenciaHome(); });
$("btConta").addEventListener("click", () => { mostrar("perfil"); renderPerfil(); });
$("logo").addEventListener("click", () => mostrar("lista"));
$("botaoBusca").addEventListener("click", () => { termoAtual = campo.value; render(); });
campo.addEventListener("keydown", e => { if (e.key === "Enter") { termoAtual = campo.value; render(); } });
document.querySelectorAll(".chip").forEach(chip => chip.addEventListener("click", () => {
  document.querySelectorAll(".chip").forEach(c => c.classList.remove("ativo")); chip.classList.add("ativo"); ordemAtual = chip.dataset.ord; render();
}));

atualizarConta();
carregarDados();
