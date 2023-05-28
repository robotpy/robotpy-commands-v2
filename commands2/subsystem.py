from .command import Command

class Subsystem:

    def __new__(cls) -> 'Subsystem':
        instance = super().__new__(cls)
        # add to the scheduler
        CommandScheduler.getInstance().registerSubsystem(instance)
        return instance

    def __init__(self) -> None:
        pass

    def periodic(self) -> None:
        pass

    def simulationPeriodic(self) -> None:
        pass

    def getDefaultCommand(self) -> Command | None:
        return CommandScheduler.getInstance().getDefaultCommand(self)
    
    def setDefaultCommand(self, command: Command) -> None:
        CommandScheduler.getInstance().setDefaultCommand(self, command)

    def getCurrentCommand(self) -> Command | None:
        return CommandScheduler.getInstance().getCurrentCommand(self)
    
