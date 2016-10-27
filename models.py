from sklearn import linear_model, preprocessing, svm, tree, ensemble
import math
from sklearn import preprocessing
import tensorflow as tf
from tensorflow.contrib import learn
import random
from IPython import embed

class Model:
    def __init__(self, train, test, query):
        self.use_predict_many = False
        for paper in test:
            paper['Score'] = random.random()
        self.use_predict_many = False
        self.train = train
        self.test = test
        self.query = query
        self.preprocessing()
        self.construct_train_data()
        self.train_model()
        if self.use_predict_many:
            self.predict_many(test)
        else:
            for paper in test:
                self.predict(paper)
        self.postprocessing()

    def preprocessing(self):
        pass

    def construct_train_data(self):
        x, y = [], []
        for paper in self.train:
            x.append([paper['Journal_IF'], paper['Year']])
            y.append(paper["Score"])
        self.x = x
        self.y = y

    def train_model(self):
        regressor = linear_model.LinearRegression()
        regressor.fit(self.x, self.y)
        self.model = regressor

    def predict(self, paper):
        score = self.model.predict([[paper['Journal_IF'], paper['Year']]])[0]
        paper["Score"] = score
        # print(score)

    def predict_many(self, test):
        pass

    def postprocessing(self):
        pass

class Model1(Model):
    """linear regression, IF+Year"""
    pass

class Model2(Model):
    """SVR(RBF), IF+Year"""
    def train_model(self):
        regressor = svm.SVR(kernel="rbf")
        regressor.fit(self.x, self.y)
        self.model = regressor

class Model3(Model):
    """SVR(Linear), IF+Year"""
    def train_model(self):
        regressor = svm.SVR(kernel="linear")
        regressor.fit(self.x, self.y)
        self.model = regressor

class Model4(Model):
    """linear regression, IF+Year+TF_Of_Query_In_Abstract"""
    def construct_train_data(self):
        x, y = [], []
        for paper in self.train:
            tf_abstract = paper["Abstract"].count(self.query)
            x.append([paper['Journal_IF'], paper['Year'], tf_abstract])
            y.append(paper["Score"])
        self.x = x
        self.y = y

    def predict(self, paper):
        tf_abstract = paper["Abstract"].count(self.query)
        score = self.model.predict([[paper['Journal_IF'], paper['Year'], tf_abstract]])[0]
        paper["Score"] = score

class Model5(Model4):
    """SVR(Linear), IF+Year+TF_Of_Query_In_Abstract"""
    def train_model(self):
        regressor = svm.SVR(kernel="linear")
        regressor.fit(self.x, self.y)
        self.model = regressor

class Model6(Model5):
    """SVR(Linear), IF+Year+TF_Of_Query_In_Abstract+TF_Of_Query_In_Title"""
    def construct_train_data(self):
        x, y = [], []
        for paper in self.train:
            tf_abstract = paper["Abstract"].count(self.query)
            tf_title = paper["Title"].count(self.query)
            x.append([paper['Journal_IF'], paper['Year'], tf_abstract, tf_title])
            y.append(paper["Score"])
        self.x = x
        self.y = y

    def predict(self, paper):
        tf_abstract = paper["Abstract"].count(self.query)
        tf_title = paper["Title"].count(self.query)
        score = self.model.predict([[paper['Journal_IF'], paper['Year'], tf_abstract, tf_title]])[0]
        paper["Score"] = score

class Model7(Model):
    """linear regression, IF+Year, with Standardlization"""
    def construct_train_data(self):
        x, y = [], []
        for paper in self.train:
            x.append([paper['Journal_IF'], paper['Year']])
            y.append(paper["Score"])
        self.x = preprocessing.StandardScaler().fit_transform(x)
        self.y = y
        self.use_predict_many = True

    def predict_many(self, test):
        x = []
        for paper in self.test:
            x.append([paper['Journal_IF'], paper['Year']])
        x = preprocessing.StandardScaler().fit_transform(x)
        scores = self.model.predict(x)
        for idx, paper in enumerate(test):
            paper["Score"] = scores[idx]

class Model8(Model):
    """linear regression, Year, with Standardlization"""
    def construct_train_data(self):
        x, y = [], []
        for paper in self.train:
            x.append([paper['Year']])
            y.append(paper["Score"])
        self.x = preprocessing.StandardScaler().fit_transform(x)
        self.y = y
        self.use_predict_many = True

    def predict_many(self, test):
        x = []
        for paper in self.test:
            x.append([paper['Year']])
        x = preprocessing.StandardScaler().fit_transform(x)
        scores = self.model.predict(x)
        for idx, paper in enumerate(test):
            paper["Score"] = scores[idx]

class Model9(Model):
    """linear regression, IF"""
    def construct_train_data(self):
        x, y = [], []
        for paper in self.train:
            x.append([paper['Journal_IF']])
            y.append(paper["Score"])
        self.x = preprocessing.StandardScaler().fit_transform(x)
        self.y = y
        self.use_predict_many = True

    def predict_many(self, test):
        x = []
        for paper in self.test:
            x.append([paper['Journal_IF']])
        x = preprocessing.StandardScaler().fit_transform(x)
        scores = self.model.predict(x)
        for idx, paper in enumerate(test):
            paper["Score"] = scores[idx]

