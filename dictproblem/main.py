list_a = [1, 2, 3, 4, 5]
list_b = ["a", "b", "c", "d", "e"]
my_dict = {}

# 두개의 리스트를 하나의 딕셔너리로 만들기
for i in range(5):
    my_dict[list_a[i]] = list_b[i]

print(my_dict)


# 두개의 리스트를 각각의 딕셔너리로 만들고 그 딕셔너리들을 리스트로 묶기..?


key_value_pairs = [{key, value} for key, value in my_dict.items()]
print(key_value_pairs)
