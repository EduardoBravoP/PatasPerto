"""
Cria o banco SQLite do PatasPerto e o popula com dados fictícios.

Uso:  python banco/criar_banco.py
Saída: banco/patasperto.db (recriado do zero a cada execução)

Os dados de lojas, produtos, ofertas e clínicas são FICTÍCIOS (demonstração
acadêmica). Os 6 primeiros produtos e as 5 lojas foram migrados do index.html
original; os demais produtos foram acrescentados para dar sinal ao modelo de IA
(grupo_ia: pele, bucal, articular...).
"""
import os
import random
import sqlite3
from datetime import date, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DB = os.path.join(AQUI, "patasperto.db")
CAMINHO_SCHEMA = os.path.join(AQUI, "schema.sql")

# ---------------------------------------------------------------- lojas
LOJAS = [
    (1, "Petshop do Zé",   0.8, 4.8, 120, "Rua das Acácias, 120 · Centro"),
    (2, "Agropet Sumaré",  0.4, 4.6, 83,  "Av. Brasil, 455 · Jd. Bela Vista"),
    (3, "Cantinho Animal", 1.2, 4.9, 210, "Rua Ipê, 78 · Vila Nova"),
    (4, "Mundo Pet",       2.1, 4.7, 64,  "Av. da Saudade, 1020 · Jd. Europa"),
    (5, "Casa dos Bichos", 1.7, 4.5, 96,  "Rua São João, 33 · Centro"),
]

