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
| "Quais clínicas reais existem perto de mim?" | **Consulta a dados externos** — Overpass (OpenStreetMap) num raio, com cache no SQLite | `banco/clinicas_osm.py` |
| "Onde ficam essas clínicas no mapa?" | **Visualização** — Leaflet desenha as coordenadas | `static/app.js → montarMapa` |

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
| Mapa e dados geográficos | Leaflet 1.9 (servido localmente) + tiles do OpenStreetMap; clínicas reais via **Overpass API** (OSM); geocodificação via **Nominatim**; localização via Geolocation API do navegador |
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

No Windows (PowerShell):

```powershell
git clone <url-do-repositorio>
cd patas-perto
.\preparar.ps1            # cria .venv, banco, dataset, treina o modelo e sobe o app
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
| `GET /api/clinicas?especialidade=&hora=HH:MM` | banco | clínicas de demonstração filtradas por especialidade e "aberta no horário" (trata 24h e faixas noturnas) |
| `GET /api/clinicas?lat=&lon=&raio_km=5&hora=&so_abertas=1&meta=1` | dados externos | clínicas **reais** do OpenStreetMap ao redor da posição, com `aberta_agora` (True/False/None) e `meta` (fonte, raio, avisos) |
| `GET /api/geocodificar?q=endereço` | dados externos | endereço/cidade → lat/lon/rótulo (Nominatim) |
| `GET /api/tutores/<id>` · `/historico` | banco | tutor + pet (com lat/lon, centro do mapa); features de compra dos últimos 90 dias |
| `POST /api/compras` `{tutor_id, oferta_id}` | banco | registra a compra — o dado que alimenta a IA |
| `POST /api/recomendar` `{tutor_id, especie, idade_anos, porte, situacao, hora, lat?, lon?, raio_km?}` | **IA + dados** | resposta com `ia` (especialidade, confiança, probabilidades, features usadas) e `banco` (clínicas abertas; reais se lat/lon vierem, com `fonte` e `aviso`) |
| `GET /api/modelo/metricas` | arquivo | conteúdo de `ml/metricas.json` |

---

## 7b. Mapa interativo com clínicas reais

A aba **🗺️ Mapa** mostra a sua posição (📍), anéis de 1 km e 2 km e as clínicas veterinárias (🏥) num raio configurável (2 a 20 km), com filtros de especialidade, horário e "só abertas". O mesmo mapa aparece embutido no resultado da Recomendação e na lista da Emergência. Clicar num marcador abre a ficha: distância, telefone (clicável), site, horário, especialidades, "Como chegar" (Google Maps) e o link do ponto no OpenStreetMap.

**Duas fontes de dados, sempre rotuladas na tela:**

| Situação | Sua posição | Clínicas | Rótulo |
|---|---|---|---|
| Você definiu a localização (📡 GPS do navegador ou endereço digitado → Nominatim) | real | **reais**, do OpenStreetMap via Overpass API (`amenity=veterinary`), com cache de 24 h no SQLite | `dados reais · OpenStreetMap` |
| Sem localização definida, ou sem internet | endereço fictício em Sumaré-SP | 8 clínicas fictícias da tabela `clinicas` | `dados de demonstração` |

Limitações declaradas (e mostradas no app):
- O OpenStreetMap **não registra especialidade**. Ela é **inferida pelo nome/horário** ("odonto" → odontologia, "hospital"/"24h" → emergência, etc.) e marcada com asterisco; sem correspondência, a recomendação mostra todas as clínicas próximas com um aviso. Confirme por telefone.
- Muitas clínicas não têm horário no OSM → aparecem como "horário ?" e não são descartadas pelo filtro "só abertas".
- A cobertura depende do que voluntários mapearam na sua região; o raio pode ser ampliado.
- Leaflet é servido localmente; ruas, Overpass e Nominatim precisam de internet. Sem internet, o app cai automaticamente para os dados de demonstração e o mapa fica quadriculado.
- Lojas e ofertas continuam fictícias (não há fonte pública de preços de petshops).

Atalhos por URL: `/#mapa`, `/#recomendacao`, `/#emergencia`, `/#perfil`; `/#recomendacao/convulsao` já abre a aba com a situação escolhida e dispara a recomendação (útil na apresentação).

## 8. Roteiro sugerido para a apresentação

1. **Problema e ideia** (README §1) — marketplace como fonte de dados; IA × banco.
2. **Dataset** — abrir `ml/gerar_dataset.py`, mostrar as regras e rodar: distribuição das classes e primeiras linhas.
3. **Treino** — rodar `ml/treinar_modelo.py`: acurácia, relatório por classe, matriz de confusão, importâncias.
4. **Sistema ao vivo** — `python app.py`, abrir o app:
   - Loja: buscar "antipulgas", ordenar por preço/distância, abrir o produto (dados vêm do SQLite).
   - Recomendação: pet cão, 6 anos, situação "check-up" → clínico geral (~70%).
   - Comprar 1× **Antipulgas** na Loja e pedir a recomendação de novo → **dermatologia (~85%)**. A compra mudou a IA.
   - Trocar a situação para "convulsão" às 03:00 → emergência + só clínicas 24h/plantão (filtro do banco), já desenhadas no mapa.
   - Aba **Mapa** (`/#mapa`): clicar em "📡 Usar meu GPS" (ou digitar a cidade) → clínicas **reais** ao redor; filtrar por especialidade/horário/raio; clicar numa clínica para centralizar e abrir a ficha com telefone e rota.
5. **Decisões e limitações** — dados sintéticos declarados; ruído de 8%; horário fora do modelo; próximos passos (segmentação de clientes com KMeans para o público-alvo da clínica; persistir o perfil no banco).

Cada integrante deve conseguir explicar: uma tabela do banco, uma coluna do dataset, uma métrica do treino e uma rota da API.

---

## 9. Estrutura do repositório

```
app.py                 API Flask (serve static/ e as rotas /api)
preparar.sh            prepara tudo e sobe o app
preparar.ps1           prepara tudo e sobe o app (Windows/PowerShell)
requirements.txt
banco/schema.sql       DDL do SQLite
banco/criar_banco.py   cria e popula o banco (dados fictícios)
banco/consultas.py     consultas SQL usadas pela API
banco/clinicas_osm.py  clínicas reais (Overpass/OSM), geocodificação (Nominatim), cache
ml/gerar_dataset.py    gera ml/dataset.csv
ml/treinar_modelo.py   treina e salva ml/modelo.pkl + ml/metricas.json
ml/recomendador.py     carrega o modelo e faz a predição
static/index.html      app (markup)
static/style.css       estilos
static/app.js          lógica do front-end (fetch na API, mapa Leaflet)
static/vendor/leaflet  biblioteca de mapas servida localmente
tests/test_api.py      smoke tests
```

Arquivos gerados (`patasperto.db`, `dataset.csv`, `modelo.pkl`, `metricas.json`) ficam fora do Git e são recriados por `preparar.sh` ou `preparar.ps1`.

---

## 10. Considerações

- Dados fictícios, uso exclusivamente acadêmico. Em produção, dados de localização e de saúde do pet exigiriam adequação à **LGPD**.
- As orientações de primeiros socorros e a recomendação de especialidade são educativas e **não substituem** o atendimento veterinário.
