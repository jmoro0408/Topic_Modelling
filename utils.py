"""
Small module that holds useful functions.
"""

from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd
import toml
from gensim import models
from gensim.test.utils import datapath
from sqlalchemy import create_engine


def read_transcripts(config_dict: dict, row_limit: Optional[int] = None) -> list[str]:
    """Reads in the podcast transcripts from postgresql db to a list.

    Args:
        config_dict (dict): Config dict with DB parameters.
        row_limit (Optionsal(int)): Number of rows to receive. If None, all
        rows are returned. Defaults to None.

    Returns:
        list[str]: List of transcripts.
    """
    _query = """SELECT * from episodes"""
    if row_limit is not None:
        _query = """SELECT * from episodes LIMIT {}""".format(row_limit)
    df = read_from_db(_query, config_dict=config_dict)
    return df["transcript"].to_list()


def read_titles(config_dict: dict, row_limit: Optional[int] = None) -> list[str]:
    """Reads in the podcast titles from postgresql db to a list.

    Args:
        config_dict (dict): Config dict with DB parameters.
        row_limit (Optionsal(int)): Number of rows to receive. If None, all
        rows are returned. Defaults to None.

    Returns:
        list[str]: List of episode titles.
    """
    _query = """SELECT * from episodes"""
    if row_limit is not None:
        _query = """SELECT * from episodes LIMIT {}""".format(row_limit)
    df = read_from_db(_query, config_dict=config_dict)
    return df["title"].to_list()


def read_toml(toml_file: Union[str, Path]) -> dict:
    """reads info from a toml file

    Args:
        config_file (Union[str,Path]): filepath of toml file

    Returns:
        dict: dictionary containing toml data
    """
    return toml.load(toml_file)


def read_from_db(query: str, config_dict: dict) -> pd.DataFrame:
    """Reads a SQL query into a pandas dataframe.

    Args:
        query (str): Query to pass to db
        config_dict (dict): config dict outlining the db parameters.
        Should include host, database, user, and password.

    Returns:
        pd.DataFrame: _description_
    """
    host = config_dict["host"]
    database = config_dict["database"]
    user = config_dict["user"]
    password = config_dict["password"]
    engine = create_engine(f"postgresql://{user}:{password}@{host}:5432/{database}")
    return pd.read_sql_query(query, engine)


def list_from_text(filepath: Union[Path, str]) -> list[str]:
    """Reads a .txt file into a list.

    Args:
        filepath (Union[Path, str]): .txt filepath.

    Returns:
        list[str]: list of words in .txt file.
    """
    loaded_text = np.loadtxt(filepath, dtype="str", delimiter=",").tolist()
    return [x.strip() for x in loaded_text]


def append_to_txt_file(
    to_append: Union[str, list], txt_filename: Union[Path, str], erase: bool = False
) -> None:
    """Appends a string to an existing .txt file, if the text does not already exist.

    Args:
        to_append (Union[str,list]): string or list of strings to be appended.
        txt_filename (Union[Path,str]): File to append to. Should include .txt extension.
        erase (bool): If true, erases the file before appending. Defaults to False.
    Returns:
        _type_: None.
    """
    with open(txt_filename, "r+", encoding="utf-8") as f:
        if erase:
            f.seek(0)
            f.truncate(0)
        current_text = [i for line in f for i in line.split(",")]
        current_text = [i.strip() for i in current_text]
        if isinstance(to_append, str):
            to_append = to_append.split(",")
        to_append = ",".join([i for i in to_append if i not in current_text])
        if len(to_append) == 0:
            print("No new text appended.")
            return None
        f.write(to_append)
    return None


def load_lda_model(filepath: str) -> models.ldamodel.LdaModel:
    """Loads a saved LDA model.
    Filepath should be full, not relative.

    Args:
        filepath (str): Full filepath of saved model.

    Returns:
        models.ldamodel.LdaModel: Saved LDA model
    """
    fname = datapath(filepath)
    return models.ldamodel.LdaModel.load(fname)


def remove_if_substring(doc: list[str], substring: Union[list, str]) -> list[str]:
    """Removes word from a list if the substring appears in the list.
    i.e: with substring = "tring"
    ["this", "is", "a", "test", "string"]
    becomes -> ["this", "is", "a", "test"]
    Args:
        doc (list[str]): list of strings
        substring (str): substring to check for

    Returns:
        doc[str]: filtered list
    """
    if isinstance(substring, str):
        substring = list(substring)
    for word in doc:
        for subword in substring:
            if subword in word:
                doc.remove(word)
    return doc
