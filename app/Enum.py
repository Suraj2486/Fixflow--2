
import enum


class UserRole(str, enum.Enum):
    USER = "User"
    TECHNICIAN = "Technician"
    MANAGER = "Manager"
    ADMIN = "ADMIN"

class TicketPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class TicketStatus(str, enum.Enum):
    REPORTED = "Reported"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    WAITING_FOR_USER = "Waiting for User"
    RESOLVED = "Resolved"
    CLOSED = "Closed"



class HistoryType(str, enum.Enum):
    ASSIGNED_TECHNICIAN = "Assigned Technician"
    STATUS = "Status"
    PRIORITY = "Priority"
    EDIT = "Edit"

class MsgType(str, enum.Enum):
    ASSIGNEMNT = 'Asignment'
    STATUS_CHANGE = 'Status changes'
    TECHNICIAN_UPDATES = 'Technician updates'
    RESOLUTION = 'Resolution'
    CLOSURE = 'Closure'