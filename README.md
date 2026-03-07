# 🛒 Copiloto de Dados IA: E-commerce & Varejo

**Um Assistente de Inteligência Artificial (Agentic Text-to-SQL) desenhado para analisar e extrair insights de uma base de dados real com mais de 283 mil avaliações de produtos da Amazon.**

Este projeto não é apenas um "chatbot". É uma aplicação modular, pronta para produção, que demonstra as melhores práticas de **Engenharia de IA, Segurança de Software e Observabilidade**.

## 🎯 Destaques Técnicos:

Este sistema foi construído para resolver problemas reais de adoção de LLMs no mundo corporativo:

* 🛡️ **Human-in-the-Loop (Segurança em 1º Lugar)**: A IA atua como uma analista de dados. Ela escreve a query SQL, mas nunca a executa diretamente. A interface exige aprovação humana antes de rodar qualquer código na base de dados, prevenindo ataques e _drop tables_.

* 🔧 **Self-Healing Code (Auto-Correção)**: Se uma query SQL falhar (ex: erro de sintaxe ou coluna inexistente), o sistema captura o erro do banco de dados em background e envia-o de volta à IA. O Agente corrige a query e tenta novamente de forma autônoma (até 3 tentativas).

* 💰 **Auditoria FinOps**: Um dashboard nativo calcula o uso exato de tokens (Input/Output) de cada interação, demonstrando a viabilidade financeira e a poupança gerada ao optar pelo modelo open-source (Llama 3.3 via Groq) em vez de APIs proprietárias (como GPT-4o).

* 🧠 **Memória Conversacional Context-Aware**: A pipeline injeta o histórico truncado da conversa no LLM. O utilizador pode fazer perguntas sequenciais com pronomes (ex: "E quais as piores notas dessa categoria?") e o SQL adapta-se dinamicamente.

* 📊 **Integração de BI**: Geração dinâmica de gráficos Pandas/Streamlit e exportação instantânea de relatórios (CSV) para cruzamento de dados offline.

## 🏗️ Arquitetura do Sistema

O projeto adota uma arquitetura modular para facilitar a manutenção e escalabilidade:
```
📁 raiz/
├── 📄 agente_sql_amazon.py   # Interface Principal (Streamlit) e Roteamento
├── 📄 requirements.txt       # Dependências e Gestão de Pacotes
├── 📄 .env                   # Variáveis de Ambiente e Chaves (Não versionado)
└── 📂 src/
    ├── 📄 database.py        # Pipeline de ingestão (HuggingFace -> SQLite)
    └── 📄 agent.py           # Core do LLM e Lógica LangChain/LangGraph
```

### O Dataset (Amazon Reviews)

O módulo ```database.py``` conecta-se diretamente ao repositório do HuggingFace (```minhth2nh/amazon_product_review_283K```) e converte os mais de 280.000 registos para um ficheiro SQLite local (```amazon_reviews.db```). Isto garante um ambiente de testes robusto e veloz sem sobrecarregar a memória RAM.

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos

* Python 3.10 ou superior.

* Uma chave de API gratuita da Groq.

### Passo a Passo

1. **Clone o repositório**:
```
git clone [https://github.com/SEU_USUARIO/copiloto-varejo-ia.git](https://github.com/SEU_USUARIO/copiloto-varejo-ia.git)
cd copiloto-varejo-ia
```

2. **Crie e ative um ambiente virtual**:
```
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

3. **Instale as dependências**:
```
pip install -r requirements.txt
```

4. **Configure a Variável de Ambiente**:
Crie um ficheiro ```.env``` na raiz do projeto e adicione a sua chave:
```
GROQ_API_KEY=sua_chave_groq_aqui
```

5. **Inicie a Aplicação**:
```
streamlit run agente_sql_amazon.py
```

_(Nota: Na primeira execução, o sistema fará o download da base de dados completa da Amazon, o que pode demorar alguns instantes.)_

## 💡 Exemplos de Uso

Experimente fazer as seguintes perguntas na aba de Chat:

* "Qual é a média geral das notas?"

* "Liste as categorias disponíveis e a quantidade de produtos em cada uma."

* "Mostre 5 avaliações (título e texto) que deram nota 1. Qual o principal motivo da reclamação?"

Desenvolvido com muito café, paciência, foco em arquitetura de dados e IA.