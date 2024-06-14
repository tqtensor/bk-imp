import matplotlib.pyplot as plt
import numpy as np

# Data
libraries = [
    "Matplotlib",
    "Numpy",
    "Scipy",
    "Sklearn",
    "TensorFlow",
    "PyTorch",
    "Pandas",
]
llama_3_cot = [4.08, 49.69, 46.48, 53.95, 44.44, 51.11, 33.51]
llama_3_zeroshot = [19.78, 20.43, 37.88, 36.99, 37.5, 46.67, 20.43]

# Number of libraries
n = len(libraries)

# Bar width
bar_width = 0.35

# X locations for the groups
index = np.arange(n)

# Create plot
fig, ax = plt.subplots(figsize=(10, 6))

# Bar plots
bar1 = ax.bar(index, llama_3_cot, bar_width, label="Llama 3 CoT")
bar2 = ax.bar(
    index + bar_width, llama_3_zeroshot, bar_width, label="Llama 3 Zeroshot"
)

# Labels and title
ax.set_xlabel("Libraries")
ax.set_ylabel("Accuracy (%)")

ax.set_xticks(index + bar_width / 2)
ax.set_xticklabels(libraries)
ax.legend()

# Save the plot with 300 dpi
plt.savefig("thesis/slides/img/code_llm.png", dpi=300)

# Show the plot
plt.show()
