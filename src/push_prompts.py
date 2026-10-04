"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

PROMPT_FILE = "prompts/bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    full_name = f"{username}/{prompt_name}"

    messages = [("system", prompt_data["system_prompt"])]
    if prompt_data.get("user_prompt"):
        messages.append(("human", prompt_data["user_prompt"]))
    prompt = ChatPromptTemplate.from_messages(messages)

    techniques = prompt_data.get("techniques_applied", [])
    readme = (
        f"# {prompt_name}\n\n"
        f"{prompt_data.get('description', '')}\n\n"
        f"**Versão:** {prompt_data.get('version', '')}\n\n"
        "**Técnicas aplicadas:**\n"
        + "\n".join(f"- {t}" for t in techniques)
    )

    print(f"Fazendo push de: {full_name} (público)")

    try:
        url = hub.push(
            full_name,
            prompt,
            new_repo_is_public=True,
            new_repo_description=prompt_data.get("description", ""),
            readme=readme,
            tags=prompt_data.get("tags", []),
        )
    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt: {e}")
        return False

    print(f"✅ Prompt publicado: {url}")
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    is_valid, errors = validate_prompt_structure(prompt_data)

    if not prompt_data.get("user_prompt"):
        errors.append("user_prompt está vazio (esperado: '{bug_report}')")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS - LANGSMITH")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    data = load_yaml(PROMPT_FILE)
    if not data or PROMPT_KEY not in data:
        print(f"❌ Chave '{PROMPT_KEY}' não encontrada em {PROMPT_FILE}")
        return 1

    prompt_data = data[PROMPT_KEY]

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✓ Prompt validado")
    return 0 if push_prompt_to_langsmith(PROMPT_KEY, prompt_data) else 1


if __name__ == "__main__":
    sys.exit(main())
