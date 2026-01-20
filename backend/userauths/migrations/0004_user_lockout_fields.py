from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userauths", "0003_user_reset_token_alter_user_otp"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="failed_login_attempts",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="is_locked",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="locked_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
