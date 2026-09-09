# 🐾 PatasPerto

> Marketplace de produtos pet que conecta o cliente às lojas mais próximas — inclusive petshops de bairro sem presença online — e usa os **dados gerados pela loja** para alimentar um modelo de **Machine Learning** que recomenda a especialidade veterinária que o pet precisa.

Projeto acadêmico (Projeto Prático Integrado, 2026). Dados de lojas, produtos, clínicas e compras são **fictícios**.

---

## 1. Ideia central

A loja não é enfeite: é a **fonte de dados da IA**. Cada compra registrada no marketplace vira histórico de comportamento (o que o tutor compra, com que frequência). O modelo aprende padrões nesse comportamento e, junto com o perfil do pet e a situação relatada, indica **qual especialidade veterinária** o cliente deve procurar. Os dois lados se beneficiam: o cliente recebe orientação; a clínica recebe demanda qualificada.

### IA × consulta a banco (a distinção que sustenta o projeto)

| Pergunta | Quem responde | Onde |
|---|---|---|
| "Que especialidade meu pet precisa?" | **IA** — Random Forest treinado com dados sintéticos | `ml/treinar_modelo.py`, `ml/recomendador.py` |
| "Quais clínicas dessa especialidade estão abertas às 23h?" | **Banco** — filtro SQL por especialidade e horário | `banco/consultas.py → listar_clinicas` |
| "Quanto esse tutor gasta por mês em produtos de pele?" | **Banco** — agregação SQL das compras | `banco/consultas.py → historico_tutor` |

A resposta da rota `/api/recomendar` e a tela do app separam explicitamente os dois blocos (`ia` e `banco`).

---

## 2. Arquitetura (3 camadas + treino offline)

```
 ┌──────────────────────────────┐        ┌──────────────────────────────┐
 │  FRONT-END  (static/)        │  fetch │  BACK-END  (app.py, Flask)   │
 │  HTML + CSS + JS, SVGs       │ ─────► │  GET  /api/ofertas           │
 │  Loja · Recomendação ·       │ ◄───── │  GET  /api/clinicas          │
 │  Emergência · Perfil         │  JSON  │  POST /api/compras           │
 └──────────────────────────────┘        │  POST /api/recomendar  [IA]  │
                                         └──────────┬───────────┬───────┘
                                                    │           │
                             ┌──────────────────────▼──┐   ┌────▼──────────────────────┐
                             │ DADOS  banco/patasperto.db│   │ MODELO  ml/modelo.pkl     │
                             │ SQLite: lojas, produtos, │   │ Pipeline scikit-learn:    │
                             │ ofertas, clínicas,       │   │ OneHotEncoder +           │
                             │ tutores, pets, compras   │   │ RandomForestClassifier    │
                             └──────────────────────────┘   └────────────▲──────────────┘
                                                                         │ treino offline (1x)
                                    ml/gerar_dataset.py → dataset.csv → ml/treinar_modelo.py
```

---

## 3. Tecnologias

| Camada | Tecnologia |
|---|---|
| Front-end | HTML, CSS, JavaScript puro; ilustrações em SVG inline |
| Back-end / API | Python 3.12 + Flask |
| Banco de dados | SQLite (módulo `sqlite3` da biblioteca padrão) |
| Machine Learning | scikit-learn (Random Forest), pandas, numpy, joblib |
| Ambiente | `uv` (ou `venv`) — ver `requirements.txt` |
| Versionamento | Git + GitHub |

---

## 4. Como executar

```bash
git clone <url-do-repositorio> && cd patas-perto
bash preparar.sh          # cria .venv, banco, dataset, treina o modelo e sobe o app
# abra http://127.0.0.1:5000
```

Passo a passo equivalente (útil para demonstrar cada etapa na apresentação):

```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install -r requirements.txt

python banco/criar_banco.py      # 1. banco SQLite com dados fictícios (+ tutor demo com compras)
python ml/gerar_dataset.py       # 2. dataset sintético: 2.500 linhas, seed 42, 8% de ruído
python ml/treinar_modelo.py      # 3. treina o Random Forest e imprime as métricas
python app.py                    # 4. API + app em http://127.0.0.1:5000
pytest tests/                    # (opcional) 6 smoke tests da API
```

> O GitHub Pages não roda Python: na apresentação o back-end roda **localmente**.

---

## 5. Dataset sintético (`ml/gerar_dataset.py`)

Não há dado real, então o dataset é gerado por regras plausíveis ("o que um veterinário esperaria") com ruído de 8% no rótulo e semente fixa. Isso é uma **escolha declarada** do projeto. Uma linha = um cliente/pet no momento em que pede recomendação.

| Coluna | Tipo | Valores | Papel |
|---|---|---|---|
| `especie` | categórica | cao, gato | perfil do pet |
| `idade_anos` | numérica | 0,5 – 15 | perfil do pet |
| `porte` | categórica | pequeno, medio, grande | perfil do pet |
| `compras_mes` | numérica | 0 – 6 | comportamento de compra (loja) |
| `gasto_alimentacao`, `gasto_petisco`, `gasto_higiene`, `gasto_brinquedo`, `gasto_pele`, `gasto_bucal`, `gasto_articular` | numérica | R$/mês | comportamento de compra (loja) |
| `situacao` | categórica | checkup, coceira, mau_halito, mancando, ganho_peso, vomito, engasgo, sangramento, toxico, convulsao, insolacao | motivo relatado |
| **`especialidade`** | categórica (alvo) | emergencia, dermatologia, odontologia, ortopedia, nutricao, clinico_geral | **o que o modelo prevê** |

