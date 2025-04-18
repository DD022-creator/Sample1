from django.shortcuts import render
from django.http import JsonResponse

def financeadvisor_view(request):
    return render(request, 'financeadvisor.html')

def get_financial_advice(request):
    if request.method == 'POST':
        income = float(request.POST.get('income', 0))
        expenses = float(request.POST.get('expenses', 0))
        savings = income - expenses
        advice = "You're doing great!" if savings > 0 else "Consider reducing your expenses."
        
        return JsonResponse({
            'income': income,
            'expenses': expenses,
            'savings': savings,
            'advice': advice
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)
