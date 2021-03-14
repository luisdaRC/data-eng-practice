# This will help us to execute this as a script
import argparse
# Printing logs in terminal
import logging
logging.basicConfig(level=logging.INFO)
# Panditas :3
import pandas as pd

from article import Article
from base import Base, Engine, Session

logger = logging.getLogger(__name__)


def main(filename):
    # Generating schema in DB
    Base.metadata.create_all(Engine)
    session = Session()
    articles = pd.read_csv(filename)
    # Iterating the DataFrame
    for index, row in articles.iterrows():
        logger.info('Loading article uid {} into DB'.format(row['uid']))
        article = Article(row['uid'],
                          row['body'],
                          row['host'],
                          row['newspaper_uid'],
                          row['tokens_body'],
                          row['tokens_title'],
                          row['title'],
                          row['url'])
        # Inserting the article into the DB
        session.add(article)
    #Po'que ajá
    session.commit()
    session.close()


if __name__ == '__main__':
    # Configurations to run the script
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='The file you want to load into the db',
                        type=str)

    args = parser.parse_args()

    main(args.filename)