# ------------------------------------------------------------- produtos
# (id, nome, categoria, grupo_ia, img, descricao, caracteristicas, avaliacoes)
PRODUTOS = [
    (1, "Ração Golden Fórmula Cães 15 kg", "Cães", "alimentacao", "racaoCao",
     "Ração super premium para cães adultos de todas as raças. Fórmula com proteínas de alta qualidade que ajudam na saúde da pele e da pelagem. Pacote de 15 kg.",
     [("Marca", "Golden"), ("Indicado para", "Cães adultos"), ("Peso", "15 kg"), ("Sabor", "Frango e carne"), ("Linha", "Super premium")],
     [("Ana", 5, "Meu cachorro adorou, o pelo ficou mais brilhante."), ("Marcos", 4, "Boa ração pelo preço. Entrega rápida."), ("Júlia", 5, "Sempre compro, ótima qualidade.")]),
    (2, "Ração Whiskas Gatos 10 kg", "Gatos", "alimentacao", "racaoGato",
     "Ração para gatos adultos, rica em nutrientes essenciais para a saúde felina. Sabor carne. Embalagem de 10 kg.",
     [("Marca", "Whiskas"), ("Indicado para", "Gatos adultos"), ("Peso", "10 kg"), ("Sabor", "Carne")],
     [("Paula", 4, "Minha gata comeu bem, mas o saco veio um pouco amassado."), ("Rafael", 5, "Preço justo e ela adora.")]),
    (3, "Bolinha Maciça para Cães", "Brinquedos", "brinquedo", "bola",
     "Bolinha maciça e resistente, ideal para brincadeiras de buscar e morder. Material atóxico e durável.",
     [("Material", "Borracha atóxica"), ("Tamanho", "Médio"), ("Indicado para", "Cães de porte pequeno e médio")],
     [("Bruno", 5, "Resistente, meu dog não conseguiu destruir."), ("Carla", 4, "Boa, mas um pouco menor do que eu imaginava.")]),
    (4, "Caminha para Gato Aconchego", "Conforto", "brinquedo", "caminha",
     "Caminha macia e aconchegante para gatos, com forro confortável e base antiderrapante. Fácil de lavar.",
     [("Material", "Poliéster"), ("Tamanho", "Grande"), ("É lavável", "Sim"), ("À prova d'água", "Não"), ("Indicado para", "Gatos e cães de porte médio")],
     [("Fernanda", 5, "Super macia, meu gato dorme o dia todo nela."), ("Diego", 4, "Confortável e fácil de lavar."), ("Lu", 5, "Ótimo custo-benefício.")]),
    (5, "Areia Sanitária para Gatos 4 kg", "Gatos", "higiene", "areia",
     "Areia sanitária higiênica com alto poder de absorção e controle de odores. Pacote de 4 kg.",
     [("Tipo", "Grão fino"), ("Peso", "4 kg"), ("Controle de odor", "Sim")],
     [("Sandra", 4, "Absorve bem, mas rende um pouco menos que eu esperava."), ("Tiago", 5, "Praticamente sem cheiro, recomendo.")]),
    (6, "Petisco Bifinho para Cães", "Petiscos", "petisco", "petisco",
     "Petisco em tiras macias, ótimo para o dia a dia e para o treinamento. Sabor carne.",
     [("Marca", "Bifinho"), ("Sabor", "Carne"), ("Peso", "60 g"), ("Indicado para", "Todas as raças")],
     [("Renata", 5, "Meu cão faz tudo por esse petisco."), ("Igor", 4, "Bom para usar no treino.")]),
    # ---- produtos acrescentados: dão sinal para a IA ----
    (7, "Antipulgas e Carrapatos Cães 10–25 kg", "Saúde", "pele", "antipulgas",
     "Pipeta antipulgas e anticarrapatos de ação prolongada (30 dias). Para cães de 10 a 25 kg.",
     [("Tipo", "Pipeta tópica"), ("Duração", "30 dias"), ("Indicado para", "Cães de 10 a 25 kg")],
     [("Vera", 5, "Resolveu a coceira dele em dois dias."), ("Caio", 4, "Funciona bem, cheiro forte na aplicação.")]),
    (8, "Shampoo Dermatológico Hipoalergênico 500 ml", "Higiene", "pele", "shampoo",
     "Shampoo para pele sensível, com aveia e aloe vera. Alivia coceira e irritações. Cães e gatos.",
     [("Volume", "500 ml"), ("Indicado para", "Pele sensível"), ("Sem perfume", "Sim")],
     [("Marta", 5, "Único que não irrita a pele da minha cadela."), ("Leo", 4, "Bom, rende bastante.")]),
    (9, "Petisco Dental Greenies Cães 170 g", "Petiscos", "bucal", "dental",
     "Petisco mastigável que ajuda a reduzir tártaro e mau hálito. Um por dia.",
     [("Peso", "170 g"), ("Função", "Higiene bucal"), ("Indicado para", "Cães acima de 7 kg")],
     [("Bia", 5, "O hálito melhorou muito."), ("Rodrigo", 4, "Ele adora, e o dentista aprovou.")]),
    (10, "Kit Escova + Pasta Dental Pet", "Higiene", "bucal", "escova",
     "Kit com escova de dedo, escova longa e pasta dental sabor carne, sem flúor. Para cães e gatos.",
     [("Itens", "2 escovas + pasta 90 g"), ("Sabor", "Carne"), ("Sem flúor", "Sim")],
     [("Gustavo", 4, "Demorou para acostumar, mas funciona."), ("Nina", 5, "Pasta com gosto bom, ele aceita.")]),
    (11, "Suplemento Articular Condroitina 60 comp.", "Saúde", "articular", "suplemento",
     "Suplemento com glucosamina e condroitina para saúde das articulações de cães adultos e idosos.",
     [("Quantidade", "60 comprimidos"), ("Indicado para", "Cães adultos e idosos"), ("Uso", "1 comprimido/dia por 10 kg")],
     [("Helena", 5, "Meu labrador de 9 anos voltou a subir a escada."), ("Pedro", 4, "Bom, mas caro.")]),
    (12, "Ração Sênior Cães 7+ 12 kg", "Cães", "alimentacao", "racaoSenior",
     "Ração para cães acima de 7 anos, com condroitina e menor teor calórico. Pacote de 12 kg.",
     [("Marca", "Premier"), ("Indicado para", "Cães a partir de 7 anos"), ("Peso", "12 kg"), ("Linha", "Sênior")],
     [("Cris", 5, "Ele está mais ativo desde que mudei."), ("Otávio", 4, "Boa ração, grãos pequenos.")]),
    (13, "Ração Light Gatos Castrados 3 kg", "Gatos", "alimentacao", "racaoLight",
     "Ração com menos gordura para gatos castrados com tendência ao sobrepeso. Pacote de 3 kg.",
     [("Marca", "Royal Canin"), ("Indicado para", "Gatos castrados"), ("Peso", "3 kg"), ("Linha", "Light")],
     [("Mila", 5, "Ela emagreceu 400 g em dois meses."), ("Jonas", 4, "Cara, mas funciona.")]),
    (14, "Tapete Higiênico 30 un.", "Higiene", "higiene", "tapete",
     "Tapete higiênico super absorvente com gel e atrativo canino. Pacote com 30 unidades.",
     [("Quantidade", "30 unidades"), ("Tamanho", "60 × 60 cm"), ("Atrativo", "Sim")],
     [("Sofia", 4, "Absorve bem."), ("Renan", 5, "Sem vazamento, ótimo.")]),
]

