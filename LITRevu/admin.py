from django.contrib import admin
from .models import Ticket, Review, UserFollows

admin.site.register(Ticket)

class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'description','created_at') 
    search_fields = ('title', 'description') 

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'rating', 'headline', 'user', 'time_created')
    search_fields = ('headline', 'user__username')  # Recherche par nom d'utilisateur
    list_filter = ('rating',)  # Filtre par note

# Enregistrer le modèle Review avec sa classe zd'administration personnalisée
admin.site.register(Review, ReviewAdmin)

admin.site.register(UserFollows)