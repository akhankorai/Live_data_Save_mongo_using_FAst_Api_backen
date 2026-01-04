from db import predictions_col

print("Documents count:", predictions_col.count_documents({}))
print("One document:", predictions_col.find_one())
