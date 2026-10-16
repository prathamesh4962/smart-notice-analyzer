from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.preprocessing import normalize_text, tokenize_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "notices.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "notice_classifier.joblib"


def load_labeled_data(csv_path: Path = DATA_PATH) -> tuple[pd.Series, pd.Series]:
    """Load and validate notice text and category columns from a CSV file."""
    data = pd.read_csv(csv_path)
    required_columns = {"text", "category"}
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dataset is missing required columns: {missing}")

    data = data.dropna(subset=["text", "category"]).copy()
    data["text"] = data["text"].astype(str).str.strip()
    data["category"] = data["category"].astype(str).str.strip()
    data = data[(data["text"] != "") & (data["category"] != "")]

    category_counts = data["category"].value_counts()
    if len(category_counts) < 2:
        raise ValueError("The dataset must contain at least two categories.")
    if (category_counts < 2).any():
        insufficient = ", ".join(category_counts[category_counts < 2].index)
        raise ValueError(
            "Each category needs at least two notices for a stratified split. "
            f"Add more examples for: {insufficient}"
        )

    return data["text"], data["category"]


def train_and_evaluate(
    csv_path: Path = DATA_PATH,
    model_path: Path = MODEL_PATH,
) -> tuple[Pipeline, float, str, pd.DataFrame, int, int]:
    """Train a TF-IDF classifier, evaluate a holdout set, and save the pipeline."""
    notices, categories = load_labeled_data(csv_path)
    notices_train, notices_test, categories_train, categories_test = train_test_split(
        notices,
        categories,
        test_size=0.25,
        random_state=42,
        stratify=categories,
    )

    pipeline = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    preprocessor=normalize_text,
                    tokenizer=tokenize_text,
                    token_pattern=None,
                    lowercase=False,
                    ngram_range=(1, 2),
                ),
            ),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )
    pipeline.fit(notices_train, categories_train)
    predictions = pipeline.predict(notices_test)

    labels = sorted(categories.unique())
    report = classification_report(
        categories_test,
        predictions,
        labels=labels,
        zero_division=0,
    )
    matrix = pd.DataFrame(
        confusion_matrix(categories_test, predictions, labels=labels),
        index=labels,
        columns=labels,
    )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)

    return (
        pipeline,
        float(accuracy_score(categories_test, predictions)),
        report,
        matrix,
        len(notices_train),
        len(notices_test),
    )


def main() -> None:
    _, accuracy, report, matrix, train_size, test_size = train_and_evaluate()
    print(f"Training notices: {train_size}")
    print(f"Holdout notices: {test_size}")
    print(f"Holdout accuracy (synthetic sample): {accuracy:.3f}")
    print("\nClassification report:")
    print(report)
    print("Confusion matrix (rows: actual, columns: predicted):")
    print(matrix)
    print(f"\nSaved pipeline to: {MODEL_PATH}")
    print("Scores are illustrative only; the dataset is small and synthetic.")


if __name__ == "__main__":
    main()