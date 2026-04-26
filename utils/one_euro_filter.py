import math
import time

class OneEuroFilter:
    def __init__(self, mincutoff=1.0, beta=0.0, dcutoff=1.0):
        """
        OneEuroFilter: A speed-based low-pass filter for noisy tracking.
        - mincutoff: Decreasing this reduces jitter at low speeds (but increases lag).
        - beta: Increasing this reduces lag at high speeds (but increases jitter).
        """
        self.mincutoff = mincutoff
        self.beta = beta
        self.dcutoff = dcutoff
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    def __call__(self, x, t=None):
        if t is None:
            t = time.time()
            
        if self.t_prev is None:
            self.x_prev = x
            self.t_prev = t
            return x

        te = t - self.t_prev
        
        # Prevent division by zero if time difference is extremely small
        if te < 1e-5:
            return self.x_prev

        ad = self.smoothing_factor(te, self.dcutoff)
        dx = (x - self.x_prev) / te
        dx_hat = self.exponential_smoothing(ad, dx, self.dx_prev)

        cutoff = self.mincutoff + self.beta * abs(dx_hat)
        a = self.smoothing_factor(te, cutoff)
        x_hat = self.exponential_smoothing(a, x, self.x_prev)

        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t

        return x_hat

    def smoothing_factor(self, te, cutoff):
        r = 2 * math.pi * cutoff * te
        return r / (r + 1)

    def exponential_smoothing(self, a, x, x_prev):
        return a * x + (1 - a) * x_prev
