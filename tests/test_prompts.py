import re
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt():
    return load_prompts(str(PROMPT_FILE))[PROMPT_KEY]


@pytest.fixture(scope="module")
def system_prompt(prompt):
    return prompt.get("system_prompt", "")


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt):
        assert "system_prompt" in prompt, "Campo 'system_prompt' não encontrado"
        assert isinstance(prompt["system_prompt"], str)
        assert prompt["system_prompt"].strip(), "'system_prompt' está vazio"

    def test_prompt_has_role_definition(self, system_prompt):
        assert re.search(r"Você é (um|uma)\b", system_prompt), \
            "O prompt deve definir uma persona (ex: 'Você é um Product Manager')"

    def test_prompt_mentions_format(self, system_prompt):
        text = system_prompt.lower()
        for expected in ("como um", "eu quero", "para que", "critérios de aceitação"):
            assert expected in text, f"O formato de User Story deve mencionar '{expected}'"

    def test_prompt_has_few_shot_examples(self, system_prompt):
        inputs = re.findall(r"Relato de Bug:", system_prompt)
        outputs = re.findall(r"Resposta:", system_prompt)
        assert len(inputs) >= 2 and len(outputs) >= 2, \
            "Few-shot exige pelo menos 2 exemplos de entrada ('Relato de Bug:') e saída ('Resposta:')"

    def test_prompt_no_todos(self, prompt):
        for field in ("system_prompt", "user_prompt", "description"):
            text = prompt.get(field, "") or ""
            assert "[TODO]" not in text, f"'[TODO]' encontrado em '{field}'"
            assert "TODO" not in text, f"'TODO' encontrado em '{field}'"

    def test_minimum_techniques(self, prompt):
        techniques = prompt.get("techniques_applied", [])
        assert len(techniques) >= 2, \
            f"Mínimo de 2 técnicas em 'techniques_applied', encontradas: {len(techniques)}"

    def test_structure_is_valid(self, prompt):
        is_valid, errors = validate_prompt_structure(prompt)
        assert is_valid, f"Estrutura inválida: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
