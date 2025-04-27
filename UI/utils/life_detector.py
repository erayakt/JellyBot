from sklearn.ensemble import IsolationForest
import numpy as np

from sklearn.ensemble import IsolationForest
import numpy as np

class LifeDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.X = []
        self.is_fitted = False

    def add_sample(self, sample):
        self.X.append(sample)
        if len(self.X) > 30 and not self.is_fitted:
            self.model.fit(self.X)
            self.is_fitted = True

    def predict_interest(self, sample):
        if not self.is_fitted:
            return 0.0  # Model not ready yet
        pred = self.model.decision_function([sample])[0]
        interestingness = 1.0 - (pred + 0.5)  # Normalize
        return max(0.0, min(1.0, interestingness))

