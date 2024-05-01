from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='indexofLITRevu'),

    path('login_view/', views.login_view, name='login_view'),  
    path('registration/', views.registration, name='registration_page'),
    path('logout/', views.logout_view, name='logout'),
    path('my_tickets/', views.my_tickets, name='my_tickets'),
    path('create_ticket/', views.create_ticket, name='create_ticket'),  
    path('update_ticket/<int:ticket_id>/', views.update_ticket, name='update_ticket'),
    path('delete_ticket/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    path('create_ticket_review/', views.create_ticket_review, name='create_ticket_review'),
    path('', views.ticket_review_list, name='ticket_review_list'),
    path('subscribe/', views.list_following, name='list_following'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('post_review/<int:ticket_id>/', views.post_review, name='post_review'),
    path('update_review/<int:pk>/', views.ReviewUpdateView.as_view(), name='update_review'),
    path('feed/', views.feed, name='feed'),
]
