from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Profile, Order
from .forms import RegistrationForm, OrderForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.http import JsonResponse


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            new_prof = Profile.objects.create(user=user)
            new_prof.btc_original = new_prof.btc_wallet
            new_prof.save()
            messages.success(request, f'Benvenuto!, {username}.')
            return redirect('login')
    else:
        messages.error(request, 'username o password errati')
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required(login_url='login')
def home(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    return render(request, 'home.html', {'profile': profile})


@login_required(login_url='login')
def create_order(request):
    x = Order()
    x = x.media_pric()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        user = request.user
        if form.is_valid():
            new_order_prof = Profile.objects.get(user=user)
            if form.instance.type == 'BUY':
                total_cash = float(form.instance.price) * float(form.instance.quantity)
                if total_cash <= new_order_prof.cash_wallet:
                    order_sell = Order.objects.filter(type='SELL').filter(active=True)\
                        .filter(price__lte=form.instance.price).filter(~Q(user=user)).order_by('price', 'date')
                    form.instance.user = user
                    form.save()
                    messages.success(request, 'creato')
                    if len(order_sell) > 0:
                        messages.success(request, 'cerca ordini')
                        for order in order_sell:
                            prof_sell = Profile.objects.get(user=order.user)
                            if order.quantity == form.instance.quantity:
                                prof_sell.btc_wallet -= order.quantity
                                prof_sell.cash_wallet += total_cash
                                new_order_prof.cash_wallet -= total_cash
                                new_order_prof.btc_wallet += order.quantity
                                form.instance.active = False
                                order.active = False
                                order.save()
                                new_order_prof.save()
                                form.save()
                                prof_sell.save()
                                messages.success(request, 'BTC acquistati')
                                return redirect('/new_order')
                            elif order.quantity < form.instance.quantity:
                                form.instance.quantity -= order.quantity
                                prof_sell.btc_wallet -= order.quantity
                                prof_sell.cash_wallet += (order.quantity * order.price)
                                new_order_prof.cash_wallet -= (order.quantity * order.price)
                                new_order_prof.btc_wallet += order.quantity
                                order.active = False
                                order.save()
                                new_order_prof.save()
                                form.save()
                                prof_sell.save()
                                messages.success(request, 'BTC acquistati parzialmente')
                                continue
                            elif order.quantity > form.instance.quantity:
                                order.quantity -= form.instance.quantity
                                prof_sell.btc_wallet -= form.instance.quantity
                                prof_sell.cash_wallet += (form.instance.quantity * order.price)
                                new_order_prof.cash_wallet -= (form.instance.quantity * order.price)
                                new_order_prof.btc_wallet += form.instance.quantity
                                form.instance.active = False
                                order.save()
                                new_order_prof.save()
                                form.save()
                                prof_sell.save()
                                messages.success(request, 'BTC acquistati')
                                return redirect('/new_order')
                        else:
                            return redirect('/new_order')
                    else:
                        messages.info(request, 'Nessuna controparte')
                        return redirect('/new_order')
                else:
                    messages.error(request, 'BTC Insufficienti!!')
                    return redirect('/new_order')
            elif form.instance.type == 'SELL':
                total_cash = float(form.instance.price) * float(form.instance.quantity)
                if new_order_prof.btc_wallet >= form.instance.quantity:
                    form.instance.user = user
                    form.save()
                    messages.success(request, 'creato')
                    order_buy = Order.objects.filter(type='BUY').filter(active=True)\
                        .filter(price__gte=form.instance.price).filter(~Q(user=user)).order_by('-price', 'date')
                    if len(order_buy) > 0:
                        messages.success(request, 'cerca ordini')
                        for order in order_buy:
                            prof_buyer = Profile.objects.get(user=order.user)
                            if order.quantity == form.instance.quantity:
                                prof_buyer.btc_wallet += order.quantity
                                prof_buyer.cash_wallet -= total_cash
                                new_order_prof.cash_wallet += total_cash
                                new_order_prof.btc_wallet -= order.quantity
                                form.instance.active = False
                                order.active = False
                                order.save()
                                new_order_prof.save()
                                form.save()
                                prof_buyer.save()
                                messages.success(request, 'BTC venduti')
                                return redirect('/new_order')
                            elif order.quantity < form.instance.quantity:
                                form.instance.quantity -= order.quantity
                                prof_buyer.btc_wallet += order.quantity
                                prof_buyer.cash_wallet -= (order.quantity * order.price)
                                new_order_prof.cash_wallet += (order.quantity * order.price)
                                new_order_prof.btc_wallet -= order.quantity
                                order.active = False
                                order.save()
                                new_order_prof.save()
                                form.save()
                                prof_buyer.save()
                                messages.success(request, 'BTC venduti parzialmente')
                                continue
                            elif order.quantity > form.instance.quantity:
                                order.quantity -= form.instance.quantity
                                prof_buyer.btc_wallet += form.instance.quantity
                                prof_buyer.cash_wallet -= (form.instance.quantity * order.price)
                                new_order_prof.cash_wallet += (form.instance.quantity * order.price)
                                new_order_prof.btc_wallet -= form.instance.quantity
                                form.instance.active = False
                                order.save()
                                new_order_prof.save()
                                form.save()
                                prof_buyer.save()
                                messages.success(request, 'BTC venduti')
                                return redirect('/new_order')
                        else:
                            return redirect('/new_order')
                    else:
                        messages.info(request, 'Nessuna controparte')
                        return redirect('/new_order')
                else:
                    messages.error(request, 'BTC Insufficienti!')
                    return redirect('/new_order')
        else:
            messages.error(request, "Inserisci quantita' o prezzo corretti!")
            return redirect('/new_order')
    else:
        form = OrderForm()
        messages.info(request, f"prezzo medio buy: {x[0]}")
        messages.info(request, f"prezzo medio sell: {x[1]}")
        return render(request, 'new_order.html', {'form': form})


class AllOrder(ListView):
    model = Order
    template_name = 'all_order.html'
    context_object_name = 'orders'


def profit(request):
    lis = []
    profiles = Profile.objects.all()
    user = request.user
    if user.is_staff:
        for prof in profiles:
            profitt = float(prof.btc_wallet) - float(prof.btc_original)
            lis.append(
                {
                    'User': f"{prof.user}",
                    'BTC Profit': profitt,
                    'Cash Profit': prof.cash_wallet - 100000
                }
            )
        return JsonResponse(lis, safe=False)
    else:
        lis.append(
            'NON SEI AUTORIZZATO'
        )
        return JsonResponse(lis, safe=False)

