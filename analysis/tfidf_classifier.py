import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score
import joblib
import os
from typing import Dict, Tuple, List

class TFIDFClassifier:
    """TF-IDF based GDPR classifier with training capability"""

    def __init__(self, model_path: str = 'data/trained_models/'):
        self.model_path = model_path
        self.vectorizer = None
        self.classifiers = {}  # One classifier per GDPR control
        self.controls = [
            'data_minimization', 'purpose_limitation', 'storage_limitation',
            'accuracy', 'integrity_confidentiality', 'lawfulness',
            'transparency', 'consent', 'data_subject_rights', 'dpo_contact'
        ]
        self.is_trained = False
        self.training_stats = {}

    def load_dataset(self, dataset_path: str = 'data/labeled_dataset.json') -> Tuple[List[str], Dict[str, List[int]]]:
        """Load and prepare training dataset"""
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        texts = []
        labels = {control: [] for control in self.controls}

        for domain_data in data['domains']:
            texts.append(domain_data['policy_text'])
            for control in self.controls:
                labels[control].append(int(domain_data['gdpr_controls'][control]))

        return texts, labels

    def train(self, dataset_path: str = 'data/labeled_dataset.json', test_size: float = 0.2) -> Dict:
        """Train TF-IDF classifiers for all GDPR controls"""
        print("=" * 80)
        print("[*] STARTING TF-IDF CLASSIFIER TRAINING")
        print("=" * 80)

        # Load dataset
        print("\n[*] Loading dataset...")
        texts, labels = self.load_dataset(dataset_path)
        total_samples = len(texts)
        print(f"[OK] Loaded {total_samples} privacy policy samples")

        # Split data
        print(f"\n[*] Splitting data: {int((1-test_size)*100)}% train, {int(test_size*100)}% test...")
        train_texts, test_texts = train_test_split(texts, test_size=test_size, random_state=42)

        # Train TF-IDF Vectorizer
        print("\n[*] Training TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            stop_words='english',
            min_df=1
        )
        X_train = self.vectorizer.fit_transform(train_texts)
        X_test = self.vectorizer.transform(test_texts)
        print(f"[OK] Vectorizer trained: {X_train.shape[1]} features extracted")

        # Train individual classifiers for each control
        print("\n[*] Training binary classifiers for each GDPR control...")
        print("-" * 80)

        results = {
            'train_size': len(train_texts),
            'test_size': len(test_texts),
            'controls': {}
        }

        for i, control in enumerate(self.controls, 1):
            print(f"\n[{i}/{len(self.controls)}] Training: {control.replace('_', ' ').title()}")

            # Split labels
            train_labels_split, test_labels_split = train_test_split(
                labels[control], test_size=test_size, random_state=42
            )
            y_train = np.array(train_labels_split)
            y_test = np.array(test_labels_split)

            # Train classifier
            clf = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
            clf.fit(X_train, y_train)

            # Evaluate
            train_pred = clf.predict(X_train)
            test_pred = clf.predict(X_test)

            train_f1 = f1_score(y_train, train_pred, average='binary', zero_division=0)
            test_f1 = f1_score(y_test, test_pred, average='binary', zero_division=0)
            test_precision = precision_score(y_test, test_pred, average='binary', zero_division=0)
            test_recall = recall_score(y_test, test_pred, average='binary', zero_division=0)

            # Cross-validation
            cv_scores = cross_val_score(clf, X_train, y_train, cv=3, scoring='f1')
            cv_mean = np.mean(cv_scores)

            self.classifiers[control] = clf

            print(f"   Train F1: {train_f1:.3f}")
            print(f"   Test F1:  {test_f1:.3f}")
            print(f"   Precision: {test_precision:.3f}")
            print(f"   Recall:    {test_recall:.3f}")
            print(f"   CV F1 (3-fold): {cv_mean:.3f} [*] {np.std(cv_scores):.3f}")

            results['controls'][control] = {
                'train_f1': float(train_f1),
                'test_f1': float(test_f1),
                'test_precision': float(test_precision),
                'test_recall': float(test_recall),
                'cv_mean': float(cv_mean),
                'cv_std': float(np.std(cv_scores))
            }

        # Calculate overall metrics
        all_test_f1 = [results['controls'][c]['test_f1'] for c in self.controls]
        overall_f1 = np.mean(all_test_f1)

        print("\n" + "=" * 80)
        print("[*] TRAINING COMPLETE - OVERALL RESULTS")
        print("=" * 80)
        print(f"Overall Test F1 Score (macro avg): {overall_f1:.3f}")
        print(f"Best performing control: {max(results['controls'].items(), key=lambda x: x[1]['test_f1'])[0]}")
        print(f"Lowest performing control: {min(results['controls'].items(), key=lambda x: x[1]['test_f1'])[0]}")
        print("=" * 80)

        self.is_trained = True
        self.training_stats = results

        # Save models
        self.save_models()

        return results

    def save_models(self):
        """Save trained models to disk"""
        os.makedirs(self.model_path, exist_ok=True)

        print(f"\n[*] Saving models to {self.model_path}...")

        # Save vectorizer
        vectorizer_path = os.path.join(self.model_path, 'tfidf_vectorizer.pkl')
        joblib.dump(self.vectorizer, vectorizer_path)
        print(f"  [OK] Saved vectorizer: {vectorizer_path}")

        # Save classifiers
        for control, clf in self.classifiers.items():
            clf_path = os.path.join(self.model_path, f'classifier_{control}.pkl')
            joblib.dump(clf, clf_path)
        print(f"  [OK] Saved {len(self.classifiers)} classifiers")

        # Save training stats
        stats_path = os.path.join(self.model_path, 'training_stats.json')
        with open(stats_path, 'w') as f:
            json.dump(self.training_stats, f, indent=2)
        print(f"  [OK] Saved training statistics")

        print("[OK] All models saved successfully!")

    def load_models(self) -> bool:
        """Load trained models from disk"""
        try:
            # Load vectorizer
            vectorizer_path = os.path.join(self.model_path, 'tfidf_vectorizer.pkl')
            self.vectorizer = joblib.load(vectorizer_path)

            # Load classifiers
            for control in self.controls:
                clf_path = os.path.join(self.model_path, f'classifier_{control}.pkl')
                self.classifiers[control] = joblib.load(clf_path)

            # Load stats
            stats_path = os.path.join(self.model_path, 'training_stats.json')
            if os.path.exists(stats_path):
                with open(stats_path, 'r') as f:
                    self.training_stats = json.load(f)

            self.is_trained = True
            return True
        except Exception as e:
            print(f"Error loading models: {e}")
            return False

    def classify(self, policy_text: str) -> Dict[str, float]:
        """Classify policy text for GDPR controls"""
        if not self.is_trained:
            # Try to load models
            if not self.load_models():
                raise Exception("Model not trained. Call train() first or load existing models.")

        # Vectorize input
        X = self.vectorizer.transform([policy_text])

        # Predict for each control
        scores = {}
        for control, clf in self.classifiers.items():
            # Get probability of compliance
            proba = clf.predict_proba(X)[0]
            # Probability of class 1 (compliant)
            scores[control] = float(proba[1]) if len(proba) > 1 else 0.0

        return scores

    def evaluate_on_unseen(self, test_domains: List[Dict]) -> Dict:
        """Evaluate model on unseen domains"""
        print("\n[*] TESTING ON UNSEEN DATA")
        print("=" * 80)

        results = []

        for domain_data in test_domains:
            domain = domain_data['domain']
            print(f"\n[*] Testing: {domain}")

            predictions = self.classify(domain_data['policy_text'])
            actual = domain_data['gdpr_controls']

            # Calculate accuracy for this domain
            correct = sum(1 for c in self.controls if (predictions[c] >= 0.5) == actual[c])
            accuracy = correct / len(self.controls)

            print(f"   Accuracy: {accuracy:.1%} ({correct}/{len(self.controls)} controls correct)")

            results.append({
                'domain': domain,
                'accuracy': accuracy,
                'predictions': predictions,
                'actual': actual
            })

        overall_accuracy = np.mean([r['accuracy'] for r in results])
        print(f"\n[*] Overall accuracy on unseen data: {overall_accuracy:.1%}")
        print("=" * 80)

        return {
            'overall_accuracy': overall_accuracy,
            'results': results
        }
