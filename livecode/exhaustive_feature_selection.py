"""Modify credit card dataset"""

from typing import Union, List
from h2oaicore.data import CustomData
import datatable as dt
import numpy as np
import pandas as pd

from sklearn.neighbors import KNeighborsClassifier
from mlxtend.feature_selection import ExhaustiveFeatureSelector as EFS

class ExhaustiveFeatureSelection(CustomData):
    _modules_needed_by_name = ["mlxtend"]

    @staticmethod
    def exhaustive_feature_selection(X: dt.Frame = None):
        if X is None:
                return []
        # X[:, 'default payment next month leak'] = X[:, 'default payment next month']
        datadf = X.to_pandas()
        data_y = datadf['default payment next month']
        data_X = datadf.iloc[:,:datadf.shape[1] - 1] # radius_mean onwards
        XX = data_X
        y = np.ravel(data_y)
        #
        knn = KNeighborsClassifier(n_neighbors=3)

        efs1 = EFS(knn, 
                min_features=5,
                max_features=10,
                scoring='accuracy',
                print_progress=True,
                cv=5)

        efs1 = efs1.fit(XX, y)
        support = sfs1.k_feature_names_
        feat_list = list(support)
        # get the new features
        col_names_to_pick = feat_list + ['default payment next month']
        new_df = datadf[col_names_to_pick]
        new_dt = dt.Frame(new_df)
        return new_dt
