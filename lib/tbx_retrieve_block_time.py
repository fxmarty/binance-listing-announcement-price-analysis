import datetime


def retrieve_block_from_date(timestamp, w3, limit_down=None, limit_up=None):
    """
    This function returns the closest ** next ** block number from a date given
    in the timestamp format.
    """

    cur_min = 0
    cur_max = w3.eth.get_block_number()  # get most recent block number

    # possible speedup
    if limit_down:
        cur_min = limit_down
    if limit_up:
        cur_max = limit_up

    if w3.eth.get_block(cur_min).timestamp > timestamp:
        raise ValueError("The requested time is too old.")

    if w3.eth.get_block(cur_max).timestamp < timestamp:
        raise ValueError("The requested time is in the future...")

    current_closest_block_number = cur_max

    n_it = 0
    while True:
        n_it += 1
        # print(n_it, "---", cur_min, "--", cur_max)
        previous_block_num = cur_max
        next_block_num = cur_min + (cur_max - cur_min) // 2

        if cur_max - cur_min <= 1:
            break

        previous_block_num = next_block_num

        if w3.eth.get_block(next_block_num).timestamp > timestamp:
            cur_max = next_block_num
        else:
            cur_min = next_block_num

    return cur_max  # return the upper one
