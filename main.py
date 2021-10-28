import splitwise_export as spwe

sObj = spwe.authorize_by_api()

expenses = spwe.get_group_expenses(sObj)

spwe.expenses_to_pdf(expenses)