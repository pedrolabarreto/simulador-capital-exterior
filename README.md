# Simulador de Capital no Exterior

Este projeto Streamlit compara três estratégias de investimento para investidores brasileiros:

1. **ETF com dividendos** (retenção 30% nos EUA, crédito 15% no Brasil)
2. **Bond com cupom** (isento nos EUA; 15% IR Brasil anual)
3. **Mutual fund acumulativo** (tributado apenas no resgate, 15% no Brasil)

## Como executar

```bash
git clone https://github.com/<seu_usuario>/simulador-capital-exterior.git
cd simulador-capital-exterior
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador.

## Deploy rápido

- Suba o repositório no GitHub.
- Crie um app na Streamlit Community Cloud apontando para `app.py`.
- O deploy atualiza automaticamente a cada push.
