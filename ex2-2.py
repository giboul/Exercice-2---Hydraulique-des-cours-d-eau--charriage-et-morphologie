import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from hydrogibs.fluvial.shields import (
    ShieldsDiagram,
    adimensional_diameter,
    adimensional_shear,
    reynolds
)
from hydrogibs.fluvial.profile import Profile
from matplotlib import pyplot as plt
plt.style.use('ggplot')
colors = plt.rcParams["axes.prop_cycle"].by_key()['color']


INPUT_FILE = (
    '2023_CIVIL-410_Exercice2_'
    'Biblio_hydraulique_Profils_Rhone_et_Shields.xlsm'
)
PROFILES = ('Rhone18.846', 'Rhone18.947')
USECOLS = 'H:K'
GMS = (33, 32)
SLOPES = (0.12/100, 0.13/100)


# Constantes du fichier
constants = pd.read_excel(INPUT_FILE, sheet_name="Shields", usecols=USECOLS).dropna()
rho_s, rho, g, nu = constants.Valeur.to_numpy().T

# Granulométrie
grains = pd.read_excel(INPUT_FILE, sheet_name="Granulométrie")
granulometry = interp1d(grains["Tamisats [%]"], grains["Diamètre des grains [cm]"]/100)
diam = {f"d_{{{dk}}}": dv for dk, dv in zip((16, 50, 90), granulometry((16, 50, 90)))}

# Shields Diagram
lw = 6
SD = ShieldsDiagram(figsize=(12, 4.5))
for profile, K, slope in zip(PROFILES, GMS, SLOPES):

    # read profile
    df = pd.read_excel(INPUT_FILE, sheet_name=profile,
                       usecols=USECOLS, dtype=float)
    # Initialisation de l'objet
    section = Profile(
        df['Dist. cumulée [m]'],
        df['Altitude [m s.m.]'],
        K,
        slope
    )
    section = section.df.query("300 <= Q <= 1600").sort_values("h")
    shear = rho*g*section.S/section.P*slope

    # Diagramme de Shields
    for dk, dv in diam.items():
        r = reynolds(np.sqrt(shear/rho), dv)
        s = adimensional_shear(shear, dv, rho_s)
        d = adimensional_diameter(np.full_like(shear, fill_value=dv), rho_s)
        SD.plot(s, r, d, lw=lw, label=f"${dk}={dv*100:.1f}$ cm")
    lw -= 3

SD.axShields.set_zorder(SD.axVanRijn.get_zorder()+1)
SD.axShields.legend(ncols=2, title=f"{'Rhone 18.947':^15} {'Rhone 18.846':^15}", loc=(0.65, 0.67))
SD.figure.tight_layout()
SD.figure.savefig("figures/Q2/shields.pdf", bbox_inches='tight')
plt.show()


# Shear diagram
for profile, K, slope in zip(PROFILES, GMS, SLOPES):

    # read profile
    df = pd.read_excel(INPUT_FILE, sheet_name=profile,
                       usecols=USECOLS, dtype=float)
    # Initialisation de l'objet
    section = Profile(
        df['Dist. cumulée [m]'],
        df['Altitude [m s.m.]'],
        K,
        slope
    )

    fig = plt.figure(figsize=(9, 4))

    plt.plot(section.rawdata.x, section.rawdata.z, '-ok', mfc='w', mew=2, label='Lit')

    data_section = section.df.query("Q <= 1600")
    z1600 = data_section.h.max() + data_section.z.min()
    h = np.maximum(0, z1600 - data_section.z)
    tp = 1000*9.81*h*slope
    plt.fill_between(data_section.x,
                     data_section.z,
                     data_section.z - 2*tp/tp.max(),
                     hatch='|',
                     edgecolor='r',
                     label=rf'Contrainte pariétale: $\tau_{{max}}={tp.max():.0f}$ Pa')
    plt.fill_between(data_section.x,
                     data_section.z,
                     data_section.z + h,
                     alpha=0.3,
                     color='b',
                     label=rf'Section mouillée')
    plt.xlabel("Distance profil [m]")
    plt.ylabel("Altitude [m.s.m.]")
    plt.tight_layout()
    plt.legend(loc='center')
    plt.savefig(f"figures/Q2/diagramme_tau_{profile}.pdf", bbox_inches='tight')
    plt.show()