# ---------------------------------------------------------------- ofertas
# (produto_id, loja_id, preco, entrega)
OFERTAS = [
    (1, 1, 189.90, "Retira hoje"), (1, 2, 194.00, "Retira hoje"), (1, 3, 199.90, "Chega quarta"), (1, 4, 205.00, "Chega quinta"),
    (2, 2, 128.90, "Retira hoje"), (2, 1, 132.00, "Retira hoje"), (2, 5, 135.50, "Chega quarta"),
    (3, 1, 19.90, "Retira hoje"), (3, 3, 17.50, "Chega quarta"), (3, 5, 18.90, "Retira hoje"),
    (4, 4, 89.90, "Chega quinta"), (4, 3, 94.90, "Chega quarta"), (4, 5, 99.00, "Retira hoje"),
    (5, 2, 24.90, "Retira hoje"), (5, 3, 22.50, "Chega quarta"), (5, 1, 26.00, "Retira hoje"),
    (6, 2, 9.90, "Retira hoje"), (6, 3, 8.50, "Chega quarta"), (6, 4, 10.90, "Chega quinta"),
    (7, 1, 64.90, "Retira hoje"), (7, 4, 59.90, "Chega quinta"), (7, 5, 62.00, "Retira hoje"),
    (8, 3, 39.90, "Chega quarta"), (8, 2, 42.50, "Retira hoje"),
    (9, 1, 34.90, "Retira hoje"), (9, 3, 32.90, "Chega quarta"), (9, 4, 36.00, "Chega quinta"),
    (10, 5, 29.90, "Retira hoje"), (10, 2, 31.90, "Retira hoje"),
    (11, 1, 119.90, "Retira hoje"), (11, 4, 109.90, "Chega quinta"),
    (12, 3, 179.90, "Chega quarta"), (12, 1, 185.00, "Retira hoje"),
    (13, 2, 89.90, "Retira hoje"), (13, 5, 92.50, "Chega quarta"),
    (14, 2, 45.90, "Retira hoje"), (14, 3, 43.90, "Chega quarta"), (14, 5, 47.00, "Retira hoje"),
]

# --------------------------------------------------------------- clínicas
# (id, nome, endereco, distancia_km, telefone, abre, fecha, aberto_24h, [especialidades])
CLINICAS = [
    (1, "Clínica VidaPet", "Rua das Flores, 200 · Centro", 0.6, "(19) 99999-0001", "00:00", "23:59", 1,
     ["clinico_geral", "emergencia", "dermatologia", "nutricao"]),
    (2, "Clínica AmorPet", "Av. Brasil, 455 · Jd. Bela Vista", 0.9, "(19) 99999-0002", "08:00", "18:00", 0,
     ["clinico_geral", "odontologia", "dermatologia"]),
    (3, "PetCare Emergências", "Av. Central, 890 · Jd. Europa", 1.5, "(19) 99999-0003", "00:00", "23:59", 1,
     ["emergencia", "clinico_geral", "ortopedia"]),
    (4, "Hosp. Vet. Bicho Feliz", "Rua Verde, 45 · Vila Nova", 2.3, "(19) 99999-0004", "00:00", "23:59", 1,
     ["emergencia", "ortopedia", "odontologia", "clinico_geral"]),
    (5, "OdontoPet Sorriso Animal", "Rua Ipê, 130 · Vila Nova", 1.3, "(19) 99999-0005", "09:00", "19:00", 0,
     ["odontologia"]),
    (6, "NutriPet Consultório", "Av. da Saudade, 900 · Jd. Europa", 2.0, "(19) 99999-0006", "10:00", "20:00", 0,
     ["nutricao", "clinico_geral"]),
    (7, "DermaVet Pele & Pelo", "Rua São João, 80 · Centro", 1.1, "(19) 99999-0007", "08:30", "17:30", 0,
     ["dermatologia"]),
    (8, "Plantão Vet Noturno", "Av. Brasil, 1200 · Jd. Bela Vista", 1.8, "(19) 99999-0008", "19:00", "07:00", 0,
     ["emergencia", "clinico_geral"]),
]

