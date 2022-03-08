# learning rate
L = 0.001


def mse_m1_pd(m1, m2, k, n, ind, dep):
    sum = 0
    for i in range(n):
        c = (2*m1*ind[i][0]**2 + 2*m2*ind[i][0]*ind[i][1] +
             2*k*ind[i][0]
             - 2*ind[i][0]*dep[i]
             )

        sum += c

    result = sum / n
    return result


def mse_m2_pd(m1, m2, k, n, ind, dep):
    sum = 0
    for i in range(n):
        c = (2*m1*ind[i][0]*ind[i][1] +
             + 2*m2*ind[i][1]**2 +
             2*k*ind[i][1]
             - 2*ind[i][1]*dep[i]
             )

        sum += c

    result = sum / n
    return result


def mse_k_pd(m1, m2, k, n, ind, dep):
    sum = 0
    for i in range(n):
        c = (
            2*m1*ind[i][0] +
            2*m2*ind[i][1]
            + 2*k
            - 2*dep[i])

        sum += c

    result = sum / n
    return result


def linear_regression_2(m1, m2, k, n, ind, dep):
    new_m1 = m1 - L * mse_m1_pd(m1, m2, k, n, ind, dep)
    new_m2 = m2 - L * mse_m2_pd(new_m1, m2, k, n, ind, dep)
    new_k = k - L * mse_k_pd(new_m1, new_m2, k, n, ind, dep)
    return (new_m1, new_m2, new_k)


def perform2VariableLinearRegression(n, ind, dep):
    # number of instances of training data
    # e.g. n = 9
    # values for each of the two independent variables
    # e.g. ind = [(0,30),(1,25),(2,20),(3,15),(4,10),(5,5),(5,0),(5,30),(5,25)]
    # corresponding values for dependent variable
    # e.g. dep = [1.8,2.7,3.4,3.9,4.4,4.9,5,4,4.4]

    # initial model parameters
    m1 = 0
    m2 = 0
    k = 0

    # refine with 100 epochs
    for epoch in range(10000):
        (m1, m2, k) = linear_regression_2(m1, m2, k, n, ind, dep)

    # output final model
    return (m1, m2, k)
