
import csv, sqlite3

con = sqlite3.connect("db.sqlite3") # change to 'sqlite:///your_filename.db'
cur = con.cursor()
#cur.execute("CREATE TABLE categorias (ID, Categoria);") # use your column names here
#cur.execute("CREATE TABLE subCategorias1 (ID,Cat_ID,Subcategoria1);")
#cur.execute("CREATE TABLE subCategorias2 (ID,SubCat1_ID,Subcategoria2);")

with open('categorias_clean.csv','r') as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['ID'], i['Categoria']) for i in dr]

with open('subcategorias1_clean.csv','r') as fin2: 
    dr = csv.DictReader(fin2)
    to_db2 = [(i['ID'], i['Cat_ID'], i['Subcategoria1']) for i in dr]
    
with open('subcategorias2_clean.csv','r') as fin3: 
    dr = csv.DictReader(fin3) 
    to_db3 = [(i['ID'], i['SubCat1_ID'], i['Subcatagoria2']) for i in dr]

cur.executemany("INSERT INTO sellers_categories (ID, Categoria) VALUES (?, ?);", to_db)
cur.executemany("INSERT INTO sellers_subcategory1 (ID,Cat_id,Subcategoria1) VALUES (?, ?, ?);", to_db2)
cur.executemany("INSERT INTO sellers_subcategory2 (ID,SubCat1_id,Subcategoria2) VALUES (?, ?, ?);", to_db3)
con.commit()
con.close()