from django.contrib import admin
from .models import Employer, Skill, Vacancy

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('name', 'hh_employer_id', 'url')
    search_fields = ('name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'salary_from', 'city', 'experience', 'employment_mode', 'published_at')
    list_filter = ('experience', 'employment_mode', 'city', 'published_at')
    search_fields = ('title', 'employer__name')