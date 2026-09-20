import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "prompt_builder.py"

spec = importlib.util.spec_from_file_location("prompt_builder", MODULE_PATH)
prompt_builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_builder)


def test_load_template_uses_project_root_not_cwd(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    template = prompt_builder.load_template("standard")

    assert "Text span" in template
    assert "{label_list}" in template


def test_build_prompt_formats_labels(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    prompt = prompt_builder.build_prompt(
        "standard",
        "These corrupt politicians have betrayed us all!",
        ["Loaded Language", "Doubt"],
    )

    assert "Loaded Language" in prompt
    assert "Doubt" in prompt
    assert "These corrupt politicians have betrayed us all!" in prompt
