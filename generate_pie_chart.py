import matplotlib.pyplot as plt
import os

# Dummy data for demonstration purposes
# In a real scenario, 'sizes' and 'labels' would come from actual file system analysis.
sizes = [1024, 2048, 512, 1536, 768] # Example sizes in bytes
labels = ['document.pdf', 'image.jpg', 'script.py', 'data.csv', 'report.docx']

# Create the pie chart
plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
plt.title('File Memory Usage in Current Directory')
plt.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.

# Save the chart
output_filename = 'memory_usage_pie_chart.png'
try:
    plt.savefig(output_filename)
    print(f"Pie chart saved as {output_filename}")
except Exception as e:
    print(f"Error saving pie chart: {e}")
