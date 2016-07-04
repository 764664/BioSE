from sklearn import linear_model, preprocessing, svm
from collections import defaultdict
import math

class Model:
    def __init__(self, train, test, query):
        self.train = train
        self.test = test
        self.query = query
        self.preprocessing()
        self.construct_train_data()
        self.train_model()
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

    def postprocessing(self):
        pass

class Model1(Model):
    pass

class Model2(Model):
    def train_model(self):
        regressor = svm.SVR(kernel="rbf")
        regressor.fit(self.x, self.y)
        self.model = regressor

class Model3(Model):
    def train_model(self):
        regressor = svm.SVR(kernel="linear")
        regressor.fit(self.x, self.y)
        self.model = regressor

class Model4(Model):
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
    def train_model(self):
        regressor = svm.SVR(kernel="linear")
        regressor.fit(self.x, self.y)
        self.model = regressor

class Model6(Model5):
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
    def construct_train_data(self):
        x, y = [], []
        for paper in self.train:
            x.append([paper['Journal_IF'], paper['Year']])
            y.append(paper["Score"])
        self.scaler = preprocessing.StandardScaler().fit(x)
        x = self.scaler.transform(x)
        self.x = x
        self.y = y

    def predict(self, paper):
        x = self.scaler.transform([[paper['Journal_IF'], paper['Year']]])
        score = self.model.predict(x)[0]
        paper["Score"] = score

class Model8(Model):
    def construct_train_data(self):
        x, y = [], []
        for paper in self.train:
            x.append([paper['Year']])
            y.append(paper["Score"])
        self.scaler = preprocessing.StandardScaler().fit(x)
        self.scaler.transform(x)
        self.x = x
        self.y = y

    def predict(self, paper):
        x = self.scaler.transform([[paper['Year']]])
        score = self.model.predict(x)[0]
        paper["Score"] = score

class Model9(Model):
    def construct_train_data(self):
        x, y = [], []
        for paper in self.train:
            x.append([paper['Journal_IF']])
            y.append(paper["Score"])
        self.scaler = preprocessing.StandardScaler().fit(x)
        self.scaler.transform(x)
        self.x = x
        self.y = y

    def predict(self, paper):
        x = self.scaler.transform([[paper['Journal_IF']]])
        score = self.model.predict(x)[0]
        paper["Score"] = score

class Model10(Model3):
    def construct_train_data(self):
        x, y = [], []
        for paper in self.train:
            x.append([paper['Journal_IF'], paper['Year']])
            y.append(paper["Score"])
        self.scaler = preprocessing.StandardScaler().fit(x)
        self.scaler.transform(x)
        self.x = x
        self.y = y

    def predict(self, paper):
        x = self.scaler.transform([[paper['Journal_IF'], paper['Year']]])
        score = self.model.predict(x)[0]
        paper["Score"] = score

class Model11(Model7):
    def train_model(self):
        regressor = clf = linear_model.Ridge()
        regressor.fit(self.x, self.y)
        self.model = regressor

class Model12(Model1):
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

    def predict(self, paper):
        tf_abstract = paper["Abstract"].count(self.query)
        tf_title = paper["Title"].count(self.query)
        x = self.scaler.transform([[paper['Journal_IF'], paper['Year'], tf_abstract*self.idf_abstract, tf_title*self.idf_title]])
        score = self.model.predict(x)[0]
        paper["Score"] = score