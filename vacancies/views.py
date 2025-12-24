from django.shortcuts import render  
from django.db.models import Count, Avg
from .models import Vacancy, Skill

def index(request):
    total_vacancies = Vacancy.objects.count()

    top_skills_query = Skill.objects.annotate(
        num_vacancies=Count('vacancies')
    ).order_by('-num_vacancies')[:10]

    skill_names = [skill.name for skill in top_skills_query]
    skill_counts = [skill.num_vacancies for skill in top_skills_query]

    avg_salary_data = Vacancy.objects.aggregate(Avg('salary_from'))
    avg_salary = avg_salary_data['salary_from__avg']
    if avg_salary:
        avg_salary = round(avg_salary)
    else:
        avg_salary = 0

    remote_count = Vacancy.objects.filter(employment_mode='Удаленная работа').count()
    hybrid_count = Vacancy.objects.filter(employment_mode='Гибридный формат').count()
    office_count = Vacancy.objects.filter(employment_mode='На месте у работодателя').count()

    context = {
        'total_vacancies': total_vacancies,
        'avg_salary': avg_salary,
        'top_skills': top_skills_query, 
        
        'skill_names': skill_names,
        'skill_counts': skill_counts,
        'remote_count': remote_count,
        'hybrid_count': hybrid_count,
        'office_count': office_count,
    }
    
    return render(request, 'vacancies/index.html', context)


def vacancy_list(request):
    vacancies = Vacancy.objects.all().order_by('-published_at')

    city_filter = request.GET.get('city')
    exp_filter = request.GET.get('experience')
    format_filter = request.GET.get('format')

    if city_filter:
        vacancies = vacancies.filter(city=city_filter)
    
    if exp_filter:
        vacancies = vacancies.filter(experience=exp_filter)

    if format_filter:
        vacancies = vacancies.filter(employment_mode=format_filter)

    cities = Vacancy.objects.values_list('city', flat=True).distinct().order_by('city')

    context = {
        'vacancies': vacancies,
        'cities': cities,
    }
    
    return render(request, 'vacancies/vacancy_list.html', context)