Regras de rotulagem (em ordem de prioridade): situação de emergência → `emergencia`; coceira ou gasto alto em pele → `dermatologia`; mau hálito ou gasto alto em bucal → `odontologia`; mancando, gasto alto em articular ou cão grande idoso → `ortopedia`; ganho de peso ou muito petisco com compra frequente → `nutricao`; senão → `clinico_geral`. 30% dos clientes recebem um "perfil de compra" concentrado em um grupo (ex.: compra muito antipulgas) sem relatar sintoma — é o que faz o modelo aprender que **a compra sozinha já carrega sinal**.

**O horário não é feature**: não muda a especialidade que o pet precisa, só filtra clínicas abertas (consulta a banco).

---

## 6. Modelo e resultados (`ml/treinar_modelo.py`)

- `Pipeline(ColumnTransformer(OneHotEncoder nas categóricas + passthrough nas numéricas), RandomForestClassifier(n_estimators=200, random_state=42))`
- Divisão 80/20 estratificada + validação cruzada 5 folds.
- Métricas do último treino (impressas no terminal e salvas em `ml/metricas.json`):

| Métrica | Valor |
|---|---|
| Acurácia no teste (500 linhas) | **~0,91** |
| Validação cruzada (5 folds) | ~0,91 ± 0,02 |
| Teto teórico com 8% de ruído | ~0,92 |

Importância das variáveis: `situacao` (~46%) domina; em seguida `gasto_pele`, `gasto_bucal`, `gasto_articular` (~10% cada) — ou seja, o comportamento de compra na loja responde por cerca de 1/3 da decisão do modelo.

Por que Random Forest: lida com categóricas e numéricas juntas, é robusto a ruído e a escalas diferentes, dá importância das variáveis (explicabilidade) e probabilidades por classe (usadas como "confiança" no app).

---

## 7. API (`app.py`)

| Rota | Tipo | Descrição |
|---|---|---|
| `GET /` | estático | serve o app (`static/index.html`) |
| `GET /api/ofertas` | banco | ofertas com produto, características, avaliações e loja |
| `GET /api/clinicas?especialidade=&hora=HH:MM` | banco | clínicas filtradas por especialidade e "aberta no horário" (trata 24h e faixas noturnas) |
| `GET /api/tutores/<id>` · `/historico` | banco | tutor + pet; features de compra dos últimos 90 dias |
| `POST /api/compras` `{tutor_id, oferta_id}` | banco | registra a compra — o dado que alimenta a IA |
| `POST /api/recomendar` `{tutor_id, especie, idade_anos, porte, situacao, hora}` | **IA + banco** | resposta com `ia` (especialidade, confiança, probabilidades, features usadas) e `banco` (clínicas abertas) |
| `GET /api/modelo/metricas` | arquivo | conteúdo de `ml/metricas.json` |

---

## 8. Roteiro sugerido para a apresentação

1. **Problema e ideia** (README §1) — marketplace como fonte de dados; IA × banco.
2. **Dataset** — abrir `ml/gerar_dataset.py`, mostrar as regras e rodar: distribuição das classes e primeiras linhas.
3. **Treino** — rodar `ml/treinar_modelo.py`: acurácia, relatório por classe, matriz de confusão, importâncias.
4. **Sistema ao vivo** — `python app.py`, abrir o app:
   - Loja: buscar "antipulgas", ordenar por preço/distância, abrir o produto (dados vêm do SQLite).
   - Recomendação: pet cão, 6 anos, situação "check-up" → clínico geral (~70%).
   - Comprar 1× **Antipulgas** na Loja e pedir a recomendação de novo → **dermatologia (~85%)**. A compra mudou a IA.
   - Trocar a situação para "convulsão" às 03:00 → emergência + só clínicas 24h/plantão (filtro do banco).
5. **Decisões e limitações** — dados sintéticos declarados; ruído de 8%; horário fora do modelo; próximos passos (segmentação de clientes com KMeans para o público-alvo da clínica; persistir o perfil no banco).

Cada integrante deve conseguir explicar: uma tabela do banco, uma coluna do dataset, uma métrica do treino e uma rota da API.

---

## 9. Estrutura do repositório

```
app.py                 API Flask (serve static/ e as rotas /api)
preparar.sh            prepara tudo e sobe o app
requirements.txt
banco/schema.sql       DDL do SQLite
banco/criar_banco.py   cria e popula o banco (dados fictícios)
banco/consultas.py     consultas SQL usadas pela API
ml/gerar_dataset.py    gera ml/dataset.csv
ml/treinar_modelo.py   treina e salva ml/modelo.pkl + ml/metricas.json
ml/recomendador.py     carrega o modelo e faz a predição
static/index.html      app (markup)
static/style.css       estilos
static/app.js          lógica do front-end (fetch na API)
tests/test_api.py      smoke tests
```

Arquivos gerados (`patasperto.db`, `dataset.csv`, `modelo.pkl`, `metricas.json`) ficam fora do Git e são recriados por `preparar.sh`.

---

## 10. Considerações

- Dados fictícios, uso exclusivamente acadêmico. Em produção, dados de localização e de saúde do pet exigiriam adequação à **LGPD**.
- As orientações de primeiros socorros e a recomendação de especialidade são educativas e **não substituem** o atendimento veterinário.
