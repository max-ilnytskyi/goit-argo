import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from sklearn.datasets import load_iris
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import train_test_split


MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")
PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")
EXPERIMENT_NAME = "iris-gradient-boosting"
BEST_MODEL_DIR = Path(__file__).resolve().parent.parent / "best_model"


def push_metrics(run_id: str, accuracy: float, loss: float) -> None:
    registry = CollectorRegistry()

    accuracy_metric = Gauge(
        "mlflow_accuracy",
        "Model accuracy for an MLflow run",
        registry=registry,
    )
    loss_metric = Gauge(
        "mlflow_loss",
        "Model log loss for an MLflow run",
        registry=registry,
    )

    accuracy_metric.set(accuracy)
    loss_metric.set(loss)

    push_to_gateway(
        PUSHGATEWAY_URL,
        job="mlflow_experiment",
        grouping_key={"run_id": run_id},
        registry=registry,
    )


def main() -> None:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    data = load_iris()
    x_train, x_test, y_train, y_test = train_test_split(
        data.data,
        data.target,
        test_size=0.2,
        random_state=42,
        stratify=data.target,
    )

    parameter_grid = [
        {"learning_rate": 0.05, "epochs": 50},
        {"learning_rate": 0.05, "epochs": 100},
        {"learning_rate": 0.1, "epochs": 50},
        {"learning_rate": 0.1, "epochs": 100},
    ]

    best_accuracy = -1.0
    best_loss = None
    best_run_id = None
    best_model = None

    for params in parameter_grid:
        model = GradientBoostingClassifier(
            learning_rate=params["learning_rate"],
            n_estimators=params["epochs"],
            random_state=42,
        )

        with mlflow.start_run() as run:
            model.fit(x_train, y_train)

            predictions = model.predict(x_test)
            probabilities = model.predict_proba(x_test)

            accuracy = accuracy_score(y_test, predictions)
            loss = log_loss(y_test, probabilities)

            mlflow.log_params(params)
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("loss", loss)
            mlflow.sklearn.log_model(model, name="model")

            push_metrics(run.info.run_id, accuracy, loss)

            print(
                f"run_id={run.info.run_id} "
                f"learning_rate={params['learning_rate']} "
                f"epochs={params['epochs']} "
                f"accuracy={accuracy:.4f} "
                f"loss={loss:.4f}"
            )

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_loss = loss
                best_run_id = run.info.run_id
                best_model = model

    BEST_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = BEST_MODEL_DIR / "model.joblib"
    joblib.dump(best_model, model_path)

    print()
    print(f"Best run_id={best_run_id}")
    print(f"Best accuracy={best_accuracy:.4f}")
    print(f"Best loss={best_loss:.4f}")
    print(f"Best model saved to {model_path}")


if __name__ == "__main__":
    main()