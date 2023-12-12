from hydrogibs.fluvial.profile import Profile
from hydrogibs.fluvial.shields import (
    ShieldsDiagram,
    adimensional_diameter,
    adimensional_shear,
    reynolds
)
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
diam = interp1d(grains["Tamisats [%]"], grains["Diamètre des grains [cm]"]/100)((16, 50, 90))

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
first_it = True
dfs = []
# Diagrammes de profil
for profile, K, Js in zip(PROFILES, GMS, SLOPES):

    # Raw (x, z) data
    df = pd.read_excel(INPUT_FILE, sheet_name=profile, usecols='H:L', dtype=float)
    _x, _z = df[['Dist. cumulée [m]', 'Altitude [m s.m.]']].to_numpy().T

    for k, transform in transformdict.items():
        # Profil transformé
        # Transform coordinates and compute hydraulic data
        x, z = transform(_x, _z, dist=dist, start=start)
        df = Profile(x, z, K, Js)
        # Profile figure
        fig, (ax1, ax2) = df.plot()
        ax1.plot(_x, _z,
                 '-o', ms=8, c='gray', zorder=0,
                 lw=3, label="Profil complet")
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

        dfs.append(df)
# plt.close("all")

# Diagrammes de Shields
colors = plt.rcParams['axes.prop_cycle'].by_key()['color'][1:]
for profile, Js in zip(PROFILES, SLOPES):

    lw=10
    SD = ShieldsDiagram(figsize=(10, 4), plot_kw=dict(label="Limite du charriage"))

    for k, section, c in zip(transformdict.keys(), dfs, colors):
        section = section.query("300 <= Q <= 1600")
        for dv in diam:
            Rh = section.S/section.P
            Rh = np.array([Rh.min(), Rh.max()])
            shear = rho*g*Rh*Js
            s = adimensional_shear(shear, dv, rho_s)
            d = adimensional_diameter(dv, rho_s)
            r = reynolds(np.sqrt(shear/rho), dv)
            SD.plot(s, r, np.full_like(s, d), c=c, lw=lw, label=k.capitalize())
        lw -= 2.5
    fontdict = dict(size=14, alpha=0.6)
    SD.axShields.text(100, 0.5, "$d_{16}$", fontdict)
    SD.axShields.text(700, 0.08, "$d_{50}$", fontdict)
    SD.axShields.text(2000, 0.02, "$d_{90}$", fontdict)

    # Unique legend labels
    handles, labels = SD.axShields.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    SD.axShields.legend(by_label.values(), by_label.keys(), loc=(0.75, 0.53), borderpad=1)
    SD.axShields.set_zorder(SD.axVanRijn.get_zorder()+1)

    SD.figure.tight_layout()
    SD.figure.savefig(f"figures/Q5/solid_{profile}.pdf", bbox_inches='tight')
    SD.figure.show()
plt.show()
