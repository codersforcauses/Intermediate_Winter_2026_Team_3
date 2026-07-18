from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("games", "0002_playerachievement_playtimesnapshot_usergame_and_more")]
    operations = [
        migrations.AddField(
            model_name="achievement",
            name="global_percent",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