class Model10(Model3):
    """SVR(Linear), IF+Year, with Standardlization"""
    def construct_train_data(self):
        x, y = [], []
        for paper in self.train:
            x.append([paper['Journal_IF'], paper['Year']])
            y.append(paper["Score"])
        self.x = preprocessing.StandardScaler().fit_transform(x)
        self.y = y
        self.use_predict_many = True

    def predict_many(self, test):
        x = []
        for paper in self.test:
            x.append([paper['Journal_IF'], paper['Year']])
        x = preprocessing.StandardScaler().fit_transform(x)
        scores = self.model.predict(x)
        for idx, paper in enumerate(test):
            paper["Score"] = scores[idx]


class Model11(Model7):
    """Ridge Regression, IF+Year, with Standardlization"""
    def train_model(self):
        regressor = linear_model.Ridge()
        regressor.fit(self.x, self.y)
        self.model = regressor

class Model12(Model1):
    """linear regression, IF+Year+TF_In_Abstract+TF_In_Title, with Standardlization"""
    def construct_train_data(self):
        x, y = [], []
        n = len(self.train)
        nt_abstract = len([ paper for paper in self.train if paper["Abstract"].find(self.query) >= 0 ])
        nt_title = len([ paper for paper in self.train if paper["Title"].find(self.query) >= 0 ])
        idf_abstract = math.log(n/nt_abstract) if nt_abstract!=0 else 10000
        idf_title = math.log(n/nt_title) if nt_title!=0 else 10000
        self.idf_abstract = idf_abstract
        self.idf_title = idf_title
        for paper in self.train:
            tf_abstract = paper["Abstract"].count(self.query)
            tf_title = paper["Title"].count(self.query)
            x.append([paper['Journal_IF'], paper['Year'], tf_abstract, tf_title])
            # x.append([paper['Journal_IF'], paper['Year'], tf_abstract*idf_abstract, tf_title*idf_title])
            y.append(paper["Score"])
        self.x = preprocessing.StandardScaler().fit_transform(x)
        # self.x = x
        self.y = y
        self.use_predict_many = True

    def predict_many(self, test):
        x = []
        for paper in self.test:
            tf_abstract = paper["Abstract"].count(self.query)
            tf_title = paper["Title"].count(self.query)
            x.append([paper['Journal_IF'], paper['Year'], tf_abstract, tf_title])
            # x.append([paper['Journal_IF'], paper['Year'], tf_abstract*self.idf_abstract, tf_title*self.idf_title])
        x = preprocessing.StandardScaler().fit_transform(x)
        # x = x
        scores = self.model.predict(x)
        for idx, paper in enumerate(test):
            paper["Score"] = scores[idx]

class Model13(Model1):
    """Fix waited, DNN, IF+Year+TF_In_Abstract+TF_In_Title, with Standardlization"""
    def construct_train_data(self):
        x, y = [], []
        n = len(self.train)
        nt_abstract = len([ paper for paper in self.train if paper["Abstract"].find(self.query) >= 0 ])
        nt_title = len([ paper for paper in self.train if paper["Title"].find(self.query) >= 0 ])
        idf_abstract = math.log(n/nt_abstract) if nt_abstract!=0 else 10000
        idf_title = math.log(n/nt_title) if nt_title!=0 else 10000
        self.idf_abstract = idf_abstract
        self.idf_title = idf_title
        for paper in self.train:
            tf_abstract = paper["Abstract"].count(self.query)
            tf_title = paper["Title"].count(self.query)
            x.append([paper['Journal_IF'], paper['Year'], tf_abstract*idf_abstract, tf_title*idf_title])
            y.append(paper["Score"])
        self.scaler = preprocessing.StandardScaler().fit(x)
        x = self.scaler.transform(x)
        self.x = x
        self.y = y

    def train_model(self):
        feature_columns = learn.infer_real_valued_columns_from_input(self.x)
        regressor = learn.DNNRegressor(
            feature_columns=feature_columns, hidden_units=[10, 10])
        regressor.fit(self.x, self.y, steps=500, batch_size=1)
        self.model = regressor

    def predict(self, paper):
        tf_abstract = paper["Abstract"].count(self.query)
        tf_title = paper["Title"].count(self.query)
        x = self.scaler.transform([[paper['Journal_IF'], paper['Year'], tf_abstract*self.idf_abstract, tf_title*self.idf_title]])
        score = self.model.predict(x)
        paper["Score"] = score

class Model14(Model12):
    """Decision Tree, IF+Year+TF_In_Abstract+TF_In_Title, with Standardlization"""
    def train_model(self):
        regressor = tree.DecisionTreeRegressor()
        regressor.fit(self.x, self.y)
        self.model = regressor


class Model15(Model12):
    """AdaBoost, IF+Year+TF_In_Abstract+TF_In_Title, with Standardlization"""
    def train_model(self):
        regressor = ensemble.AdaBoostRegressor()
        regressor.fit(self.x, self.y)
        self.model = regressor

class Model16(Model12):
    """Random Forest, IF+Year+TF_In_Abstract+TF_In_Title, with Standardlization"""
    def train_model(self):
        regressor = ensemble.RandomForestRegressor()
        regressor.fit(self.x, self.y)
        self.model = regressor

class Model17(Model1):
    """Decision Tree, IF+Year"""
    def train_model(self):
        regressor = tree.DecisionTreeRegressor()
        regressor.fit(self.x, self.y)
        self.model = regressor