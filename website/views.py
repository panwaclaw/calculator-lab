import math
from decimal import Decimal

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


class IndexView(View):
    def get(self, request):
        return render(request, 'website/index.html')


class CalcView(View):

    MINIMUM = Decimal("-1000000000000.000000")
    MAXIMUM = Decimal("1000000000000.000000")

    def truncate(self, n):
        multiplier = Decimal(10 ** 10)
        return math.floor(n * multiplier) / multiplier

    def round_half_up(self, n, decimals=0):
        multiplier = Decimal(10 ** 10)
        return math.floor(n * multiplier + Decimal(0.5)) / multiplier

    def round_even(self, n):
        return round(n, 10)

    def process(self, a, b, op, r=True):
        result = Decimal(0)
        if op == '+':
            result = a + b
        if op == '-':
            result = a - b
        if op == '*':
            result = a * b
        if op == '/':
            if b == Decimal(0):
                return HttpResponse("Division by zero", status=500)
            result = a / b
            result = Decimal(f"{result:.6f}")

        if result < self.MINIMUM or result > self.MAXIMUM:
            return HttpResponse("Overflow", status=500)

        if r:
            string = f"{result:.10f}"
        else:
            string = f"{result}"

        if string.find('.') != -1:
            while string[-1] == '0':
                string = string[:-1]
        if string[-1] == ".":
            string = string[:-1]

        if string == "-0":
            string = "0"

        return string

    def post(self, request):
        if not request.is_ajax:
            return HttpResponse("NOT AJAX")
        if request.POST.get('a', '').find('e') != -1 or request.POST.get('b', '').find('e') != -1:
            return HttpResponse("scientific notation is not allowed", status=500)
        a = Decimal(request.POST.get('a'))
        b = Decimal(request.POST.get('b'))
        c = Decimal(request.POST.get('c'))
        d = Decimal(request.POST.get('d'))
        op1 = request.POST.get('sign1')
        op2 = request.POST.get('sign2')
        op3 = request.POST.get('sign3')
        roundtype = request.POST.get('roundtype')

        r1 = self.process(b, c, op2)
        if type(r1) == HttpResponse:
            return r1

        print(r1)

        if (op1 in ['*', '/']) or (op1 in ['+', '-'] and op3 in ['+', '-']):
            r2 = self.process(a, Decimal(r1), op1)
            if type(r2) == HttpResponse:
                return r2

            print(r2)

            r3 = self.process(Decimal(r2), d, op3, r=False)
            if type(r3) == HttpResponse:
                return r3
            string = r3
        else:
            print(r1, op3, d)
            r2 = self.process(Decimal(r1), d, op3)
            if type(r2) == HttpResponse:
                return r2

            print(r2)

            r3 = self.process(a, Decimal(r2), op1, r=False)
            if type(r3) == HttpResponse:
                return r3
            string = r3

        if roundtype == "math":
            string = f"{self.round_half_up(Decimal(string)):,}".replace(',', ' ')
        if roundtype == "half_even":
            string = f"{self.round_even(Decimal(string)):,}".replace(',', ' ')
        if roundtype == "trunc":
            string = f"{self.truncate(Decimal(string)):,}".replace(',', ' ')

        if string.find('.') != -1:
            while string[-1] == '0':
                string = string[:-1]
        if string[-1] == ".":
            string = string[:-1]

        if string == "-0":
            string = "0"

        return HttpResponse(string)
