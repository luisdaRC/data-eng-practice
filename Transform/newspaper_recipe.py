import argparse
import logging
import hashlib
import pandas as pd
import nltk
from nltk.corpus import stopwords
from urllib.parse import urlparse
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


def main(filename):  # In this function is described the process of the script
    logger.info('Starting cleaning process')

    df = _read_data(filename)  # First of all, this read the data
    newspaper_uid = _extract_newspaper_uid(
        filename)  # It's extracted the newspaper uid
    # It's created the new column in the DataFrame
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)  # It's extracted the hst name from its url
    # El format de sublime fué el que desordenó los comentarios.
    # It will fill up all the missing titles using its own url
    df = _fill_missing_titles(df)
    df = _generate_uids_for_rows(df)
    df = _remove_newlines_from_body(df)
    # It will generate ints in new columns of significative words
    # contained in title and body
    df["tokens_title"] = _tokenizer_columns(df, "title")
    df["tokens_body"] = _tokenizer_columns(df, "body")

    df = _remove_duplicated_entries(df, "title")
    df = _drop_rows_with_missing_values(df)
    _save_data(df, filename)

    return df


def _read_data(filename):
    logger.info('Reading file {}'.format(filename))

    return pd.read_csv(filename)


def _extract_newspaper_uid(filename):
    logger.info('Extracting newspaper uid')
    newspaper_uid = filename.split('_')[0]

    logger.info('Newspaper uid detected: {}'.format(newspaper_uid))
    return newspaper_uid


def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info('Filling newspaper_uid column with {}'.format(newspaper_uid))
    df['newspaper_uid'] = newspaper_uid

    return df


def _extract_host(df):
    logger.info('Extracting host from urls')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)

    return df


def _fill_missing_titles(df):
    logger.info('Filling missing titles')
    missing_titles_mask = df['title'].isna()
    missing_titles = (df[missing_titles_mask]['url']
                      .str.extract(r'(?P<missing_titles>[^/]+)$').astype("str")
                      .applymap(lambda title: title.replace('-', ' '))
                      )

    df.loc[missing_titles_mask, 'title'] = missing_titles.loc[
        :, 'missing_titles']

    return df


def _generate_uids_for_rows(df):
    logger.info('Generating uids for each row')
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest())
            )
    df['uid'] = uids

    return df.set_index("uid")


def _remove_newlines_from_body(df):
    logger.info('Removing new lines (/n) from title')
    stripped_body = (df
                     .astype("str")
                     .apply(lambda row: row['body'], axis=1)
                     .apply(lambda body: list(body))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\n', ''), letters)))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\r', ''), letters)))
                     .apply(lambda letters: ''.join(letters))
                     )
    df["body"] = stripped_body

    return df


def _tokenizer_columns(df, column_name):
    stop_words = set(stopwords.words("spanish"))
    return (df.dropna()
            .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
            .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
            .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
            .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
            .apply(lambda valid_word_list: len(valid_word_list))
            )


def _remove_duplicated_entries(df, column):
    logger.info('Removing duplicated entries')
    df.drop_duplicates(subset=[column], keep="first", inplace=True)

    return df


def _drop_rows_with_missing_values(df):
    logger.info('Dropping rows with missing values')
    return df.dropna()


def _save_data(df, filename):
    clean_filename = "clean_{}".format(filename)
    logger.info('Saving data at location {}'.format(filename))
    df.to_csv(clean_filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='The path to the dirty data',
                        type=str)

    args = parser.parse_args()

    df = main(args.filename)
    print(df)
