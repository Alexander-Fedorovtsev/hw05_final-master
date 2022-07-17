def make_divider_of(divider):
    def division_operation(divisible):
        answer = divisible / divider
        return answer

    return division_operation


# Создали функцию
div2 = make_divider_of(2)
print(div2(10))  # Такой вызов должен вернуть 10/2, то есть 5.0

div5 = make_divider_of(5)
print(div5(20))  # Такой вызов должен вернуть 4.0

print(div5(div2(20)))  # Такой вызов должен вернуть 2.0
