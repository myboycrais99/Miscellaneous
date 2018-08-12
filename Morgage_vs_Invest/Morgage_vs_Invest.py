"""

"""
import numpy as np


# Equation for amortization: A = P[(r(1+r)**n)/((1+r)**n-1)],
# where A is payment amount per period, P is principle, r is interest rate per
# period expressed as a decimal, and n is number of payments.
def amortization(rate, number, principal, extra=0, extra_start=0):
    """This method calculates and returns an amortization schedule based on an
    interest rate, number of payments, and initial principal
    
    :param rate: 
        interest rate expressed as a percentage
    :param number: 
        number of payments or periods
    :param principal: 
        principal amount
    :param extra:
        extra amount to apply to principal
    :param extra_start:
        payment number to start extra payments
        
    :return: Amount
        payment amount per period
    """

    r = rate / 12 / 100
    i = np.zeros((number + 1,), dtype=float)
    p = np.zeros((number + 1,), dtype=float)
    bal = np.zeros((number + 1,), dtype=float)

    a = np.round(principal * ((r * (1 + r) ** number) /
                              ((1 + r) ** number - 1)), 2)

    pay = np.ones((number + 1,), dtype=float) * a
    pay[extra_start:] += extra

    bal[0] = principal
    for n in range(1, number):
        i[n] = np.round(bal[n - 1] * r, 2)
        p[n] = np.round(pay[n] - i[n], 2)

        bal[n] = np.round(bal[n - 1] - p[n], 2)

        # print("{:3.0f}:  $ {:7.2f}\t $ {:7.2f}\t $ {:7.2f}\t $ {:9.2f}"
        #       "".format(n, np.round(pay[n], 2), np.round(p[n], 2),
        #                 np.round(i[n], 2), np.round(bal[n], 2)))

        if bal[n] < a:
            n += 1
            i[n] = np.round(bal[n - 1] * r, 2)
            pay[n] = np.round(bal[n - 1] + i[n], 2)
            p[n] = np.round(pay[n] - i[n], 2)
            bal[n] = np.round(bal[n - 1] - p[n], 2)

            # print("{:3.0f}:  $ {:7.2f}\t $ {:7.2f}\t $ {:7.2f}\t $ {:9.2f}"
            #       "".format(n, np.round(pay[n], 2), np.round(p[n], 2),
            #                 np.round(i[n], 2), np.round(bal[n], 2)))

            break

    return a, p[1:], i[1:], bal[1:]


def invest(rate, number, principal, years, extra=0, extra_start=0):
    """
    :param rate: 
        interest rate expressed as a percentage
    :param number: 
        number of periods per year
    :param principal: 
        principal amount
    :param years:
        number of years money is invested
    :param extra:
        extra amount to apply each period
    :param extra_start:
        payment number to start extra payments
    :return: 
    """

    r = rate / 100

    a = principal
    for i in range(int(number * years)):
        a = a * (1 + r / number) + extra
    a = np.round(a, 2)

    return a


if __name__ == "__main__":
    extra = 00  # 1500 + 950 + 300
    extra_start = 20

    value, loan, rate, term = 261000, 203200, 2.75, 180
    _, _, interest, _ = amortization(rate, term, loan)
    max_interest = np.sum(interest)

    amount, principle, interest, balance = (
        amortization(rate, term, loan, extra, extra_start))

    months = len(principle[principle > 0]) - extra_start

    investments = 167500
    r, n, y, s = 10, 12, months / 12, 0
    gain = invest(r, n, investments, y, extra, s) - investments

    print("months saved:", 180 - months - extra_start)
    print("Duration [years]: ", np.round(len(principle[principle > 0]) / 12, 2))
    print("Interest Saved:\t\t\t$ {:10.2f}".format(
        max_interest - np.sum(interest)))
    print("Investment Gains:\t\t$ {:10.2f}".format(gain))
    print("Investments after\n\t15 years:\t\t\t$ {:10.2f}".format(
        invest(r, n, investments, 9, extra, s)))

    print(amount, principle[0])