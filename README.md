# Simulador de Projeção de Capital no Exterior

Este app Streamlit compara três estratégias de investimento para o investidor brasileiro:

1. **ETF que paga dividendos** (retenção de 30% nos EUA, crédito 15% no Brasil)
2. **Bond que paga cupom** (isento nos EUA; 15% IR Brasil anual)
3. **Mutual fund acumulativo** (tributado apenas no resgate, 15% no Brasil)

## Executando localmente

```bash
# clone o repositório
git clone https://github.com/<seu_usuario>/<seu_repo>.git
cd <seu_repo>

# crie ambiente virtual (opcional)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate   # Windows

# instale dependências
pip install -r requirements.txt

# rode
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador.
