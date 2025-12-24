from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название навыка")
    
    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class Employer(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название компании")
    hh_employer_id = models.CharField(max_length=50, unique=True, verbose_name="ID на HH.ru")
    url = models.URLField(blank=True, null=True, verbose_name="Ссылка на компанию")
    
    class Meta:
        verbose_name = "Работодатель"
        verbose_name_plural = "Работодатели"

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    hh_id = models.CharField(max_length=50, unique=True, verbose_name="ID вакансии на HH", default="")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='vacancies', verbose_name="Компания")
    
    salary_from = models.IntegerField(null=True, blank=True, verbose_name="Зарплата от")
    salary_to = models.IntegerField(null=True, blank=True, verbose_name="Зарплата до")
    currency = models.CharField(max_length=10, default="RUR", verbose_name="Валюта")
    
    city = models.CharField(max_length=100, verbose_name="Город")
    url = models.URLField(verbose_name="Ссылка на вакансию")
    published_at = models.DateTimeField(verbose_name="Дата публикации")
    
    experience = models.CharField(max_length=50, verbose_name="Опыт работы", default="Не указано")
    employment_mode = models.CharField(max_length=50, verbose_name="Формат работы", default="Полный день")

    skills = models.ManyToManyField(Skill, related_name='vacancies', verbose_name="Ключевые навыки")

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-published_at']

    def __str__(self):
        return f"{self.title} ({self.employer.name})"