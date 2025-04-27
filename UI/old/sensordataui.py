import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from matplotlib.animation import FuncAnimation

# Adjust the port and baud rate as needed
SERIAL_PORT = '/dev/ttyUSB0'   # Update as needed
BAUD_RATE = 115200

# Initialize the serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
print("Connected to", SERIAL_PORT)

# Variables for storing data
iteration = 0  # Start from 1
temperature = []
tds = []
tds_voltage = []
tds_ppm = []

# Tkinter root window
root = tk.Tk()
root.title("Sensor Data Collection")

# Create a canvas for the matplotlib figures
fig, axs = plt.subplots(2, 2, figsize=(10, 8))
axs[0, 0].set_title('Temperature (°C)')
axs[0, 1].set_title('TDS ADC')
axs[1, 0].set_title('TDS Voltage')
axs[1, 1].set_title('TDS PPM')

for ax in axs.flat:
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Value')

# Add the canvas to the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=0, rowspan=5)

# Create the buttons for starting and disengaging
def start_reading():
    global iteration
    iteration = 0
    temperature.clear()
    tds.clear()
    tds_voltage.clear()
    tds_ppm.clear()
    update_data()

def disengage():
    global running
    running = False
    print("Data collection disengaged")

def update_data():
    global iteration, running
    running = True

    # Create the FuncAnimation object and store it in a variable
    ani = FuncAnimation(fig, animate, interval=500)

    # Start the animation
    plt.show()

def animate(i):
    if running:
        line = ser.readline().decode().strip()

        if line.startswith("Temperature_C:"):
            parts = line.split(":")
            temperature.append(float(parts[1]))

            line = ser.readline().decode().strip()
            parts = line.split(":")
            tds.append(float(parts[1]))

            line = ser.readline().decode().strip()
            parts = line.split(":")
            tds_voltage.append(float(parts[1]))

            line = ser.readline().decode().strip()
            parts = line.split(":")
            tds_ppm.append(float(parts[1]))

            print(f"Iteration {iteration}: Temp={temperature[iteration]}, TDS={tds[iteration]}, TDS_Voltage={tds_voltage[iteration]}, TDS_PPM={tds_ppm[iteration]}")

            iteration += 1

            # Update the graphs
            axs[0, 0].cla()
            axs[0, 0].plot(range(iteration), temperature, label="Temperature (°C)", color='blue')
            axs[0, 0].set_title('Temperature (°C)')
            axs[0, 0].set_xlabel('Iteration')
            axs[0, 0].set_ylabel('Temperature (°C)')

            axs[0, 1].cla()
            axs[0, 1].plot(range(iteration), tds, label="TDS ADC", color='green')
            axs[0, 1].set_title('TDS ADC')
            axs[0, 1].set_xlabel('Iteration')
            axs[0, 1].set_ylabel('TDS ADC')

            axs[1, 0].cla()
            axs[1, 0].plot(range(iteration), tds_voltage, label="TDS Voltage", color='red')
            axs[1, 0].set_title('TDS Voltage')
            axs[1, 0].set_xlabel('Iteration')
            axs[1, 0].set_ylabel('TDS Voltage')

            axs[1, 1].cla()
            axs[1, 1].plot(range(iteration), tds_ppm, label="TDS PPM", color='orange')
            axs[1, 1].set_title('TDS PPM')
            axs[1, 1].set_xlabel('Iteration')
            axs[1, 1].set_ylabel('TDS PPM')

            # Redraw the canvas
            canvas.draw()

# Create Start and Disengage buttons
start_button = tk.Button(root, text="Start Reading", command=start_reading)
start_button.grid(row=5, column=0, padx=10, pady=10)

disengage_button = tk.Button(root, text="Disengage", command=disengage)
disengage_button.grid(row=6, column=0, padx=10, pady=10)

# Start the Tkinter mainloop
root.mainloop()
