# GQL python
A simple interface for graphql in python using machine authentication.

## Setup

1. Make sure you have Poetry installed. If not, install it using the official installer, visit [https://python-poetry.org/docs/#installing-with-the-official-installer](https://python-poetry.org/docs/#installing-with-the-official-installer).

2. Create a Poetry shell:
   ```
   poetry shell
   ```

3. Install the project dependencies:
   ```
   poetry install
   ```

Side note: If you would rather not use Poetry, you can use pip to install the required dependencies.

## Usage

To use the library, you need to set up your environment with your client ID and client secret. You can find these values in the PlayerData API settings.

1. Add in your client ID and client secret into the python file you want to run. 

2. Run the python file.
```
python your_script.py
```
3. The CSV will appear in the same directory as the python file. 