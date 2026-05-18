# Crochet Shape Visualizer

Desktop application for building a simplified 3D model from crochet rows.
The user enters stitch width, row height, and the number of stitches in each
row. The application then shows the calculated shape in a 3D preview.

## Requirements

- Python 3.10 or newer

## Installation

1. Download or clone this repository.

2. Open a terminal in the project folder.

3. Create a virtual environment:

```bash
python -m venv .venv
```

4. Activate the virtual environment.

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Windows Command Prompt:

```cmd
.\.venv\Scripts\activate.bat
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

5. Install the required packages:

```bash
pip install numpy PySide6 pyvista pyvistaqt
```

## How to Run

Run the application from the project folder:

```bash
python main.py
```
