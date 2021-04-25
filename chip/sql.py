# SQL Models
from typing import List

from aiosqlite import Connection


class DBModel:
    """
    ABC To allow for unified use of database models.
    """

    _state: Connection
    __rows__: list
    _data: dict

    @classmethod
    async def create_table(cls, connection: Connection, *rows, name=None) -> None:
        """Creates the table.

        :param connection: The aiosqlite connection object.
        :param rows: A list of rows to create (name type constraints)
        :param name: Optional[str] - The name of the table. Defaults to cls.__class__.__name__."""
        if not rows:
            rows = cls.__rows__
        query = "CREATE TABLE IF NOT EXISTS {} ({});".format(name or cls.__class__.__name__.lower(), ",\n".join(rows))
        # The IF NOT EXISTS in there means this function can be called numerous times.
        await connection.execute(query)
        await connection.commit()

    @classmethod
    async def create(cls, state, **values):
        """
        [C]RUD - Creates an entry in the database.

        :param values: column:value pairs to use.
        :param state: The state to use
        :return: Resolved model
        """
        raise NotImplementedError

    @classmethod
    async def get(cls, state, key, **other_comps):
        """
        C[R]UD - Retrieve an entry from the database.

        :param state: The state to use
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

    def __getattr__(self, item):
        if not isinstance(item, str):
            raise TypeError("Got type '{.__class__.__name__}' instead of 'str'.".format(item))
        try:
            return self._data[item]
        except KeyError:
            raise AttributeError(self.__class__.__name__ + " has no attribute '{}'.".format(item))

    __getitem__ = __getattr__  # We'll just alias getitem to getattr (so we can do stuff like model["key"] or model.key)

    def __setattr__(self, key, value):
        # We can only edit self, setting attributes will just do it to the local object.
        # This is bad because we use an async lib, so can't do the update here ourselves.
        # And we also don't want to end up with a race condition where we have tasks competing to see who can
        # edit the database the fastest. Asyncio tasks really do just show off in that regard.
        raise AttributeError(f"Please use {self.__class__.__name__}.edit() over setting attributes.")

    @property
    def state(self) -> Connection:
        """
        The connection state

        :return: aiosqlite.Connection - the current database connection
        """
        return self._state

    @property
    def data(self) -> dict:
        """
        The raw dictionary of data for this table.

        :return: dict - key: value pairs
        """
        return self._data.copy()


class Guild(DBModel):
    """
    A database model representing a guild.
    """

    __rows__ = [
        "id INTEGER PRIMARY KEY NOT NULL UNIQUE",
        "prefix TEXT NULLABLE DEFAULT NULL",
        "mod_log INTEGER UNIQUE",
        "mod_role INTEGER UNIQUE",
        "case_id INTEGER",
    ]

    def __init__(self, data: dict, *, state):
        self._state = state
        self._data = data

    @classmethod
    async def create(cls, state: Connection, **kwargs):
        query = """
        INSERT INTO guilds VALUES (?, ?, ?, ?, ?);
        """
        await state.execute(query, *kwargs.values())
        await state.commit()
        return cls(kwargs, state=state)

    @classmethod
    async def get(cls, state, key, **other_comps):
        query = """
        SELECT * FROM guilds WHERE {} LIMIT 1;
        """
        if other_comps:
            where = " AND ".join(f"{column}={value}" for column, value in other_comps.items())
        else:
            where = "id=" + key
        query = query.format(where)
        data = {}
        async with state.execute(query) as cursor:
            row = await cursor.fetchone()
            for key in row.keys():
                data[key] = row[key]
        return cls(data, state=state)

    async def edit(self, keys: List[str], values):
        if not hasattr(self, "id"):
            raise ValueError("Missing ID for guild data model - unable to update")
        query = """
        UPDATE guilds
        SET {}
        WHERE id=?"""

        _set = []
        for n, key in enumerate(keys):
            _set.append(f"{key}={values[n]}")
        query = query.format(", ")
        await self.state.execute(query, (self.id,))
        await self.state.commit()

    async def delete(self) -> None:
        if not hasattr(self, "id"):
            raise ValueError("Missing ID for guild data model - unable to delete.")
        await self.state.execute(
            """
            DELETE FROM guilds
            WHERE id=?
            """,
            (self.id,),
        )
        await self.state.commit()
        return
