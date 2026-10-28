# Hermes Kanban Dashboard

Painel web para visualizar tarefas do Kanban do Hermes em tempo real via polling.

## Executar local
```bash
pip install -r requirements.txt
python app.py
```
Acesse http://localhost:5000

## Deploy Dokploy
Conecte o repositório Git ao Dokploy. O Dockerfile já está pronto.
Variável de ambiente opcional:
`KANBAN_BOARD=default`

## API
- GET /api/stats
- GET /api/tasks
