from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse
from .forms import TicketForm, ReviewForm, SearchForm
from .models import Ticket, Review, UserFollows
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from django.contrib import messages
from itertools import chain


@login_required
def index(request):
    context = {"message": "Hello world!"}
    if request.user.is_authenticated:
        ticket_form = TicketForm()
        context['ticket_form'] = ticket_form
        user = request.user
        following_users = user.following.all()

        # Récupérer les tickets créés par l'utilisateur connecté
        tickets = Ticket.objects.filter(user=user)
        context['tickets'] = tickets

        context['following_users'] = following_users
    return render(request, "LITRevu/index.html", context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # After successful login, redirect the user
                return redirect('ticket_review_list')
    else:
        form = AuthenticationForm()
    return render(request, 'LITRevu/login.html', {'form': form})


def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # After registration, you can choose where to redirect the user
            return redirect('ticket_review_list')
    else:
        form = UserCreationForm()
    return render(request, 'LITRevu/registration.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('ticket_review_list')


@login_required
def create_ticket(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('my_tickets')
    else:
        ticket_form = TicketForm()
    return render(request, 'LITRevu/create_ticket.html', {'ticket_form': ticket_form})


@login_required
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('my_tickets')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'LITRevu/update_ticket.html', {'form': form, 'ticket': ticket})

@login_required
def post_review(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect('ticket_review_list')
    else:
        form = ReviewForm()
    return render(request, 'LITRevu/post_review.html', {'form': form, 'ticket': ticket})


class ReviewUpdateView(UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'LITRevu/update_review.html'
    success_url = '/'


@login_required
def create_ticket_review(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect('my_tickets')
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()
    return render(request, 'LITRevu/create_ticket_review.html', {'ticket_form': ticket_form, 'review_form': review_form})


@login_required
def list_following(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            # Perform a search query to find users matching the query
            users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    else:
        form = SearchForm()
        users = User.objects.exclude(id=request.user.id)

    following = request.user.following.values_list('followed_user__id', flat=True)
    return render(request, 'LITRevu/list_following.html', {'form': form, 'users': users, 'following': following})

@login_required
def follow_user(request, user_id):
    user_to_follow = User.objects.get(pk=user_id)
    if not request.user.following.filter(followed_user=user_to_follow).exists():
        follow_instance = UserFollows(user=request.user, followed_user=user_to_follow)
        follow_instance.save()
    return redirect('list_following')

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = User.objects.get(pk=user_id)
    follow_instance = request.user.following.filter(followed_user=user_to_unfollow)
    if follow_instance.exists():
        follow_instance.delete()
    return redirect('list_following')


@login_required
def ticket_review_list(request):
    user = request.user
    tickets = Ticket.objects.filter(user=user)
    reviews = Review.objects.filter(user=user)
    following_users = UserFollows.objects.filter(user=user).values_list('followed_user', flat=True)
    following_tickets = Ticket.objects.filter(user__in=following_users)
    following_reviews = Review.objects.filter(user__in=following_users)
    replied_tickets = Ticket.objects.filter(review__user=user)

    combined_list = [
        {'item': ticket, 'type': 'Ticket'} for ticket in (tickets | following_tickets | replied_tickets)
    ] + [
        {'item': review, 'type': 'Review'} for review in (reviews | following_reviews)
    ]

    # Check if each ticket has been reviewed by the logged-in user
    for item in combined_list:
        if item['type'] == 'Ticket':
            item['item'].user_reviewed = Review.objects.filter(ticket=item['item'], user=user).exists()

    combined_list.sort(key=lambda x: x['item'].time_created if x['type'] == 'Review' else x['item'].created_at, reverse=True)

    return render(request, 'LITRevu/ticket_review_list.html', {'combined_list': combined_list})


@login_required
def my_tickets(request):
    user = request.user
    tickets = Ticket.objects.filter(user=user)
    ticket_reviews = {}
    for ticket in tickets:
        reviews = Review.objects.filter(ticket=ticket)
        ticket_reviews[ticket] = reviews

    return render(request, 'LITRevu/my_tickets.html', {'ticket_reviews': ticket_reviews})

@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    # Check if the user is authorized to delete the ticket
    if request.user == ticket.user:
        ticket.delete()
    # Redirect to the my_tickets view after deletion
    return redirect('my_tickets')

from django.db.models import Value, CharField

@login_required
def feed(request):
    # Fetch tickets and reviews for the logged-in user
    user = request.user
    tickets = Ticket.objects.filter(user=user)
    reviews = Review.objects.filter(user=user)

    # Annotate tickets and reviews with content type indicators
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    # Combine tickets and reviews into a single list
    posts = sorted(chain(tickets, reviews), key=lambda post: post.time_created if hasattr(post, 'time_created') else post.created_at, reverse=True)

    # Render the template with the combined list
    return render(request, 'LITRevu/flow.html', context={'posts': posts})