# ------------------------------------------------------------ tutor demo
TUTOR_DEMO = (1, "Ana Ribeiro", "ana.ribeiro@exemplo.com", "(19) 98888-0000", "Rua das Acácias, 300 · Centro")
PET_DEMO = (1, 1, "Thor", "cao", 6.0, "medio")
# Histórico de compras do tutor demo nos últimos 90 dias (oferta_id, dias_atras)
COMPRAS_DEMO = [
    (1, 85), (1, 55), (1, 25),        # ração Golden (alimentação) a cada ~30 dias
    (17, 70), (17, 40), (17, 12),     # bifinho (petisco)
    (20, 60), (20, 30),               # antipulgas (pele)
    (8, 50),                          # bolinha (brinquedo)
    (36, 20),                         # tapete higiênico (higiene)
]


def criar():
    if os.path.exists(CAMINHO_DB):
        os.remove(CAMINHO_DB)
    con = sqlite3.connect(CAMINHO_DB)
    with open(CAMINHO_SCHEMA, encoding="utf-8") as f:
        con.executescript(f.read())

    con.executemany("INSERT INTO lojas VALUES (?,?,?,?,?,?)", LOJAS)

    for pid, nome, cat, grupo, img, desc, caracs, avals in PRODUTOS:
        con.execute("INSERT INTO produtos VALUES (?,?,?,?,?,?)", (pid, nome, cat, grupo, img, desc))
        con.executemany("INSERT INTO caracteristicas VALUES (?,?,?)", [(pid, r, v) for r, v in caracs])
        con.executemany("INSERT INTO avaliacoes VALUES (?,?,?,?)", [(pid, a, n, t) for a, n, t in avals])

    con.executemany("INSERT INTO ofertas (id, produto_id, loja_id, preco, entrega) VALUES (?,?,?,?,?)",
                    [(i + 1, *o) for i, o in enumerate(OFERTAS)])

    for cid, nome, end, dist, tel, abre, fecha, h24, esps in CLINICAS:
        con.execute("INSERT INTO clinicas VALUES (?,?,?,?,?,?,?,?)", (cid, nome, end, dist, tel, abre, fecha, h24))
        con.executemany("INSERT INTO clinica_especialidades VALUES (?,?)", [(cid, e) for e in esps])

    con.execute("INSERT INTO tutores VALUES (?,?,?,?,?)", TUTOR_DEMO)
    con.execute("INSERT INTO pets VALUES (?,?,?,?,?,?)", PET_DEMO)

    hoje = date.today()
    for oferta_id, dias in COMPRAS_DEMO:
        preco = con.execute("SELECT preco FROM ofertas WHERE id=?", (oferta_id,)).fetchone()[0]
        con.execute("INSERT INTO compras (tutor_id, oferta_id, data, quantidade, valor) VALUES (?,?,?,?,?)",
                    (1, oferta_id, (hoje - timedelta(days=dias)).isoformat(), 1, preco))

    con.commit()
    resumo = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ["lojas", "produtos", "ofertas", "clinicas", "tutores", "compras"]}
    con.close()
    print(f"Banco criado em {CAMINHO_DB}")
    for t, n in resumo.items():
        print(f"  {t:10s} {n:4d} registros")


if __name__ == "__main__":
    criar()
