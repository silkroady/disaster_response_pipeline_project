import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_file_path, categories_file_path):
    """
    - Reads two CSV files as pandas DataFrame
    - Merges them into a one DataFrame
    Parameters:
    messages_file_path (str): CSV file containing Twitter messages
    categories_file_path (str): CSV file containing categories

    Returns:
    df (DataFrame): merged dataset
    """

    messages = pd.read_csv(messages_file_path)
    categories = pd.read_csv(categories_file_path)

    df = messages.merge(categories, on='id')

    return df


def clean_data(df):

    """
    Cleans the merged dataset

    Parameters:
    df (DataFrame): Merged dataset returned from load_data() function

    Returns:
    df (DataFrame): Cleaned data
    """

    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(";",\
                                            expand = True)

    # select the first row of the categories dataframe
    row = categories.iloc[0]

    # use this row to extract a list of new column names for categories.
    category_colnames = row.apply(lambda x: x.split('-')[0]).tolist()

    # rename the columns of `categories`
    categories.columns = category_colnames

    # Convert category values to just numbers 0 or 1.

    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].apply(lambda x:x.split('-')[1])
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)

    # the "related category happens to have three values instead of two, so converting 2's to 1's
    categories['related']=categories['related'].map(lambda x: 1 if x == 2 else x)


    # drop the original categories column from `df`
    df.drop('categories', axis=1, inplace=True)

    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df,categories], axis=1)

    # drop duplicates
    df.drop_duplicates(inplace = True)

    return df


def save_data(df, database_filename):
    """
    Creates a SQLite database and saves the cleaned data as table in the database

    Parameters:
    df (DataFrame): Cleaned data returned from clean_data() function
    database_file_name (str): Database file name

    Returns:
    None
    """
    engine = create_engine('sqlite:///' + database_filename)
    df.to_sql('messages_disaster', engine, index=False, if_exists = 'replace')


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)

        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)

        print('Cleaned data saved to database!')

    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
