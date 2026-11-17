import argparse
import json
import os
import joblib
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

import user_data_manager

DEFAULT_DB_PATH = "data/embeddings.json"
DEFAULT_MODEL_PATH = "model/gesture_rf.joblib"
DEFAULT_LABELS_PATH = "model/labels.json"


def load_samples(db_path_or_dict):
    if isinstance(db_path_or_dict, dict):
        db = db_path_or_dict
    else:
        if not os.path.exists(db_path_or_dict):
            raise FileNotFoundError(
                f"No collected samples found at {db_path_or_dict}. Save samples first."
            )
        with open(db_path_or_dict, "r", encoding="utf-8") as f:
            db = json.load(f)

    X, y = [], []
    labels = sorted(db.keys())
    label_to_idx = {lbl: i for i, lbl in enumerate(labels)}

    for label, samples in db.items():
        for sample in samples:
            X.append(sample)
            y.append(label_to_idx[label])

    if len(X) < 10 or len(labels) < 2:
        raise ValueError(
            f"Need at least 10 samples and 2 labels to train a useful model. (Found {len(X)} samples across {len(labels)} labels)"
        )

    return np.array(X, dtype=np.float32), np.array(y), labels


def augment_embeddings(X, y, copies=3, noise_std=0.015, scale_jitter=0.03):
    aug_X = [X]
    aug_y = [y]

    for _ in range(copies):
        noise = np.random.normal(0.0, noise_std, size=X.shape).astype(np.float32)
        scale = np.random.uniform(1.0 - scale_jitter, 1.0 + scale_jitter, size=(X.shape[0], 1)).astype(np.float32)
        aug_sample = (X * scale) + noise
        aug_sample = np.clip(aug_sample, -2.0, 2.0)
        aug_X.append(aug_sample.astype(np.float32))
        aug_y.append(y)

    return np.vstack(aug_X), np.concatenate(aug_y)


def build_ensemble():
    rf = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced_subsample",
        min_samples_leaf=2,
        max_features="sqrt",
        n_jobs=-1,
    )
    et = ExtraTreesClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        min_samples_leaf=1,
        max_features="sqrt",
        n_jobs=-1,
    )

    return VotingClassifier(
        estimators=[("rf", rf), ("et", et)],
        voting="soft",
        weights=[1.0, 1.2],
        n_jobs=-1,
    )


def train_model_for_user(username=None, db=None):
    """
    Train model for a specific user, or fallback to global paths if username is None.
    Returns (success: bool, message: str, report_str: str).
    """
    np.random.seed(42)

    if username:
        user_root = user_data_manager.get_user_root(username)
        model_dir = os.path.join(user_root, "model")
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "gesture_rf.joblib")
        labels_path = os.path.join(model_dir, "labels.json")
        source = db if db is not None else user_data_manager.load_user_db(username)
    else:
        model_dir = "model"
        os.makedirs(model_dir, exist_ok=True)
        model_path = DEFAULT_MODEL_PATH
        labels_path = DEFAULT_LABELS_PATH
        source = db if db is not None else DEFAULT_DB_PATH

    try:
        X, y, labels = load_samples(source)
    except Exception as e:
        return False, str(e), ""

    # Check minimum class distribution
    class_counts = np.bincount(y, minlength=len(labels))
    min_count = int(np.min(class_counts))
    stratify_target = y if min_count >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=stratify_target
    )

    X_train_aug, y_train_aug = augment_embeddings(X_train, y_train, copies=4)
    clf = build_ensemble()
    clf.fit(X_train_aug, y_train_aug)

    y_pred = clf.predict(X_test)
    report = classification_report(
        y_test,
        y_pred,
        labels=np.arange(len(labels)),
        target_names=labels,
        zero_division=0,
    )

    joblib.dump(clf, model_path)
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)

    success_msg = f"Model successfully trained and saved for {'user ' + username if username else 'global storage'} at {model_path}"
    return True, success_msg, report


def main():
    parser = argparse.ArgumentParser(description="Train Sign Language Gesture Classifier")
    parser.add_argument("--user", type=str, default=None, help="Username to train model for (optional)")
    args = parser.parse_args()

    success, msg, report = train_model_for_user(args.user)
    print(msg)
    if report:
        print("\nClassification Report:\n", report)


if __name__ == "__main__":
    main()
