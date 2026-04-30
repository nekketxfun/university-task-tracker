from django.core.management.base import BaseCommand
from task_tracker.models import Department, CustomUser, ProcessTemplate, TemplateStep


class Command(BaseCommand):
    help = 'Seed database with demo data'

    def handle(self, *args, **options):
        dept, _ = Department.objects.get_or_create(
            name='Кафедра Информатики',
            defaults={'code': 'CS-01', 'head_name': 'Иванов И.И.'}
        )

        user, _ = CustomUser.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@uni.ru',
                'full_name': 'Петров П.П.',
                'department': dept,
                'is_active': True
            }
        )
        if _: user.set_password('12345678'); user.save()

        template, _ = ProcessTemplate.objects.get_or_create(
            name='Подготовка РПД',
            defaults={'department': dept, 'created_by': user, 'is_active': True}
        )

        if _:
            TemplateStep.objects.create(template=template, step_order=1, title='Сбор требований',
                                        default_deadline_days=3)
            TemplateStep.objects.create(template=template, step_order=2, title='Написание программы',
                                        default_deadline_days=10)
            TemplateStep.objects.create(template=template, step_order=3, title='Рецензирование',
                                        default_deadline_days=5)

        self.stdout.write(self.style.SUCCESS('Successfully seeded data'))