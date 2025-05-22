# Intelligent Parking System with Face & License Plate Recognition

This project implements a smart parking system that automates vehicle entry and exit using AI. It utilizes YOLO for license plate detection and a face recognition library to verify driver identity, ensuring secure and efficient parking management.

## 🔍 Features
- **License Plate Detection** using YOLO algorithm
- **Character Recognition** for license plate text
- **Face Recognition** for driver identity verification
- **Barrier Gate Control** that opens only when face and plate match
- **High Accuracy**:
  - License Plate Detection: 91.86% (IOU: 74.15%)
  - Character Recognition: 95.8% (IOU: 81.25%)

## 🛠 Technology Stack

### ✅ Libraries & Frameworks
- **Python** 3.6.9  
- **PyMata** 2.20 (for Arduino communication)  
- **NumPy** 1.19.4  
- **Matplotlib** 2.1.1  
- **OpenCV (GPU)** 4.5.5  
- **face_recognition** 1.2.3  
- **Tkinter** 8.6 (GUI)  
- **Pillow (PIL)** 8.4.0  
- **MySQL** 8.0  

## ⏱ Performance
- **Computation Time**:
  - Google Colab: 4.85 seconds
  - Jetson Nano: 37.69 seconds

## 📂 Project Structure
