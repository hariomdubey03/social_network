def result_list_to_dict(result):
    return [row._asdict() for row in result]


def result_row_to_dict(result_row):
    return result_row._asdict()
