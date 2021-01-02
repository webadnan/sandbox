#! /usr/bin/env python3
import random, ctypes

# Docs: https://docs.google.com/document/d/1hhQJKfDAgwGnS3V7cETgiEgXe0Uof9CxEjBlfs7QlNA
# Spreadsheet: https://docs.google.com/spreadsheets/d/14ksBFQ6lUx7AV0h-UCWf5vxdXYU9xH02JMOxQkMCXiI


class SQLCost:
    def __init__(self, cost_update, cost_select):
        self.cost_update = cost_update
        self.cost_select = cost_select

    def assert_update(self, n_days_ago, result, text):
        assert self.cost_update(n_days_ago) == result, \
            "%s, cost of updating for %d should be %d" % (text, n_days_ago, self.cost_update(n_days_ago))

    def assert_select(self, range_days_count, result, text):
        assert self.cost_select(range_days_count) == result, \
            "%s, cost of selecting for %d should be %d" % (text, range_days_count, self.cost_select(range_days_count))


def set_random_day(day=-1):
    global random_day
    if day == -1:
        random_day = random.randint(1, 30)
    else:
        random_day = day


def get_today():
    return random_day


def option2_calc_update(n_days_ago):
    # The current date could be anything between 1 to 30.
    today = get_today()
    # total operation is
    # if updating_day falls within current month then n+1
    if n_days_ago < today:
        return 1 + n_days_ago
    # otherwise the next 30th date
    else:
        # based on current date, the updating target date will be
        target_day = today - n_days_ago
        return (abs(target_day) % 30) + 1


def option2_calc_select(range_days_count):
    # The current date could be anything between 1 to 30.
    today = get_today()
    # total operation is
    # if updating_day falls within current month then 2
    if range_days_count < today:
        return 2
    # otherwise for each month it touched, it needs to read 2 queries
    else:
        # based on current date, the updating target date will be
        target_day = today - range_days_count
        month_count = 1  # considering current month as well
        month_count += (abs(target_day) / 30) + 1
        return int(month_count) * 2


def create_sql_costs():
    sql_costs = []
    # Option 1
    sql_costs.append(SQLCost(
        cost_update=lambda n_days_ago: n_days_ago + 1,
        cost_select=lambda range_days_count: 2 if range_days_count > 0 else 0))
    # Option 2
    sql_costs.append(SQLCost(
        cost_update=option2_calc_update,
        cost_select=option2_calc_select))
    # Option 3
    sql_costs.append(SQLCost(
        cost_update=lambda n_days_ago: 1,
        cost_select=lambda range_days_count: range_days_count))
    return sql_costs


def test():
    sql_costs = create_sql_costs()
    set_random_day(15)

    # Option 1
    sql_costs[0].assert_update(0, 1, "Option 1")
    sql_costs[0].assert_update(1, 2, "Option 1")
    sql_costs[0].assert_update(14, 15, "Option 1")
    sql_costs[0].assert_update(15, 16, "Option 1")
    sql_costs[0].assert_update(100, 101, "Option 1")
    sql_costs[0].assert_select(0, 0, "Option 1")
    sql_costs[0].assert_select(1, 2, "Option 1")
    sql_costs[0].assert_select(14, 2, "Option 1")
    sql_costs[0].assert_select(15, 2, "Option 1")
    sql_costs[0].assert_select(100, 2, "Option 1")

    # Option 2
    sql_costs[1].assert_update(0, 1, "Option 2")
    sql_costs[1].assert_update(1, 2, "Option 2")
    sql_costs[1].assert_update(14, 15, "Option 2")
    sql_costs[1].assert_update(15, 1, "Option 2")
    sql_costs[1].assert_update(100, 26, "Option 2")
    sql_costs[1].assert_select(0, 2, "Option 2")
    sql_costs[1].assert_select(1, 2, "Option 2")
    sql_costs[1].assert_select(14, 2, "Option 2")
    sql_costs[1].assert_select(15, 4, "Option 2")
    sql_costs[1].assert_select(100, 8, "Option 2")

    # Option 3
    sql_costs[2].assert_update(0, 1, "Option 3")
    sql_costs[2].assert_update(1, 1, "Option 3")
    sql_costs[2].assert_update(14, 1, "Option 3")
    sql_costs[2].assert_update(15, 1, "Option 3")
    sql_costs[2].assert_update(100, 1, "Option 3")
    sql_costs[2].assert_select(0, 0, "Option 3")
    sql_costs[2].assert_select(1, 1, "Option 3")
    sql_costs[2].assert_select(14, 14, "Option 3")
    sql_costs[2].assert_select(15, 15, "Option 3")
    sql_costs[2].assert_select(100, 100, "Option 3")

# update_days_distribution = (percent, min_days, max_days)
# select_days_distribution = (percent, days_range)
def emulate(update_days_distribution, select_days_distribution):
    assert sum([e[0] for e in update_days_distribution]) == 100
    assert sum([e[0] for e in select_days_distribution]) == 100

    sql_costs = create_sql_costs()
    use_sample_data_percent = 100
    update_count = 4000000 * use_sample_data_percent /100 # 4M
    select_count = 20000000 * use_sample_data_percent /100 # 20M
    # init costs for each options
    update_cost = [0 for e in sql_costs]
    select_cost = [0 for e in sql_costs]
    distribution_texts = []

    # update
    for update_tuple in update_days_distribution:
        (percent, min_days, max_days) = update_tuple
        distribution_texts += ["{} % of -{} to -{} days".format(percent, min_days, max_days)]
        for _ in range(int(update_count * int(percent) / 100)):
            days = random.randint(min_days, max_days)
            set_random_day()
            for i in range(len(sql_costs)):
                update_cost[i] += sql_costs[i].cost_update(days)
    print("update_cost")
    print('\n'.join(distribution_texts))
    print('\n'.join([str(e) for e in update_cost]))

    distribution_texts = []
    for select_tuple in select_days_distribution:
        (percent, days_range) = select_tuple
        distribution_texts += ["{} % of {} last days".format(percent, days_range)]
        for _ in range(int(select_count * int(percent) / 100)):
            set_random_day()
            for i in range(len(sql_costs)):
                select_cost[i] += sql_costs[i].cost_select(days_range)
    print("select_cost")
    print('\n'.join(distribution_texts))
    print('\n'.join([str(e) for e in select_cost]))


def main():
    sql_costs = create_sql_costs()
    for i in range(1):
        set_random_day(4)
        sql_costs[1].cost_select(3 + 30 + 90)

    emulate([(90, 0, 0), (8, 1, 3), (2, 4, 30)],
            [(90, 30), (5, 90), (5, 730)])

test()
main()
