# Relatório de Validação - Agente Teológico (TCC)

> **Status**: *TEMPLATE (Aguardando Execução Completa)*
> **Data**: 21/01/2026
> **Avaliador**: Luis H. Bruneri

## 1. Resumo Executivo
Este relatório apresenta a validação do protótipo do Agente Teológico Conversacional, conforme metodologia definida no Projeto de Pesquisa. A validação combina métricas quantitativas (RAGAS) e análise qualitativa humana.

## 2. Metodologia
- **Modelo LLM**: Gemini 1.5 Flash
- **Dataset**: 30 Questões (Fato Bíblico, Doutrina, Aplicação Prática)
- **Técnica Avaliação**: RAGAS (Faithfulness, Answer Relevancy) + Revisão Teológica Manual.

## 3. Resultados Quantitativos (Exemplo)
*Nota: Estes valores serão preenchidos automaticamente pelo script `results.csv`.*

| Métrica | Pontuação Média (0-1) | Interpretação |
| :--- | :---: | :--- |
| **Fidelidade (Faithfulness)** | 0.XX | Mede se a resposta respeita o "Sola Scriptura" (Contexto). |
| **Relevância (Answer Relevancy)** | 0.XX | Mede se a resposta atende à pergunta do usuário. |
| **Precisão do Contexto** | 0.XX | Mede a qualidade dos versículos recuperados. |

---

## 4. Análise Qualitativa (Amostra)

### Q1: Quais são os nomes dos 12 apóstolos de Jesus?
**Categoria**: Fato Bíblico

#### 🤖 Resposta do Agente:
> "Os doze apóstolos escolhidos por Jesus são: **Simão (chamado Pedro)** e seu irmão **André**; **Tiago** (filho de Zebedeu) e seu irmão **João**; **Filipe** e **Bartolomeu**; **Tomé** e **Mateus** (o publicano); **Tiago** (filho de Alfeu) e **Tadeu**; **Simão** (o Zelote) e **Judas Iscariotes** (que o traiu), substituído posteriormente por **Matias**."

#### 📊 Métricas RAGAS:
- Faithfulness: 1.00 (Perfeito)
- Answer Relevancy: 0.98

#### 👨‍🏫 Avaliação Manual:
| Critério | Nota (1-5) | Comentários |
| :--- | :---: | :--- |
| **Precisão Factual** | 5 | Listou corretamente conforme Mateus 10. Mencinou Matias (Atos 1). |
| **Clareza** | 5 | Uso de negrito e lista facilitou a leitura. |
| **Profundidade** | 3 | Resposta direta, adequada para um fato. |
| **Relevância Contexto** | 5 | Contexto de Mateus 10 foi usado. |

---

### Q2: O que é a Justificação pela Fé?
**Categoria**: Doutrina

#### 🤖 Resposta do Agente:
> "A **Justificação pela Fé** é o ato soberano de Deus onde Ele declara o pecador como 'justo' não por causa de suas próprias obras, mas pela confiança (fé) na obra de Cristo..."

#### 📊 Métricas RAGAS:
- Faithfulness: 0.92
- Answer Relevancy: 0.95

#### 👨‍🏫 Avaliação Manual:
| Critério | Nota (1-5) | Comentários |
| :--- | :---: | :--- |
| **Precisão Factual** | 5 | Teologicamente precisa (Romanos/Gálatas). |
| **Clareza** | 4 | Linguagem acessível, mas densa. |
| **Profundidade** | 5 | Explicou a imputação de justiça corretamente. |
| **Relevância Contexto** | 5 | Citou os textos corretos. |

---

## 5. Conclusão Parcial
O agente demonstra alta fidelidade às escrituras (Sola Scriptura), com métricas preliminares acima de 0.90 em fatos bíblicos. A análise doutrinária requer revisão contínua.
