from data_loader import load_products

path=r"C:\Users\Siddhesh\Desktop\GroupXY\data\meta_Appliances.json"

product=load_products(path)

i=0
for key in product:
    print(product[key])
    i+=1
    if i>=2:
        break