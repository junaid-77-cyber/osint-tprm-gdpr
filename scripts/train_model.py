"""
Training script for TF-IDF GDPR Classifier
Run this script to train the model on labeled dataset
"""

import sys
import os
sys.path.append('.')
os.environ['PYTHONIOENCODING'] = 'utf-8'

from analysis.tfidf_classifier import TFIDFClassifier
import json
import numpy as np

def main():
    print("""
===============================================================================
          OSINT TPRM - TF-IDF CLASSIFIER TRAINING
              GDPR Compliance Model Training
===============================================================================
    """)

    # Initialize classifier
    classifier = TFIDFClassifier()

    # Train on full dataset
    print("\n[*] Phase 1: Training on labeled dataset...")
    results = classifier.train(dataset_path='data/labeled_dataset.json', test_size=0.25)

    # Create unseen test data (manually selected domains not in training)
    unseen_data = [
        {
            "domain": "pinterest.com",
            "policy_text": "Pinterest Privacy Policy. We collect information you provide content you save and usage data. We use data to provide services show ads and improve Pinterest. We share data with service providers advertisers and other users. You can access and download your data. We keep data while your account is active. We use security measures. Contact us for privacy.",
            "gdpr_controls": {
                "data_minimization": False,
                "purpose_limitation": True,
                "storage_limitation": False,
                "accuracy": True,
                "integrity_confidentiality": True,
                "lawfulness": True,
                "transparency": False,
                "consent": False,
                "data_subject_rights": True,
                "dpo_contact": False
            }
        },
        {
            "domain": "whatsapp.com",
            "policy_text": "WhatsApp Privacy Policy. We collect account information messages you send usage data and device information. We use data to operate provide support and improve our services. We share data with Facebook companies service providers and when required by law. You can access your information. We keep data as necessary for providing services. We use encryption and security measures. Contact our Data Protection Officer.",
            "gdpr_controls": {
                "data_minimization": True,
                "purpose_limitation": True,
                "storage_limitation": True,
                "accuracy": True,
                "integrity_confidentiality": True,
                "lawfulness": True,
                "transparency": True,
                "consent": True,
                "data_subject_rights": True,
                "dpo_contact": True
            }
        },
        {
            "domain": "instagram.com",
            "policy_text": "Instagram Data Policy. We collect content you create information about your activity and device information. We use data to provide personalize and improve our products show ads and communicate. We share data with Facebook companies partners and service providers. You can access port and delete your information. We retain data as long as necessary. We use security measures. Contact us about data.",
            "gdpr_controls": {
                "data_minimization": False,
                "purpose_limitation": True,
                "storage_limitation": False,
                "accuracy": True,
                "integrity_confidentiality": True,
                "lawfulness": True,
                "transparency": True,
                "consent": False,
                "data_subject_rights": True,
                "dpo_contact": False
            }
        }
    ]

    # Test on unseen data
    print("\n[*] Phase 2: Testing on unseen domains...")
    unseen_results = classifier.evaluate_on_unseen(unseen_data)

    # Print summary
    print("\n\n" + "=" * 80)
    print("TRAINING AND TESTING COMPLETE!")
    print("=" * 80)
    print(f"\n[TRAIN] Training Set Performance:")
    print(f"   Samples: {results['train_size']}")
    print(f"   Avg F1 Score: {np.mean([results['controls'][c]['train_f1'] for c in classifier.controls]):.3f}")

    print(f"\n[TEST] Test Set Performance:")
    print(f"   Samples: {results['test_size']}")
    print(f"   Avg F1 Score: {np.mean([results['controls'][c]['test_f1'] for c in classifier.controls]):.3f}")

    print(f"\n[UNSEEN] Unseen Data Performance:")
    print(f"   Samples: {len(unseen_data)}")
    print(f"   Accuracy: {unseen_results['overall_accuracy']:.1%}")

    print("\n[SAVE] Models saved to: data/trained_models/")
    print("\n[DONE] Ready to use in application!")
    print("=" * 80)

if __name__ == '__main__':
    main()
