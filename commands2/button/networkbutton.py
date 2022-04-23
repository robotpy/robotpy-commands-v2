from networktables import NetworkTable, NetworkTables, NetworkTableEntry

from typing import Union, overload

from .button import Button


class NetworkButton(Button):
    @overload
    def __init__(self, entry: NetworkTableEntry) -> None:
        ...

    @overload
    def __init__(self, table: Union[NetworkTable, str], field: str) -> None:
        ...

    def __init__(self, *args, **kwargs) -> None:
        num_args = len(args) + len(kwargs)
        if num_args == 1:
            entry: NetworkTableEntry = kwargs.get("entry", args[0])
            super().__init__(
                lambda: NetworkTables.isConnected and entry.getBoolean(False)
            )
        elif num_args == 2:
            table = kwargs.get("table", args[0])
            field = kwargs.get("field", args[-1])

            if isinstance(table, str):
                table = NetworkTables.getTable(table)

            entry = table.getEntry(field)
            self.__init__(entry)
        else:
            raise TypeError(
                f"__init__() takes 1 or 2 positional arguments but {num_args} were given"
            )
