import os
import glob
from bs4 import BeautifulSoup
from cfg.config import project_path


if __name__ == "__main__":

    filelist = glob.glob(os.path.join(project_path, "dat", "pages/*.html"))

    res = []
    for file_path in sorted(filelist):
        with open(file_path, "r") as f:

            contents = f.read()
            soup = BeautifulSoup(contents, "html")
            elements = soup.find_all("a", {"class": "css-1ej4hfo"})

            for element in elements:
                annoncement_hash = os.path.basename(element.get("href"))
                print(annoncement_hash)
                res.append(annoncement_hash)

    # Check we have no duplicates
    assert len(res) == len(set(res))

    with open(os.path.join(project_path, "dat", "page_hashes.txt"), "w") as f:
        for hash in res:
            f.write(hash)
            f.write("\n")