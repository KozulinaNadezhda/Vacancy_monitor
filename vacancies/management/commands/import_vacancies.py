import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from vacancies.models import Vacancy, Employer, Skill
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Загрузка вакансий с HH.ru'

    def handle(self, *args, **kwargs):
        self.stdout.write("Начинаем импорт вакансий (Junior Analysts)...")

        delete_threshold = datetime.now() - timedelta(days=10)
        deleted_count, _ = Vacancy.objects.filter(published_at__lt=delete_threshold).delete()
        self.stdout.write(f"Удалено устаревших вакансий: {deleted_count}")

        base_url = "https://api.hh.ru/vacancies"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        experience_levels = ["noExperience", "between1And3"]
        
        for exp in experience_levels:
            self.stdout.write(f"--- Запрос вакансий с опытом: {exp} ---")

            date_from = (datetime.now() - timedelta(days=1)).isoformat()
            
            params = {
                "text": "Analyst OR Аналитик",
                "search_field": "name",
                "area": 113,
                "experience": exp,
                "per_page": 100,
                "order_by": "publication_time",
                "date_from": date_from, 
            }

            try:
                response = requests.get(base_url, params=params, headers=headers)
                
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"Ошибка API {response.status_code}: {response.text}"))
                    continue

                data = response.json()
                items = data.get('items', [])
                self.stdout.write(f"Найдено в поиске: {len(items)}")

                for item in items:
                    try:
                        name_lower = item['name'].lower()
                        if not ('analyst' in name_lower or 'аналитик' in name_lower):
                            continue 

                        vacancy_id = item['id']
                        detail_url = f"{base_url}/{vacancy_id}"
                        
                        detail_response = requests.get(detail_url, headers=headers)
                        if detail_response.status_code != 200:
                            continue
                            
                        full_data = detail_response.json()

                        emp_data = full_data.get('employer', {})
                        if not emp_data or 'id' not in emp_data:
                            continue

                        employer, _ = Employer.objects.get_or_create(
                            hh_employer_id=emp_data.get('id'),
                            defaults={
                                'name': emp_data.get('name'),
                                'url': emp_data.get('alternate_url')
                            }
                        )

                        salary_data = full_data.get('salary')
                        salary_from = None
                        salary_to = None
                        if salary_data:
                            salary_from = salary_data.get('from')
                            salary_to = salary_data.get('to')

                        schedule_data = full_data.get('schedule', {})
                        schedule_id = schedule_data.get('id')
                        
                        if schedule_id == 'remote':
                            final_mode = 'Удаленная работа'
                        elif schedule_id == 'flexible':
                            final_mode = 'Гибридный формат'
                        else:
                            final_mode = 'На месте у работодателя'

                        vacancy, created = Vacancy.objects.update_or_create(
                            hh_id=full_data.get('id'),
                            defaults={
                                'title': full_data.get('name'),
                                'employer': employer,
                                'salary_from': salary_from,
                                'salary_to': salary_to,
                                'city': full_data.get('area', {}).get('name', 'Unknown'),
                                'url': full_data.get('alternate_url'),
                                'published_at': parse_datetime(full_data.get('published_at')),
                                'experience': full_data.get('experience', {}).get('name', 'Не указано'),
                                'employment_mode': final_mode,
                            }
                        )

                        key_skills = full_data.get('key_skills', [])
                        for skill_obj in key_skills:
                            skill_name = skill_obj.get('name')
                            skill, _ = Skill.objects.get_or_create(name=skill_name)
                            vacancy.skills.add(skill)

                        action = "Создана" if created else "Обновлена"
                        self.stdout.write(f"{action}: {vacancy.title} ({final_mode})")

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Ошибка обработки вакансии: {e}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Общая ошибка: {e}"))

        self.stdout.write(self.style.SUCCESS('Успешно!'))