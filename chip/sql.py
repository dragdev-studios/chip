# SQL Models
from typing import List

from aiosqlite import Connection


class DBModel:
    """
    ABC To allow for unified use of database models.
    """
    state: Connection
    invalid: bool = False

    @classmethod
    async def create(cls, **values):
        """
        [C]RUD - Creates an entry in the database.

        :param values: column:value pairs to use.
        :return: Resolved model
        """
        raise NotImplementedError

    @classmethod
    async def get(cls, key, **other_comps):
        """
        C[R]UD - Retrieve an entry from the database.

        :param key: The primary key to choose from, if **other_comps is not provided.
        :param other_comps: A column:value pair.
        :return: Resolved model
        """
        raise NotImplementedError

    async def edit(self, keys: List[str], values) -> None:
        """
        CR[U]D - Edits the entry on the database.

        .. warning::
            This function commits directly to the database automatically. Make sure your datatypes are correct.

        :param keys: The column names to update
        :param values: the values to update with
        :return: None
        """
        raise NotImplementedError

    async def delete(self) -> None:
        """
        CRU[D] - Deletes this entry.

        .. warning::
            This is irreversible!

        :return: Nothing. You won't be able to use this model again after.
        """
        raise NotImplementedError
