VENV   ?= venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

.DEFAULT_GOAL := help
.PHONY: help venv install env pull push evaluate test pipeline clean

help: ## Lista os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-10s %s\n", $$1, $$2}'

$(PYTHON):
	python3 -m venv $(VENV)

venv: $(PYTHON) ## Cria o ambiente virtual (venv/)

install: venv ## Cria o venv (se preciso) e instala as dependências
	$(PIP) install -r requirements.txt

env: ## Cria o .env a partir do .env.example (não sobrescreve se já existir)
	@if [ -f .env ]; then echo ".env já existe, nada a fazer"; else cp .env.example .env && echo ".env criado, preencha as chaves"; fi

pull: ## 1. Pull do prompt v1 do LangSmith -> prompts/bug_to_user_story_v1.yml
	$(PYTHON) src/pull_prompts.py

push: ## 3. Push do prompt v2 (PÚBLICO) -> {username}/bug_to_user_story_v2
	$(PYTHON) src/push_prompts.py

evaluate: ## 4. Avalia o v2 publicado no Hub (~60 chamadas ao LLM, gera custo)
	$(PYTHON) src/evaluate.py

test: ## 5. Testes de validação do prompt (sem chamar LLM)
	$(PYTHON) -m pytest tests/test_prompts.py -v

pipeline: test push evaluate ## Testa, publica o v2 e avalia (publica e gera custo)

clean: ## Remove caches (__pycache__, .pytest_cache)
	find . -path ./$(VENV) -prune -o -type d -name __pycache__ -print -exec rm -rf {} +
	rm -rf .pytest_cache
