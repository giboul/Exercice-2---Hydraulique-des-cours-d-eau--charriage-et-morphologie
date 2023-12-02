from hydrogibs.fluvial.canal import Section
from hydrogibs.fluvial.shields import shields_diagram
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
plt.style.use('ggplot')


# Base data
INPUT_FILE = (
    '2023_CIVIL-410_Exercice2_'
    'Biblio_hydraulique_Profils_Rhone_et_Shields.xlsm'
)
PROFILES = ('Rhone18.846', 'Rhone18.947')
GMS = (33, 32)
SLOPES = (0.12/100, 0.13/100)

# Granulometry : d16, d50, d90
grains = pd.read_excel(INPUT_FILE, sheet_name="Granulométrie")
dk = interp1d(grains["Tamisats [%]"], grains["Diamètre des grains [cm]"]/100)((16, 50, 90))

# Constantes du fichier
constants = pd.read_excel(INPUT_FILE, sheet_name="Shields", usecols="H:K").dropna()
rho_s, rho, g, nu = constants.Valeur.to_numpy().T

# Différentes fonctions d'élargissement

def translate(x, z, dist, start=None):
    x = x.copy()
    if start is None:
        start = x.min() + (x.max()-x.min()) / 2
    x[start >= x] -= dist
    return x, z


def extend(x, z, dist, start=None):
    x = x.copy()
    if start is None:
        start = x.min() + (x.max()-x.min()) / 2
    mask = start >= x
    x[mask] = x[mask] - (start - x[mask]) * dist / (start - x.min())
    return x, z


def elongate(x, z, dist, start=None):
    x = x.copy()
    return x * (1 + dist/(x.max() - x.min())) - dist, z


def linearize(x, z, dist, start):
    mask = x <= start
    zm = np.sort(z[mask])[::-1]
    z[mask] = zm
    x[mask] = -dist + (start + dist) * (zm[0] - zm)/(zm[0] - zm[-1])
    return x, z


transformdict = dict(
    identité=lambda x, z, *args, **kwargs: (x, z),
    translation=translate,
    linéarisation=linearize,
    extension=extend,
    # elongate=elongate,
)

dist = 45  # Élargissement de 45 m
start = 40  # Commence au 40e mètre

for profile, K, Js in zip(PROFILES, GMS, SLOPES):

    # Raw (x, z) data
    df = pd.read_excel(INPUT_FILE, sheet_name=profile, usecols='H:L', dtype=float)
    _x, _z = df[['Dist. cumulée [m]', 'Altitude [m s.m.]']].to_numpy().T
    
    # Figure for shields diagram
    solidfig, (solidax1, solidax2) = plt.subplots(figsize=(10, 4), ncols=2, gridspec_kw=dict(wspace=0))
    cycle = solidax1._get_lines.prop_cycler

    lw=10
    first_it = True
    for k, transform in transformdict.items():

        # Initialize section without hydraulic data
        section = Section(_x, _z, process=False).preprocess()
        x, z = section.data[["x", "z"]].to_numpy().T

        # Transform coordinates and compute hydraulic data
        section.data.x, section.data.z = transform(section.x, section.z, dist=dist, start=start)
        section = section.compute_geometry().compute_critical_data().compute_GMS_data(K, Js)

        # Profile figure
        fig, (ax1, ax2) = section.plot(show=False)
        fig.set_size_inches(6, 3)
        ax2.dataLim.x0 = 300
        ax2.dataLim.x1 = 1600
        ax2.autoscale_view()

        if first_it is True:
            lns = ax1.get_lines() + ax2.get_lines()
            labs = [l.get_label() for l in lns]
            ax1.legend(lns, labs, loc='upper center')
            legend = False
            frontier = True
            first_it = False
        else:
            ax1.get_legend().remove()
            frontier = False
        fig.savefig(f"figures/Q5/profiles/{k}_{profile}.pdf", bbox_inches='tight')
        fig.show()

        # _fig, _ax = plt.subplots()
        # _h = np.linspace(1, 3, num=1000)
        # _ax.plot(_h, section.interp_B(_h))
        # _ax.set_title(k)
        # _ax.set_xlabel("h (m)")
        # _ax.set_ylabel("B (m)")
        # _fig.show()

        # Shields diagram
        section.data = section.data.query("300 <= Q <= 1600")
        print(f"{profile} | {k = :^20} | {section.data.h.to_numpy()[-1] = :.1f}")
        styling = dict(lw=lw, ls='-', show=False,
                       fig=solidfig,
                       axes=(solidax1, solidax2),
                       label=k.capitalize(),
                       color=next(cycle)['color'],
                       plot_frontier=frontier)
        shields_diagram(dk, section.S/section.P, Js, ** styling)
        lw -= 2.5

    fontdict = dict(size=14, alpha=0.6)
    solidax1.text(100, 0.5, "$d_{16}$", fontdict)
    solidax1.text(700, 0.08, "$d_{50}$", fontdict)
    solidax1.text(2000, 0.02, "$d_{90}$", fontdict)

    handles, labels = solidax1.get_legend_handles_labels()
    labels[0] = "Limite du charriage"
    by_label = dict(zip(labels, handles))
    solidax1.legend(by_label.values(), by_label.keys(), loc=(0.75, 0.53), borderpad=1)
    solidax1.set_zorder(10)
    solidfig.tight_layout()
    solidfig.savefig(f"figures/Q5/solid_{profile}.pdf", bbox_inches='tight')
    solidfig.show()
plt.show()
