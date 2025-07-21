# LogistiQ: Smart Parcel Delivery Simulator

**LogistiQ** is a Python-based simulation tool designed to model and visualize modern parcel delivery logistics for educational, research, and optimization projects. Built for efficiency, accuracy, and real-time insight, the simulator features a custom hash table, multi-truck routing, real-world delivery scenarios, and an interactive CLI. This program mainly leverages the nearest neighbor heuristic to solve a variation of the Traveling Salesman Problem.

---

## Features

- **Efficient Hash Table Package Management**  
  Packages are stored and indexed using a custom-built, chained hash table for fast retrieval.

- **Multi-Truck Operations**  
  Simulates several delivery trucks, each with set departure times, package limits, mileage monitoring, and dynamic routes.

- **Live Status Tracking**  
  Package statuses update in real-time, including conditions for delayed packages and dynamic address corrections.

- **CSV Data Integration**  
  Imports addresses, routing distances, and package manifests from user-provided CSV files, allowing for rapid customization.

- **Interactive Interface**  
  Users can execute simulation runs, retrieve delivery status for specific times or packages, and review mileage/statistics—all from the command line.

- **Time-Based Simulation Logic**  
  Models operations from 8:00:00 to 17:00:00, with user-queryable simulation time points.

- **Advanced Scenario Handling**  
  Simulates common logistics situations, such as address changes or flight-delayed packages.

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/darren-truong/logistiQ.git
   cd logistiQ
   ```

2. **Run the Application**
   ```bash
   python3 main.py
   ```


