import re

def retract_label(my_string_with_labels):
    pattern = r"<label[^>]*>(.*?)</label>"
    matches = re.findall(pattern, my_string_with_labels)
    if matches:
        return matches[0]
    else:
        print("llm output no reason")

    return None

def retract_reason(my_string_with_labels):
    pattern = r"<reason[^>]*>(.*?)</reason>"

    matches = re.findall(pattern, my_string_with_labels, re.IGNORECASE | re.DOTALL)
    if matches:
        return matches[0]
    else:
        print("llm output no reason")

    return None


def test_retract_reason():
    text = "<label>这是标签里的内容</label>"

    matches = retract_label(text)

    print(matches)

if __name__ == '__main__':
    test_retract_reason()