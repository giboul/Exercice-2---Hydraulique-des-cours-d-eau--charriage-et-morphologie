import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from hydrogibs.fluvial.shields import shields_diagram
from hydrogibs.fluvial.canal import Section
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
diam = {f"$d_{{{dk}}}$": dv for dk, dv in zip((16, 50, 90), granulometry((16, 50, 90)))}

fig = plt.figure(figsize=(12, 4.5))

axes=None
frontier = True
lw = 6
for profile, K, slope in zip(PROFILES, GMS, SLOPES):

    # read profile
    df = pd.read_excel(INPUT_FILE, sheet_name=profile,
                       usecols=USECOLS, dtype=float)
    # Initialisation de l'objet
    section = Section(
        df['Dist. cumulée [m]'],
        df['Altitude [m s.m.]'],
    ).compute_GMS_data(K, slope).compute_critical_data()
    section = section.data.query("300 <= Q <= 1600")
    # Diagramme de Shields
    _, axes = shields_diagram(diam.values(),
                              section.S/section.P,
                              slope,
                              diameter_labels=diam.keys(),
                              lw=lw,
                              axes=axes,
                              plot_frontier=frontier,
                              show=False)
    if frontier is True:
        frontier = False
    lw -= 3

axes[0].set_zorder(axes[1].get_zorder()+1)
axes[0].legend(ncols=2, title=f"{'Rhone 18.947':^15} {'Rhone 18.846':^15}", loc=(0.65, 0.67))
fig.savefig("figures/Q2/shields.pdf", bbox_inches='tight')
plt.show()


# Shear diagram
for profile, K, slope in zip(PROFILES, GMS, SLOPES):

    # read profile
    df = pd.read_excel(INPUT_FILE, sheet_name=profile,
                       usecols=USECOLS, dtype=float)
    # Initialisation de l'objet
    section = Section(
        df['Dist. cumulée [m]'],
        df['Altitude [m s.m.]'],
    ).compute_GMS_data(K, slope).compute_critical_data()

    fig = plt.figure(figsize=(9, 4))

    plt.plot(section.rawdata.x, section.rawdata.z, '-ok', mfc='w', mew=2, label='Lit')

    data_section = section.data.query("Q <= 1600")
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
