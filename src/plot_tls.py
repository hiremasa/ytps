import numpy as np
import matplotlib.pyplot as plt


def plot_tls(lc_clean, flatten_lc, trend_lc, result):
    """Plot a figure for TLS pipline

    This function returns a figure containing 1. clean lc w/ baseline 2. flatten lc 3. periodgram of transit 4. phase folded lc

    ----------

    Args:
        lc_clean : 'lightkurve.lightcurve.TessLightCurve' object
                        from preprocessed lk.search_lightcurve(target) func.
        flatten_lc : 'numpy.ndarray' object
                        from wotan.flatten() func.
        trend_lc : 'numpy.ndarray' object
                        from wotan.flatten() func.
        result : 'transitleastsquares.results.transitleastsquaresresults' object
                        from transitleastsquares.transitleastsquares(time, flatten_lc) func.

    ----------
    
    Returns:
        fig : 'matplotlib.figure.Figure' object
    """
    time = lc_clean.time.value
    flux = lc_clean.flux.value

    fig, axes = plt.subplots(2, 2, figsize=(10, 10), tight_layout=True, facecolor="whitesmoke")
    fig.suptitle(f"TOI {None}, TIC {lc_clean.TICID} (sector {41})", fontsize=30) # have to update TOI & sector args
    axes = axes.flatten()

    # 1. clean lc w/ baseline
    ax = axes[0]
    ax.set_title('Clean lc w/ baseline', fontsize=20)
    ax.scatter(time, flux, s=1, color='black', label="row data")
    ax.plot(time, trend_lc, linewidth=2, color='red', label="base line curve", linestyle='dashed')
    ax.legend(loc='best')
    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('Raw flux', fontsize=12)

    # 2. Flatten lc
    ax = axes[1]
    ax.set_title('Flatten lc', fontsize=20)
    ax.scatter(time, flatten_lc, s=1, label='flat')
    mask = [False] * len(time)
    for i in range(int((time.max() - results.T0)//results.period) + 1):
        mask |= (time >= results.T0 + i * results.period - 5*results.period_uncertainty) & (time <= results.T0 + i * results.period + 5*results.period_uncertainty)
    ax.scatter(time[mask], flatten_lc[mask], s=1, color="red", label='transit')
    ax.legend()
    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('Detrended flux', fontsize=12)

    # 3. Transit Least Squares SDE
    ax = axes[2]
    ax.axvline(results.period, alpha=0.4, lw=3, label=f"peak = {results.period}")
    ax.set_xlim(np.min(results.periods), np.max(results.periods))
    for n in range(2, 10):
        ax.axvline(n*results.period, alpha=0.4, lw=1, linestyle="dashed")
        ax.axvline(results.period/n, alpha=0.4, lw=1, linestyle="dashed")
    ax.set_title('Transit Least Squares SDE', fontsize=20)
    ax.set_ylabel(r'SDE')
    ax.set_xlabel('Period (days)')
    ax.plot(results.periods, results.power, color='black', lw=0.5, label="Othe periods [d]")
    ax.legend()
    ax.set_xlim(0, max(results.periods))

    # 4. Folded lc
    ax = axes[3]
    ax.plot(results.model_folded_phase, results.model_folded_model, color='red', label="TLS model \nfoled at Prot")
    ax.scatter(results.folded_phase, results.folded_y, s=10, zorder=2, alpha=0.5)
    #plt.xlim(0.48, 0.52)
    ax.ticklabel_format(useOffset=False)
    ax.set_xlabel('Phase')
    ax.set_ylabel('Relative flux')
    ax.legend()
    
    return fig