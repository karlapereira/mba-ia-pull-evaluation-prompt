"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_HUB_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith() -> bool:
    """
    Faz pull do prompt inicial do Hub e salva em YAML.

    Returns:
        True se sucesso, False caso contrário
    """
    print(f"Fazendo pull de: {PROMPT_HUB_NAME}")

    try:
        prompt = hub.pull(PROMPT_HUB_NAME)
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return False

    system_prompt = ""
    user_prompt = ""
    for message in prompt.messages:
        template = message.prompt.template
        if message.__class__.__name__ == "SystemMessagePromptTemplate":
            system_prompt = template
        elif message.__class__.__name__ == "HumanMessagePromptTemplate":
            user_prompt = template

    prompt_name = PROMPT_HUB_NAME.split("/")[-1]
    data = {
        prompt_name: {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if not save_yaml(data, str(OUTPUT_PATH)):
        return False

    print(f"✅ Prompt salvo em: {OUTPUT_PATH}")
    return True


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS - LANGSMITH")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    return 0 if pull_prompts_from_langsmith() else 1


if __name__ == "__main__":
    sys.exit(main())
