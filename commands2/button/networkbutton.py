from networktables import NetworkTable, NetworkTables, NetworkTableEntry

from typing import Union, overload

from .button import Button


class NetworkButton(Button):
    """
    A class used to bind command scheduling to a NetworkTable boolean fields.
    Can be composed with other buttons with the operators in Trigger.

    @see Trigger
    """

    @overload
    def __init__(self, entry: NetworkTableEntry) -> None:
        """
        Creates a NetworkButton that commands can be bound to.

        :param entry: The entry that is the value.
        """

    @overload
    def __init__(self, table: Union[NetworkTable, str], field: str) -> None:
        """
        Creates a NetworkButton that commands can be bound to.

        :param table: The table where the networktable value is located.
        :param field: The field that is the value.
        """

    def __init__(self, *args, **kwargs) -> None:
        num_args = len(args) + len(kwargs)
        if num_args == 1:
            entry: NetworkTableEntry = kwargs.get("entry") or args[0]

            if not isinstance(entry, NetworkTableEntry):
                raise self._type_error(entry)
            
            super().__init__(
                lambda: NetworkTables.isConnected() and entry.getBoolean(False)
            )
        elif num_args == 2:
            table = kwargs.get("table") or args[0]
            field = kwargs.get("field") or args[-1]

            if isinstance(table, str):
                table = NetworkTables.getTable(table)

            entry = table.getEntry(field)
            self.__init__(entry)
        else:
            raise self._type_error(args)

    def _type_error(self, *args):
        return TypeError(
            "NetworkButton.__init__(): incompatible constructor arguments. The following argument types are supported:\n"
            "\t1. commands2.button.NetworkButton(entry: NetworkTableEntry)\n"
            "\t2. commands2.button.NetworkButton(table: str, field: str)\n"
            "\t3. commands2.button.NetworkButton(table: NetworkTable, field: str)\n"
            f"Invoked with: {', '.join(map(str, args))}"
        )
