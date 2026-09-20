import os
from pathlib import Path
from utils import get_project_root, load_config


def load_template(strategy: str, prompts_dir: str = "prompts") -> str:
    """Reads one template file (e.g. 'standard') and returns its raw text."""
    project_root = get_project_root()
    prompts_path = Path(prompts_dir)

    if not prompts_path.is_absolute():
        prompts_path = project_root / prompts_dir

    path = prompts_path / f"{strategy}.txt"

    if not path.exists():
        raise FileNotFoundError(f"No template found for strategy '{strategy}' at {path}")

    with path.open("r", encoding="utf-8") as f:
        template = f.read()

    return template


def build_prompt(strategy: str, span_text: str, labels: list, prompts_dir: str = "prompts") -> str:
    """Fills a template with the fixed label list and one span's text."""
    template = load_template(strategy, prompts_dir)
    label_list = "\n".join(f"- {label}" for label in labels)
    return template.format(label_list=label_list, span_text=span_text)


if __name__ == "__main__":

    config = load_config()

    demo_labels = config["labels"]

    # Temporary smoke-test selection.
    # Keep all four strategies in config.yaml.
    strategies_to_test = ["structured_output"]

    demo_span = "These corrupt politicians have betrayed us all!"

    for strat in strategies_to_test:
        print(f"\n=== {strat} ===")
        print(build_prompt(strat, demo_span, demo_labels))