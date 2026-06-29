import os

PATH_FILE_CODE = os.path.abspath(__file__)


PATH_FOLDER_CODE = os.path.dirname(PATH_FILE_CODE)


PATH_FOLDER_PROJECT = os.path.dirname(PATH_FOLDER_CODE)


PATH_FOLDER_LATEX = os.path.join(PATH_FOLDER_PROJECT, "latex")
