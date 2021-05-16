"""Ridge Regression model from sklearn"""
import datatable as dt
import numpy as np
from h2oaicore.models import CustomModel
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge


class RidgeRegressionModel(CustomModel):
    _regression = True
    _binary = False
    _multiclass = False
    _display_name = "RidgeRegression"
    _description = "Ridge Regression Model based on sklearn"

    def fit(self, X, y, sample_weight=None, eval_set=None, sample_weight_eval_set=None, **kwargs):
        orig_cols = list(X.names)
        
        model = Ridge()
        feature_model = RandomForestRegressor()

        self.means = dict()

        for col in X.names:
            XX = X[:, col]
            self.means[col] = XX.mean1()
            if self.means[col] is None:
                self.means[col] = 0
            XX.replace(None, self.means[col])
            X[:, col] = XX
            assert X[dt.isna(dt.f[col]), col].nrows == 0

        X = X.to_numpy()

        model.fit(X, y)
        feature_model.fit(X, y)

        importances = np.array(feature_model.feature_importances_)
        self.set_model_properties(model=model,
                                  features=orig_cols,
                                  importances=importances.tolist(),
                                  iterations=0)

    def predict(self, X, **kwargs):
        for col in X.names:
            XX = X[:, col]
            XX.replace(None, self.means[col])
            X[:, col] = XX

        model, _, _, _ = self.get_model_properties()

        X = X.to_numpy()

        return model.predict(X)