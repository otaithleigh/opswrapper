import matplotlib.pyplot as plt
import numpy as np
import opswrapper as ops

#--[ Configuration ]-----------------------------------------------------------#
# If your paths need configuring, do that here. Defaults are read from a file  #
# called '.path_of.toml' in your home directory if it exists.                  #
#------------------------------------------------------------------------------#
# ops.config.path_of.opensees = <your opensees path>
# ops.config.path_of.scratch = <your scratch dir>

#--[ Define material ]---------------------------------------------------------#
Fy = 50
E = 29000
b = 0.01

steel = ops.material.Steel02(1, Fy, E, b, R0=5, sigma_i=0.3*Fy)

#--[ Define loading ]-----------------------------------------------------------
yield_strain = Fy/E
# strain_peaks = np.array([0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 0])*yield_strain
# strain_peaks = np.array([0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 0])*2*yield_strain
strain_peaks = np.array([0, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 0])*2*yield_strain
strain_rate = yield_strain/100

#--[ Run analysis ]-------------------------------------------------------------
analysis = ops.analysis.UniaxialMaterialAnalysis(steel)

results_pos_env = analysis.run_analysis([0, strain_peaks.max()], 'StrainRate', strain_rate)
results_neg_env = analysis.run_analysis([0, strain_peaks.min()], 'StrainRate', strain_rate)
results_cyclic = analysis.run_analysis(strain_peaks, 'StrainRate', strain_rate)

#--[ Plot results ]-------------------------------------------------------------
plt.rcParams['lines.linewidth'] = 1.0

fig, ax = plt.subplots()
ax.plot(results_pos_env.disp, results_pos_env.force, color='k', linestyle='dashed')
ax.plot(results_neg_env.disp, results_neg_env.force, color='k', linestyle='dashed')
ax.plot(results_cyclic.disp, results_cyclic.force)

ax.minorticks_on()
ax.grid()
ax.set_xlabel('Strain (in/in)')
ax.set_ylabel('Stress (ksi)')
fig.tight_layout()

plt.show()
