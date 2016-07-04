from sklearn import gaussian_process
from sklearn import svm
from sklearn import linear_model
from collections import defaultdict

class BasicEvaluator:
    def __init__(self):
        pass

    @staticmethod
    def evaluate(train, test, query):
        train_size = len(train)
        x = []
        y = []
        for paper in train:
            x.append([paper['Journal_IF'], paper['Year']])
            y.append(paper["Score"])
        regressor = linear_model.LinearRegression()
        regressor.fit(x, y)

        for paper in test:
            score = regressor.predict([[paper['Journal_IF'], paper['Year']]])[0]
            paper["Score"] = score

class EvaluatorSVR:
    @staticmethod
    def evaluate(train, test, query):
        train_size = len(train)
        x = []
        y = []
        for paper in train:
            x.append([paper['Journal_IF'], paper['Year']])
            y.append(paper["Score"])
        regressor = svm.SVR(kernel="rbf")
        regressor.fit(x, y)

        for paper in test:
            score = regressor.predict([[paper['Journal_IF'], paper['Year']]])[0]
            paper["Score"] = score

class EvaluatorGP:
    @staticmethod
    def evaluate(train, test, query):
        train_size = len(train)
        x = []
        y = []
        for paper in train:
            x.append([paper['Journal_IF'], paper['Year']])
            y.append(paper["Score"])
        gp = gaussian_process.GaussianProcess()
        gp.fit(x, y)

        for paper in test:
            score = gp.predict([[paper['Journal_IF'], paper['Year']]])[0]
            paper["Score"] = score

class BasicEvaluatorTF:
    def __init__(self):
        pass

    @staticmethod
    def evaluate(train, test, query):
        train_size = len(train)
        x = []
        y = []
        h = defaultdict(int)
        for paper in train:
            tf_abstract = paper["Abstract"].count(query)
            x.append([paper['Journal_IF'], paper['Year'], tf_abstract])
            y.append(paper["Score"])
            h[tf_abstract] += 1

        print(h)
        regressor = linear_model.LinearRegression()
        regressor.fit(x, y)

        for paper in test:
            tf_abstract = paper["Abstract"].count(query)
            score = regressor.predict([[paper['Journal_IF'], paper['Year'], tf_abstract]])[0]
            paper["Score"] = score