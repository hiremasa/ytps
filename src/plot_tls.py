import numpy as np
import matplotlib.pyplot as plt
import lightkurve as lk

def get_transit_mask(lc, period, epoch, duration_hours):
    """
    lc : lk.LightCurve
        lightcurve that contains time and flux properties

    Another version using numpy arrays only
    ---------------------------------------
    mask = []
    t0 += np.ceil((time[0] - dur - t0) / period) * period
    for t in np.arange(t0, time[-1] + dur, period):
        mask.extend(np.where(np.abs(time - t) < dur / 2.)[0])
    return  np.array(mask)
    """
    assert isinstance(lc, lk.LightCurve)
    assert (
        (period is not None)
        & (epoch is not None)
        & (duration_hours is not None)
    )
    temp_fold = lc.fold(period, epoch_time=epoch)
    fractional_duration = (duration_hours / 24.0) / period
    phase_mask = np.abs(temp_fold.phase.value) < (fractional_duration * 1.5)
    transit_mask = np.in1d(lc.time.value, temp_fold.time_original[phase_mask].value)
    return transit_mask

def plot_tls(lc_clean, flatten_lc, trend_lc, results, args):
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
        results : 'transitleastsquares.results.transitleastsquaresresults' object
                        from transitleastsquares.transitleastsquares(time, flatten_lc) func.

    ----------

    Returns:
        fig : 'matplotlib.figure.Figure' object
    """
    assert isinstance(lc_clean, lk.LightCurve)
    assert isinstance(flatten_lc, np.ndarray)
    assert isinstance(trend_lc, np.ndarray)
    assert isinstance(results, dict)

    time = lc_clean.time.value
    flux = lc_clean.flux.value

    fig, axes = plt.subplots(2, 2, figsize=(10, 10), tight_layout=True, facecolor="whitesmoke")
    if args.method == "gp":
        fig.suptitle(f"TOI {args.TOI}, TIC {lc_clean.TICID} (sector {args.sector_number})\nMethod {args.method}, {args.kernel}kernel", fontsize=30)
    else:
        fig.suptitle(f"TOI {args.TOI}, TIC {lc_clean.TICID} (sector {args.sector_number})\nMethod {args.method}", fontsize=30) # have to update TOI & sector args
    axes = axes.flatten()

    # 1. clean lc w/ baseline
    ax = axes[0]
    ax.set_title('Clean lc w/ baseline', fontsize=20)
    ax.scatter(time, flux, s=1, color='black', label="raw data")
    ax.plot(time, trend_lc, linewidth=2, color='red', label="baseline", linestyle='dashed')
    ax.legend(loc='best')
    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('Raw flux', fontsize=12)

    # 2. Flatten lc
    ax = axes[1]
    ax.set_title('Flattened lc', fontsize=20)
    ax.scatter(time, flatten_lc, s=1, label='flat')
    # mask = [False] * len(time)
    # for i in range(int((time.max() - results.T0)//results.period) + 1):
    #     mask |= (time >= results.T0 + i * results.period - 5*results.period_uncertainty) & (time <= results.T0 + i * results.period + 5*results.period_uncertainty)
    mask = get_transit_mask(
                lc_clean, results.period, results.T0, results.duration * 24
            )
    ax.scatter(time[mask], flatten_lc[mask], s=1, color="red", label='transit')
    ax.legend()
    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('Detrended flux', fontsize=12)

    # 3. Transit Least Squares SDE
    ax = axes[2]
    ax.axvline(results.period, alpha=0.4, lw=3, label=f"peak = {results.period:.2f} d")
    ax.set_xlim(np.min(results.periods), np.max(results.periods))
    for n in range(2, 10):
        ax.axvline(n*results.period, alpha=0.4, lw=1, linestyle="dashed")
        ax.axvline(results.period/n, alpha=0.4, lw=1, linestyle="dashed")
    ax.set_title('TLS periodogram', fontsize=20)
    ax.set_ylabel(r'SDE')
    ax.set_xlabel('Period (days)')
    ax.plot(results.periods, results.power, color='black', lw=0.5, label="harmonics")
    ax.legend()
    ax.set_xlim(0, max(results.periods))

    # 4. Folded lc
    ax = axes[3]
    ax.plot((results.model_folded_phase-0.5)*results.period, results.model_folded_model, color='red', label="TLS model \nfolded at Porb")
    ax.scatter((results.folded_phase-0.5)*results.period, results.folded_y, s=10, zorder=2, alpha=0.5)
    ax.set_title('Phase-folded lc', fontsize=20)
    # zoom-in to transit center
    ax.set_xlim(-results.duration*2,results.duration*2)
    #plt.xlim(0.48, 0.52)
    ax.ticklabel_format(useOffset=False)
    ax.set_xlabel('Phase (days)', fontsize=12)
    ax.set_ylabel('Relative flux', fontsize=12)
    ax.legend()

    return fig
