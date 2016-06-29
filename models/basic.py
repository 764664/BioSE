from sklearn import gaussian_process
from sklearn import svm
from sklearn import linear_model

class BasicEvaluator:
    def __init__(self):
        pass

    @staticmethod
    def evaluate(train, test):
        train_size = len(train)
        # print(train[:5])
        x = []
        y = []
        for paper in train:
            x.append([paper['Journal_IF'], paper['Year']])
            y.append(paper["Score"])
        # gp = gaussian_process.GaussianProcessRegressor(theta0=1e-2, thetaL=1e-4, thetaU=1e-1)
        # gp.fit(x, y)
        # clf = svm.SVR(kernel="rbf")
        clf = linear_model.LinearRegression()
        clf.fit(x, y)
        # print(x)
        # print(clf.coef_)

        for paper in test:
            score = clf.predict([[paper['Journal_IF'], paper['Year']]])[0]
            paper["Score"] = score
            # score = gp.predict([[paper['Journal_IF'], paper['Year']]])[0]
            # paper['TestScore'] = score
