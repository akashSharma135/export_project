from splitwise import Splitwise
from splitwise.balance import Balance
from splitwise.group import Group
from splitwise.debt import Debt
import splitwise_export as spwe

sObj = spwe.authorize_by_api()

expenses = spwe.get_group_expenses(sObj)

spwe.expenses_to_csv(expenses)