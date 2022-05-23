import numpy as np


class Stats:
    def __init__(self, mean, err, variance, tau, r_hat):
        self.mean = mean
        self.err = err
        self.variance = variance
        self.tau = tau
        self.r_hat = r_hat

    def __repr__(self):
        return f"{self.mean} ± {self.err} [σ²={self.variance}, τ={self.tau}, R̂={self.r_hat}"


class StatsArray:
    def __init__(self, mean, err, variance, tau, r_hat):
        self.mean = mean
        self.err = err
        self.variance = variance
        self.tau = tau
        self.r_hat = r_hat

    def __getitem__(self, i):
        if isinstance(i, int):
            return Stats(
                self.mean[i], self.err[i], self.variance[i], self.tau[i], self.r_hat[i]
            )
        else:
            return StatsArray(
                self.mean[i], self.err[i], self.variance[i], self.tau[i], self.r_hat[i]
            )

    def __repr__(self):
        return f"StatsArray(n={len(self.mean)})"

    def keys(self):
        return ["mean", "err", "variance", "tau", "r_hat"]


dtype_re = [
    ("mean", "f8"),
    ("error", "f8"),
    ("variance", "f8"),
    ("tau", "f8"),
    ("r_hat", "f8"),
]
