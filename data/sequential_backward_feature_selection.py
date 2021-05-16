"""Modify credit dataset"""

from typing import Union, List
from h2oaicore.data import CustomData
import datatable as dt
import numpy as np
import pandas as pd

from sklearn.neighbors import KNeighborsClassifier
from mlxtend.feature_selection import ExhaustiveFeatureSelector as EFS

class SequentialBackwardFeatureSelection(CustomData):
    _modules_needed_by_name = ["mlxtend"]

    @staticmethod
    def sequential_backward_feature_selection(X: dt.Frame = None) -> pd.DataFrame:
        datadf = X.to_pandas()

        data_id = datadf['ID']
        data_y = datadf['default payment next month']
        data_X = datadf.iloc[:,2:data.shape[1] - 1] # radius_mean onwards

        XX = data_X
        y = np.ravel(data_y)

        print("Dataset: ", data.shape)
        print("id: ", data_id.shape)
        print("y: ", data_y.shape)
        print("X: ", data_X.shape)

        knn = KNeighborsClassifier(n_neighbors = 3)
        sfs1 = SFS(knn, 
                k_features=15, 
                forward=True, 
                floating=False, 
                verbose=2,
                scoring='accuracy',
                cv=0)
        sfs1.fit(XX, y)
        support = sfs1.k_feature_names_
        feat_list = list(support)
        col_names_to_pick = feat_list + ['default payment next month']
        new_df = datadf[col_names_to_pick]
        return new_df
