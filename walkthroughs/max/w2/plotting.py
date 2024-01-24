import matplotlib.pyplot as plt

# Given array of values
values = [0.1, 0.2, -0.4, 0.3]

# To run the GUI event loop
plt.ion()

# Creating a bar plot
figure, ax = plt.subplots(figsize=(6, 4))
bars = ax.bar(range(len(values)), values, color=['green' if v >= 0 else 'red' for v in values])

# Setting title
ax.set_title("Bar Plot", fontsize=15)

# Setting x-axis label and y-axis label
ax.set_xlabel("Index")
ax.set_ylabel("Values")

# Display the updated plot interactively
plt.show()

# Pause for a short duration
plt.pause(1)

# Keep the plot window open
plt.show(block=True)