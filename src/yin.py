"""
Implementation of YIN algorithm for CircuitPython, adapted from https://github.com/patriceguyot/Yin/blob/master/yin.py

I was unable to adapt the fastest version of the difference function.
- The complex arrays and conjugate function appear to have been removed from CircuitPython.
- CircuitPython's fft and ifft functions do not use complex arrays.

However I was able to adapt the "scipy" version of the difference function, as the convolve function was actually in the firmware although it wasn't in the documentation.

Functions have been renamed to keep my linter happy.
"""

import ulab.numpy as np
from adafruit_itertools import accumulate

def difference_function_original(x, n, tau_max):
    """
    Compute difference function of data x. This corresponds to equation (6) in [1]

    Original algorithm. This is unused as it is super slow. Keeping it here as reference.

    :param x: audio data (float[])
    :param N: length of data (int)
    :param tau_max: integration window size (int)
    :return: difference function (int[tau_max])
    :rtype: list
    """
    df = [0] * tau_max
    for tau in range(1, tau_max):
        for j in range(0, n - tau_max):
            tmp = x[j] - x[j + tau]
            df[tau] += tmp * tmp
    return df

def difference_function(x, n, tau_max):
    """
    Compute difference function of data x. This corresponds to equation (6) in [1]

    Faster implementation of the difference function.
    The required calculation can be easily evaluated by Autocorrelation function or similarly by convolution.
    Wiener–Khinchin theorem allows computing the autocorrelation with two Fast Fourier transforms (FFT), with time complexity O(n log n).
    This function use an accellerated convolution function fftconvolve from Scipy package.

    :param x: audio data
    :param N: length of data
    :param tau_max: integration window size
    :return: difference function
    :rtype: list
    """
    x = np.array(x)
    w = x.size
    x_cumsum = np.concatenate((np.array([0]), np.array(list(accumulate(x * x)))))
    conv = np.convolve(x, x[::-1])
    #x_cumsum = np.concatenate((np.array([0]), (x * x).cumsum()))
    #conv = fftconvolve(x, x[::-1])
    tmp = x_cumsum[w:0:-1] + x_cumsum[w] - x_cumsum[:w] - 2 * conv[w - 1:]
    # for some reason the original code produces one more element
    # return tmp[:tau_max + 1]
    return tmp[:tau_max]


def cumulative_mean_normalized_difference_function(df, n):
    """
    Compute cumulative mean normalized difference function (CMNDF).

    This corresponds to equation (8) in [1]

    :param df: Difference function (int[tau_max])
    :param N: length of data (int)
    :return: cumulative mean normalized difference function (float[tau_max + 1])
    :rtype: list
    """

    cmndf =  df[1:] * np.array(range(1, n)) / np.array(list(accumulate(df[1:])))
    #cmndf = df[1:] * range(1, N) / np.cumsum(df[1:]).astype(float) #scipy method
    return np.concatenate((np.ones(1), cmndf))

def get_pitch(cmdf, tau_min, tau_max, harmo_th=0.1):
    """
    Return fundamental period of a frame based on CMNDF function.

    :param cmdf: Cumulative Mean Normalized Difference function (float[tau_max + 1])
    :param tau_min: minimum period for speech
    :param tau_max: maximum period for speech
    :param harmo_th: harmonicity threshold to determine if it is necessary to compute pitch frequency
    :return: fundamental period if there is values under threshold, 0 otherwise
    :rtype: float
    """
    tau = tau_min
    while tau < tau_max:
        if cmdf[tau] < harmo_th:
            while tau + 1 < tau_max and cmdf[tau + 1] < cmdf[tau]:
                tau += 1
            return tau
        tau += 1

    return 0    # if unvoiced

def compute_yin(sig, sr, w_len=512, w_step=256, f0_min=100, f0_max=500, harmo_thresh=0.1):
    """
    Compute the Yin Algorithm. Return fundamental frequency and harmonic rate.

    :param sig: Audio signal (list of float)
    :param sr: sampling rate (int)
    :param w_len: size of the analysis window (samples)
    :param w_step: size of the lag between two consecutives windows (samples)
    :param f0_min: Minimum fundamental frequency that can be detected (hertz)
    :param f0_max: Maximum fundamental frequency that can be detected (hertz)
    :param harmo_tresh: Threshold of detection. The yalgorithmù return the first minimum of the CMND fubction below this treshold.

    :returns:

        * pitches: list of fundamental frequencies,
        * harmonic_rates: list of harmonic rate values for each fundamental frequency value (= confidence value)
        * argmins: minimums of the Cumulative Mean Normalized DifferenceFunction
        * times: list of time of each estimation
    :rtype: tuple
    """

    #print('Yin: compute yin algorithm')
    tau_min = int(sr / f0_max)
    tau_max = int(sr / f0_min)

    time_scale = range(0, len(sig) - w_len, w_step)  # time values for each analysis window
    times = [t/float(sr) for t in time_scale]
    frames = [sig[t:t + w_len] for t in time_scale]

    pitches = [0.0] * len(time_scale)
    harmonic_rates = [0.0] * len(time_scale)
    argmins = [0.0] * len(time_scale)

    for i, frame in enumerate(frames):

        # Compute YIN
        df = difference_function(frame, w_len, tau_max)
        cmdf = cumulative_mean_normalized_difference_function(df, tau_max)
        p = get_pitch(cmdf, tau_min, tau_max, harmo_thresh)

        # Get results
        if np.argmin(cmdf)>tau_min:
            argmins[i] = float(sr / np.argmin(cmdf))
        if p != 0: # A pitch was found
            pitches[i] = float(sr / p)
            harmonic_rates[i] = cmdf[p]
        else: # No pitch, but we compute a value of the harmonic rate
            harmonic_rates[i] = min(cmdf)

    return pitches, harmonic_rates, argmins, times
