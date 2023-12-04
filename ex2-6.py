from matplotlib import pyplot as plt
plt.style.use('ggplot')
import pandas as pd

df = pd.read_csv("débits.csv")

plt.figure(figsize=(5, 3))
plt.bar(df.y, df.Q)
plt.axline((df.y.mean(), df.Q.mean()), slope=0, ls='-.', color='teal',
           label=rf"$\overline{{Q}}={df.Q.mean()}$ m$^3$/s")
plt.ylabel("$Q$ [m$^3$/s]")
plt.legend()
plt.tight_layout()
plt.savefig("figures/Q6/débits.pdf", bbox_inches='tight')
plt.show()
