import logging
logging .basicConfig(level=logging.INFO)
# subprocess let us manipulate terminal files. As if we had the terminal
# in python
import subprocess


logger = logging.getLogger(__name__)
# If we have more sites, just add them to the array
news_sites_uid = ["eluniversal"]


def main():
    _extract()
    _Transform()
    _Load()


def _extract():
    logger.info("Starting Extract process")
    subprocess.run(["python", "main.py", news_sites_uid[0]], cwd="./Extract")
    subprocess.run(["find", ".", "-name", "{}*".format(news_sites_uid[0]), "-exec", "mv",
                    "{}", "../Transform/{}_.csv".format(news_sites_uid[0]), ";"], cwd="./Extract")

#This part of code is having a weird behavior, in last it serves, but with bugs
def _Transform():
    logger.info("Starting Transform process")
    dirty_data_filename = "{}_.csv".format(news_sites_uid[0])
    clean_data_filename = "clean_{}".format(dirty_data_filename)
    subprocess.run(["python", "newspaper_recipe.py", dirty_data_filename],
                   cwd="./Transform")
    subprocess.run(["rm", dirty_data_filename], cwd="./Transform")
    subprocess.run(["mv", clean_data_filename,
                    "../Load/{}.csv".format(news_sites_uid[0])], cwd="./Transform")


def _Load():
    logger.info("Starting Load process")
    clean_data_filename = "{}.csv".format(news_sites_uid[0])
    subprocess.run(["python", "main.py", clean_data_filename], cwd="./Load")
    subprocess.run(["rm", clean_data_filename], cwd="./Load")

if __name__ == "__main__":
    main()
