def find_longest_sequence(input_string):
    if not input_string:
        return None, 0

    current_char = input_string[0]
    current_length = 1
    max_char = current_char
    max_length = current_length

    for i in range(1, len(input_string)):
        if input_string[i] == current_char:
            current_length += 1
        else:
            current_char = input_string[i]
            current_length = 1

        if current_length > max_length:
            max_length = current_length
            max_char = current_char

    xml_output = f"""<data>
    <row>{input_string}</row>
    <longest_sequence length="{max_length}">{max_char}</longest_sequence>
</data>"""

    return xml_output


# Example usage
test_string = "аааббббвввввввггг"
result = find_longest_sequence(test_string)
print(result)