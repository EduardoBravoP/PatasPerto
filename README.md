# 🐾 PatasPerto

> Encontre produtos para o seu pet nas lojas mais perto de você — inclusive nas que ainda não estão na internet.

**PatasPerto** é um aplicativo que reúne, num só lugar, os produtos de lojas de pet próximas do usuário, permitindo comparar preço e distância. O diferencial é dar visibilidade a **petshops locais que não têm site nem presença online**, cujos produtos hoje só são vistos presencialmente.

Projeto desenvolvido para a disciplina de Projeto Prático Integrado, seguindo a metodologia **Scrum** (Sprint 0 a Sprint 4), com entrega final na 2ª semana de novembro de 2026.

---

## 🎯 Foco desta entrega: Marketplace

O escopo **construído** neste projeto é a feature de **Marketplace**. Ela cobre a jornada principal do usuário:

- **Busca de produtos** sobre uma base de lojas e ofertas.
- **Resultados em grade**, no formato de marketplaces tradicionais (foto, preço, avaliação e prazo).
- **Filtros de ordenação** por **menor preço** e por **mais perto** de você.
- **Página do produto** com fotos, avaliações e informações de entrega/retirada.
- **Página da loja** com os produtos que ela oferece.
- **Painel do lojista** para cadastrar e atualizar produtos (CRUD simples) — é onde o dado do marketplace nasce.

> ℹ️ Nesta versão, os dados de lojas e produtos são **fictícios**, usados para demonstrar a lógica do aplicativo.

---

## 🛰️ Funcionalidade futura (provável): Waze do Pet

Faz parte da **visão** do PatasPerto, mas **está fora do escopo desta entrega** — planejada para versões futuras:

- Coleira inteligente com **GPS e conectividade próprios** (4G/LoRa), enviando a posição direto ao backend.
- **Zona segura**: alerta ao dono quando o pet se afasta de um raio definido.
- **Rota em tempo real** até o pet, atualizada conforme a coleira envia novas posições.

Essa frente envolve hardware e custo de fabricação, por isso é tratada aqui como **roadmap**, não como entrega atual.

---

## 🧩 Arquitetura (visão geral)

Aplicativo cliente consumindo um backend com dois serviços principais — **catálogo** (produtos, preços, lojas) e, futuramente, **rastreamento** — apoiados por um banco de dados e por uma **API de mapas** externa para geolocalização. O painel do lojista alimenta o serviço de catálogo.

```
[App PatasPerto] ──> [API / Backend] ──> [Serviço de Catálogo] ──> [Banco de Dados]
       │                                          ▲
       └──> [API de Mapas]                 [Painel do Lojista]
```

*(A trilha de rastreamento por GPS entra neste mesmo backend em versões futuras.)*

---

## 🛠️ Tecnologias

- **Front-end:** `<preencher>`
- **Back-end:** `<preencher>`
- **Banco de dados:** `<preencher>`
- **API de mapas:** `<preencher>` (ex.: Google Maps / Mapbox)
- **Controle de versão:** Git + GitHub

---

## 👥 Equipe

| Papel | Integrante |
|---|---|
| Product Owner | `<preencher>` |
| Scrum Master | `<preencher>` |
| Dev Team | `<preencher>` |

---

## 🗓️ Roadmap (Scrum)

| Sprint | Período | Entregável principal |
|---|---|---|
| Sprint 0 – Setup | 11/08 a 22/08 | Grupo, papéis, backlog, repositório e base de dados fictícia |
| Sprint 1 | 25/08 a 12/09 | Busca funcionando sobre a base *(1ª apresentação: 12/09)* |
| Sprint 2 | 15/09 a 03/10 | Filtros + página do produto *(2ª apresentação: 03/10)* |
| Sprint 3 | 06/10 a 24/10 | Página da loja + painel do lojista *(3ª apresentação: 24/10)* |
| Sprint 4 – Finalização | 27/10 a 14/11 | Polimento, testes, documentação e **entrega final** |

---

## ▶️ Como executar

> A ser preenchido quando a stack estiver definida.

```bash
# Exemplo:
# git clone https://github.com/<usuario>/patasperto.git
# cd patasperto
# <comandos de instalação e execução>
```

---

## 🔒 Considerações

- Os dados de lojas, produtos e avaliações são **fictícios** e servem apenas para fins de demonstração acadêmica.
- Em um cenário real, o app trataria dados de **localização** e informações de usuários e lojas, exigindo conformidade com a **LGPD**.

---

## 📄 Contexto acadêmico

Projeto acadêmico sem fins comerciais, desenvolvido como trabalho da disciplina de Projeto Prático Integrado — `<instituição / turma>`, 2026.
