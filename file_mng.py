import os
import pickle

def make_pkl(var, name):
    with open(f"{name}.pkl", "wb") as f:
        pickle.dump(var, f)

def organize_files():
    files = os.listdir("img")
    for i, file in enumerate(sorted(files, reverse = True)):
        if i >= 10: os.remove(f"img/{file}")