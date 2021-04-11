import pandas as pd

vne_1 = pd.read_csv('tuoitre_result_temp.csv')
print(len(vne_1))
vne_2 = pd.read_csv('tuoitreonline.csv')
print(len(vne_2))
vne = vne_2.append(vne_1)
print(len(vne))
vne_drop_duplicate = vne.drop_duplicates(keep='first')
print(len(vne_drop_duplicate))

vne_drop_duplicate.to_csv('tuoitreonline.csv', index=False, encoding='utf-8')