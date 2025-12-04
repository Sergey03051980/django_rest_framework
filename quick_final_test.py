import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
import django
django.setup()

from materials.models import Course
import time

print("🔥 БЫСТРЫЙ ТЕСТ С МЕТОДОМ SAVE()")
print("="*50)

course = Course.objects.first()
if course:
    print(f"Курс: {course.title}")
    
    # Обновляем 3 раза
    for i in range(1, 4):
        print(f"\n📝 Обновление #{i}...")
        course.description = f"Обновление #{i} в {time.strftime('%H:%M:%S')}"
        course.save()
        print(f"✅ Обновление #{i} сохранено")
        time.sleep(1)  # Пауза между обновлениями
    
    print("\n🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
    print("🔍 Проверьте Celery - должно быть 3 задачи")
else:
    print("❌ Нет курсов")

print("="*50)
