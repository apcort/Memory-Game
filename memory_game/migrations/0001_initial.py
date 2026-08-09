import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Partida',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nivel', models.CharField(choices=[('basico', 'Básico'), ('medio', 'Medio'), ('avanzado', 'Avanzado')], max_length=10)),
                ('resultado', models.CharField(choices=[('victoria', 'Victoria'), ('derrota', 'Derrota')], max_length=10)),
                ('intentos_permitidos', models.PositiveSmallIntegerField()),
                ('intentos_usados', models.PositiveSmallIntegerField()),
                ('tiempo_limite', models.PositiveSmallIntegerField(help_text='Segundos disponibles para la partida')),
                ('tiempo_usado', models.FloatField(help_text='Segundos que tardó el jugador')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partidas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Partida',
                'verbose_name_plural': 'Partidas',
                'ordering': ['-fecha'],
            },
        ),
    ]
