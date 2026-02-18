# MarketRadar - Agente Autônomo de Navegação Web

MarketRadar é um agente autônomo especializado em Open Source Intelligence (OSINT) e pesquisa de mercado. Ele navega pela web de forma autônoma para cumprir objetivos específicos, superando obstáculos de UI, pop-ups e paginação.

## Características

- Navegação autônoma na web usando Playwright
- Detecção e prevenção de loops
- Extração automática de dados (preços, produtos, etc.)
- Sistema de memória para rastreamento de ações
- Respostas em formato JSON estruturado
- Navegação human-like (usa barras de busca e menus)

## Instalação Rápida

1. Clone o repositório:
```bash
git clone <repository-url>
cd market-radar-agent
```

2. Instale as dependências do backend:
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
cd ..
```

3. Instale as dependências do frontend:
```bash
cd frontend
npm install
cd ..
```

> 📖 **Para instruções detalhadas de execução, consulte [INSTRUCOES_EXECUCAO.md](./INSTRUCOES_EXECUCAO.md)**

## Uso

### Modo CLI (Linha de Comando)

Execute o agente com um objetivo específico:

```bash
cd backend
python main.py "Encontre o preço médio de Creatina no Brasil"
```

Ou em inglês:

```bash
cd backend
python main.py "Find the average price of Creatine in Brazil"
```

### Modo Web (Frontend)

#### Instalação Inicial

1. **Instale as dependências do backend:**
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
cd ..
```

2. **Instale as dependências do frontend:**
```bash
cd frontend
npm install
cd ..
```

#### Execução

**Terminal 1 - Inicie a API backend:**
```bash
cd backend
python api.py
```

Ou usando uvicorn:
```bash
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Inicie o frontend:**
```bash
cd frontend
npm start
```

3. **Acesse `http://localhost:3000` no navegador**

#### Funcionalidades da Interface Web

- **💬 Chat Interativo**: Digite comandos diretamente no chat para o agente
- **📚 Lista de Fontes**: Visualize automaticamente todas as URLs consultadas
- **📊 Gráficos de Preços**: Veja o histórico de preços em tempo real
- **📄 Exportação PDF**: Gere relatórios completos em PDF
- **📡 Logs em Tempo Real**: Acompanhe o progresso via WebSocket
- **⚙️ Configurações**: Ajuste opções como modo headless e máximo de iterações

#### Exemplo de Uso

1. Abra `http://localhost:3000`
2. No chat, digite: "Encontre o preço médio de Creatina no Brasil"
3. Pressione Enter ou clique em "Enviar"
4. Acompanhe o agente navegando e coletando dados
5. Veja os gráficos sendo atualizados em tempo real
6. Exporte o relatório completo em PDF quando terminar

## Estrutura do Projeto

### Backend
- `backend/`: Código Python do backend
  - `main.py`: Arquivo principal de execução CLI
  - `api.py`: API FastAPI com WebSocket para frontend
  - `agent.py`: Lógica do agente MarketRadar com tomada de decisão
  - `browser_engine.py`: Engine de navegação web usando Playwright
  - `memory.py`: Sistema de memória e histórico de ações
  - `extractor.py`: Sistema de extração de dados da web
  - `requirements.txt`: Dependências Python

### Frontend
- `frontend/`: Aplicação React com TypeScript
  - `src/App.tsx`: Componente principal
  - `src/components/MissionControl.tsx`: Controle de missões
  - `src/components/MissionLog.tsx`: Log em tempo real
  - `src/components/DataViewer.tsx`: Visualizador de dados extraídos
  - `tsconfig.json`: Configuração TypeScript

## Formato de Resposta

O agente retorna comandos em formato JSON:

```json
{
  "thought_process": "Análise do estado atual",
  "reasoning": "Explicação da ação escolhida",
  "action": {
    "name": "type|click|goto|scroll|wait|extract|finish",
    "params": {
      "selector": "...",
      "text": "..."
    }
  },
  "is_goal_achieved": false
}
```

## Ações Disponíveis

- `goto(url)`: Navegar para uma URL
- `click(selector)`: Clicar em um elemento
- `type(selector, text)`: Digitar em um campo
- `scroll(direction)`: Rolar a página (down/up)
- `wait(seconds)`: Aguardar um tempo
- `extract(data_points)`: Extrair dados da página
- `finish(summary)`: Finalizar a missão

## Variáveis de Ambiente

Crie um arquivo `.env` (opcional):

```
BROWSER_HEADLESS=true
MAX_ITERATIONS=50
```

## Requisitos

- Python 3.8+
- Playwright
- Navegador Chromium (instalado via Playwright)
