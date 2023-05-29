
from .trigger import Trigger
from typing import overload

from ntcore import NetworkTable
from ntcore import NetworkTableInstance
from ntcore import BooleanSubscriber
from ntcore import BooleanTopic

class NetworkButton(Trigger):

    @overload
    def __init__(self, topic: BooleanTopic) -> None:
        pass

    @overload
    def __init__(self, sub: BooleanSubscriber) -> None:
        pass

    @overload
    def __init__(self, table: NetworkTable, field: str) -> None:
        pass

    @overload
    def __init__(self, table: str, field: str) -> None:
        pass

    @overload
    def __init__(self, inst: NetworkTableInstance, table: str, field: str) -> None:
        pass

    def __init__(self, *args, **kwargs) -> None:
        num_args = len(args) + len(kwargs)
        if num_args == 1:
            arg, *_ = args + tuple(kwargs.values())
            if isinstance(arg, BooleanTopic):
                self.__init__(arg.subscribe(False))
            elif isinstance(arg, BooleanSubscriber):
                super().__init__(lambda: arg.getTopic().getInstance().isConnected() and arg.get())
            else:
                raise ValueError("Invalid argument")
        elif num_args == 2:
            table, field, *_ = args + tuple(kwargs.values())
            if isinstance(table, NetworkTable):
                self.__init__(table.getBooleanTopic(field))
            elif isinstance(table, str):
                self.__init__(NetworkTableInstance.getDefault(), table, field)
            else:
                raise ValueError("Invalid argument")
        elif num_args == 3:
            inst, table, field, *_ = args + (None, None, None)
            if "inst" in kwargs:
                inst = kwargs["inst"]
            if "table" in kwargs:
                table = kwargs["table"]
            if "field" in kwargs:
                field = kwargs["field"]
            
            if inst is None:
                raise ValueError("NetworkTableInstance is required")
            if table is None:
                raise ValueError("NetworkTable name is required")
            if field is None:
                raise ValueError("Field name is required")
            
            self.__init__(inst.getTable(table), field)
        else:
            raise ValueError("Invalid number of arguments")