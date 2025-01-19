import os

def create_folder(folder_path):
    """
    Creates a folder at the specified path if it doesn't already exist.

    Parameters:
    - folder_path (str): The path of the folder to create.
    """
    try:
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        print(f"Error creating folder: {e}")
